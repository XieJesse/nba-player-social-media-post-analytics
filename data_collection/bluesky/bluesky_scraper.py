import os 
import requests
import psycopg
import re
from textblob import TextBlob
import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from atproto import Client
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

client = Client()
client.login(os.getenv("BLUESKY_USERNAME"), os.getenv("BLUESKY_PASSWORD"));
now = datetime.now(timezone.utc)
one_day_ago = now - timedelta(days=1)
iso_time_str = one_day_ago.isoformat().replace("+00:00", "Z")

seen = set()
with psycopg.connect("dbname=project1 user=postgres password=postgres") as conn:
    # print("test")
    with conn.cursor() as cur:
        with open("../players.txt", 'r') as file_object:
            index = 0
            
            for line in file_object:
                index += 1
                player_names = line.split(",")
                    # print(name)
                    # print("a")
                params = {
                    "q": player_names[0].replace('\n', ''),
                    "limit": 100,
                    "since": iso_time_str
                }

                resps = client.app.bsky.feed.search_posts(
                    params=params
                )

                resps_dict = resps.model_dump()
                posts = resps_dict['posts']

                for post in posts:
                    uri = post["uri"]    
                    uri = uri.replace("at://", "")
                    did, rest = uri.split("/", 1)
                    post_id = rest.split("/")[-1]
                    web_url = f"https://bsky.app/profile/{did}/post/{post_id}"
                    player_polarity = {}
 
                    post_content = post["record"]["text"]

                    # print(json.dumps(post, indent=4))

                    comment_data = {
                        "author_did": post.get("author", {}).get("did"),
                        "author_avatar": post.get("author", {}).get("avatar"),
                        "author_display_name": post.get("author", {}).get("display_name"),
                        "tags": post.get("record", {}).get("tags"),
                        "like_count": post.get("like_count", 0),
                        "quote_count": post.get("quote_count", 0),
                        "reply_count": post.get("reply_count", 0),
                        "repost_count": post.get("repost_count", 0),
                        "bookmark_count": post.get("bookmarkCount", 0),
                    }

                    # print(comment_data)
                    if not post or "record" not in post:
                        continue 
                    if "created_at" in post["record"]:
                        post_created_at = post["record"]["created_at"]
                    elif "createdAt" in post["record"]:
                        post_created_at = post["record"]["createdAt"]
                    else:
                        post_created_at = datetime.now()
                    
                    if (post_content[0:15]) in seen:
                        continue 
                    seen.add(post_content[0:15])

                    post_content = post_content.replace('\n', ' ')

                    blob = TextBlob(post_content)
                    polarity = blob.sentiment.polarity

                    if index not in player_polarity:
                        player_polarity[index] = (polarity,1)

                    player_polarity[index] = (player_polarity[index][0]+polarity,player_polarity[index][1]+1)

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
                    
                    dt = datetime.fromisoformat(post_created_at.replace("Z", "+00:00"))
                    
                    post_title = post_content[0:50]
                    cur.execute(add_to_posts_table,(post_title[0:50],"bluesky",post_content[0:500], web_url[0:100], dt, json.dumps(comment_data),0.0))
                    
                    new_post_id = cur.fetchone()[0]
                    # print(len(player_polarity.items()))
                    for i, pp in player_polarity.items():

                        average_polarity = pp[0] / pp[1]
                        update_players_table = """
                        UPDATE players
                        SET
                            total_sentiment_score = total_sentiment_score + %s,
                            num_posts = num_posts + %s
                        WHERE id = %s;
                        """
                        cur.execute(update_players_table,(average_polarity,1,i))

                        add_to_player_posts_table = """
                        INSERT INTO player_posts (player_id, post_id, sentiment_score) VALUES (%s, %s, %s) ;
                        """
                        cur.execute(add_to_player_posts_table,(i,new_post_id,average_polarity))

            conn.commit()