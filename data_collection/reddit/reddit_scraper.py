import praw
import os 
import psycopg
import re
from textblob import TextBlob
import datetime
import json

from dotenv import load_dotenv

load_dotenv()

reddit = praw.Reddit(client_id=os.getenv("REDDIT_CLIENT_ID"),
                     client_secret=os.getenv("REDDIT_API_KEY"),
                     user_agent="python:cs415-project-1:v.0.1")

subreddit = reddit.subreddit("nba")



with psycopg.connect("dbname=project1 user=postgres password=postgres") as conn:
    # print("test")
    with conn.cursor() as cur:
        print("test")
        results = list(subreddit.top(time_filter="day", limit=None))
        # accounts for issue where subreddit.top returns nothing
        for i in range(100):
            found_items = False
            for item in results:
                found_items = True
                # print(item.title)
                print("found")
                break 
            if found_items:
                break
            else:
                # print("a")
                results = list(subreddit.top(time_filter="day", limit=None))
        # print(len(results))
        for submission in results:

            #parse comments of post
            submission.comments.replace_more(limit=0)
            commentsList = submission.comments.list()
            for comment in commentsList:
                add = False
                player_polarity = {}
                sentences = re.split(r'(?<=[.!?]) +', comment.body.replace('\n', ' '))

                for sentence in sentences:
                # print(sentence)
                    blob = TextBlob(sentence)
                    polarity = blob.sentiment.polarity
                    with open("../players.txt", 'r') as file_object:
                        index = 0
                        
                        for line in file_object:
                            index += 1
                            player_names = line.split(",")
                            for name in player_names:
                                # print(name)
                                # print("a")
                                if name.replace('\n', '').lower() in sentence.lower():
                                    # print(player_names[0],sentence)
                                    add = True
                                    # print("hit")
                                    if index not in player_polarity:
                                        player_polarity[index] = (polarity,1)

                                    else:
                                        player_polarity[index] = (player_polarity[index][0]+polarity,player_polarity[index][1]+1)
                                    break

                if not add:
                    continue
                # print(submission.title)
                add_to_posts_table = """
                INSERT INTO posts (
                    title,
                    platform,
                    content,
                    url,
                    created_time,
                    json,
                    toxicity_score
                ) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id;
                """
                # print(submission.created_utc)
                dt = datetime.datetime.fromtimestamp(comment.created_utc)
                comment_data = {
                    "id": comment.id,
                    "author": str(comment.author) if comment.author else None,
                    "body": comment.body,
                    "body_html": comment.body_html,
                    "created_utc": comment.created_utc,
                    "distinguished": comment.distinguished,
                    "edited": comment.edited,
                    "is_submitter": comment.is_submitter,
                    "link_id": comment.link_id,
                    "parent_id": comment.parent_id,
                    "permalink": comment.permalink,
                    "saved": comment.saved,
                    "score": comment.score,
                    "stickied": comment.stickied,
                    "submission_id": comment.submission.id,
                    "submission_title": comment.submission.title,
                    "subreddit": str(comment.subreddit),
                    "subreddit_id": comment.subreddit_id
                }
                cur.execute(add_to_posts_table,(submission.title[0:50],"reddit-comment",comment.body.replace('\n', ' ')[0:500], comment.permalink[0:50], dt,json.dumps(comment_data),0.0) )
                new_post_id = cur.fetchone()[0]

                for index, pp in player_polarity.items():

                    average_polarity = pp[0] / pp[1]
                    update_players_table = """
                    UPDATE players
                    SET
                        total_sentiment_score = total_sentiment_score + %s,
                        num_posts = num_posts + %s
                    WHERE id = %s;
                    """
                    cur.execute(update_players_table,(average_polarity,1,index))

                    add_to_player_posts_table = """
                    INSERT INTO player_posts (player_id, post_id, sentiment_score) VALUES (%s, %s, %s) ;
                    """

                    cur.execute(add_to_player_posts_table,(index,new_post_id,average_polarity))


            #parse content of post
            add = False
            if (submission.link_flair_text == "Post Game Thread"):
                # print("skip")
                continue
            #store player id, (total polarity, num_sentences)
            player_polarity = {}
            sentences_title = re.split(r'(?<=[.!?]) +', submission.title)
            sentences_text = re.split(r'(?<=[.!?]) +', submission.selftext.replace('\n', ' '))

            sentences = sentences_title + sentences_text
            for sentence in sentences:
                # print(sentence)
                blob = TextBlob(sentence)
                polarity = blob.sentiment.polarity
                with open("../players.txt", 'r') as file_object:
                    index = 0
                    
                    for line in file_object:
                        index += 1
                        player_names = line.split(",")
                        for name in player_names:
                            # print(name)
                            # print("a")
                            if name.replace('\n', '').lower() in sentence.lower():
                                # print(player_names[0],sentence)
                                add = True
                                # print("hit")
                                if index not in player_polarity:
                                    player_polarity[index] = (polarity,1)

                                else:
                                    player_polarity[index] = (player_polarity[index][0]+polarity,player_polarity[index][1]+1)
                                break

            if not add:
                continue
            # print(submission.title)

            add_to_posts_table = """
            INSERT INTO posts (
                title,
                platform,
                content,
                url,
                created_time,
                json,
                toxicity_score
            ) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id;
            """
            # print(submission.created_utc)
            dt = datetime.datetime.fromtimestamp(submission.created_utc)
            submission_data = {
                "id": submission.id,
                "name": submission.name,
                "title": submission.title,
                "author": str(submission.author) if submission.author else None,
                "author_flair_text": submission.author_flair_text,
                "selftext": submission.selftext,
                "created_utc": submission.created_utc,
                "score": submission.score,
                "num_comments": submission.num_comments,
                "upvote_ratio": submission.upvote_ratio,
                "permalink": submission.permalink,
                "url": submission.url,
                "distinguished": submission.distinguished,
                "edited": submission.edited,
                "is_original_content": submission.is_original_content,
                "is_self": submission.is_self,
                "link_flair_text": submission.link_flair_text,
                "locked": submission.locked,
                "over_18": submission.over_18,
                "spoiler": submission.spoiler,
                "stickied": submission.stickied,
                "saved": submission.saved,
                "subreddit": str(submission.subreddit),
                "subreddit_id": submission.subreddit_id,
                "poll_data": str(submission.poll_data) if hasattr(submission, "poll_data") else None,
            }
            cur.execute(add_to_posts_table,(submission.title[0:50],"reddit-post",submission.selftext.replace('\n', ' ')[0:500], submission.url[0:50], dt,json.dumps(submission_data),0.0) )
            new_post_id = cur.fetchone()[0]

            for index, pp in player_polarity.items():

                average_polarity = pp[0] / pp[1]
                update_players_table = """
                UPDATE players
                SET
                    total_sentiment_score = total_sentiment_score + %s,
                    num_posts = num_posts + %s
                WHERE id = %s;
                """
                cur.execute(update_players_table,(average_polarity,1,index))

                add_to_player_posts_table = """
                INSERT INTO player_posts (player_id, post_id, sentiment_score) VALUES (%s, %s, %s) ;
                """

                cur.execute(add_to_player_posts_table,(index,new_post_id,average_polarity))

        conn.commit()