import os 
import json
from textblob import TextBlob
import re
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import json

import psycopg

load_dotenv()

youtube_api_key = os.getenv("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=youtube_api_key)

request = youtube.channels().list(
        part="contentDetails,id,localizations,snippet,statistics,status,topicDetails",
        forHandle="NBA"
    )
response = request.execute()
upload_playlists_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

results = 150
curr_results = 0
playlist_responses = []
playlist_next_page_token = None

while curr_results < results:
    playlist_response = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=upload_playlists_id,
        maxResults=50,
        pageToken=playlist_next_page_token
    ).execute()

    playlist_responses.append(playlist_response)
    curr_results += len(playlist_response)

    if (playlist_response.get("nextPageToken")):
        playlist_next_page_token = playlist_response.get("nextPageToken")

now = datetime.now(timezone.utc)
end_time = now - timedelta(hours=24)
start_time = now - timedelta(hours=48)

print(len(playlist_responses))

"""
"items" : {"contentDetails" : {"videoid"} : wfv1_1t9ZaE }
"items" : {"contentDetails" : {"videoPublishedAt"} : 2025-10-16T02:36:37Z}
"""

videos = []
for playlist_r in playlist_responses:
    for video in playlist_r["items"]:
        # print(video)
        # print(json.dumps(video, indent=4))
        # print(video["contentDetails"]["videoId"])
        # print(video["contentDetails"]["videoPublishedAt"])
        video_id = video["contentDetails"]["videoId"]
        video_published_at = video["contentDetails"]["videoPublishedAt"]

        # need to compare with iso format
        video_published_at = datetime.fromisoformat(video_published_at.replace("Z", "+00:00"))
        if (start_time <= video_published_at <= end_time):
            videos.append(video_id)
        # elif (video_published_at < end_time):
        #     # everything else after it too prob wont fall in the range if data 
        #     # is returned in sorted order
        #     break

print(videos)
# print(len(videos))

next_page_token = None

# videos = [videos[0]]
# return
with psycopg.connect("dbname=project1 user=postgres password=postgres") as conn:
            with conn.cursor() as cur:
                for video_id in videos:

                    request_video = youtube.videos().list(
                            part="snippet,statistics,contentDetails,status",
                            id=video_id,
                            maxResults=25,
                        )
                    response_video = request_video.execute()
                    print(response_video["items"][0]["snippet"]["title"])
                    video_title = response_video["items"][0]["snippet"]["title"][0:50]
                    
                    video_description = response_video["items"][0]["snippet"]["description"]
                    video_url = "https://www.youtube.com/watch?v=" + video_id
                    default_player_id = None

                    with open("../players.txt", 'r') as file_object:
                        index = 0
                        
                        for line in file_object:
                            index += 1
                            player_names = line.split(",")
                            if not default_player_id:
                                for name in player_names:
                                    # print(name)
                                    # print("a")
                                    if name.replace('\n', '').lower() in video_title.lower() or name.replace('\n', '').lower() in video_description.lower():
                                        default_player_id = index
                                        break
                                            
                    while True:
                        request = youtube.commentThreads().list(
                            part="id,replies,snippet",
                            videoId=video_id,
                            maxResults=100,
                            pageToken = next_page_token
                        )
                        response = request.execute()
                        next_page_token = response.get("nextPageToken")
                        # print(next_page_token)

                        comments_thread = response["items"]
                        comments = []
                        for comment in comments_thread:
                            comment_text = comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"].replace('\n', ' ')
                            comment_published_str = comment["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
                            comment_published_dt = datetime.fromisoformat(comment_published_str.replace("Z", "+00:00"))
                            # print(json.dumps(comment, indent=4))

                            comment_data = {
                                "id": comment.get("id"),
                                "videoId": comment.get("snippet", {}).get("videoId"),
                                "channelId": comment.get("snippet", {}).get("channelId"),
                                "authorDisplayName": comment.get("snippet", {}).get("topLevelComment", {}).get("snippet", {}).get("authorDisplayName"),
                                "authorProfileImageUrl": comment.get("snippet", {}).get("topLevelComment", {}).get("snippet", {}).get("authorProfileImageUrl"),
                                "likeCount": comment.get("snippet", {}).get("topLevelComment", {}).get("snippet", {}).get("likeCount", 0),
                                "totalReplyCount": comment.get("snippet", {}).get("totalReplyCount", 0)
                            }

                            # print(comment_data)
                            # break
                            
                            # print(comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"])
                        # print(json.dumps(response["items"], indent = 4))
                        
                            # print(comment_text)
                            player_polarity = {}
                            
                            sentences = re.split(r'(?<=[.!?]) +', comment_text)
                            # print(sentences)
                            player_id = default_player_id

                            add = False
                            for sentence in sentences:

                                blob = TextBlob(sentence)
                                polarity = blob.sentiment.polarity
                                found = False
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
                                                found = True
                                                # print("hit")
                                                if index not in player_polarity:
                                                    player_polarity[index] = (polarity,1)

                                                player_polarity[index] = (player_polarity[index][0]+polarity,player_polarity[index][1]+1)
                                    if not found and default_player_id:
                                        index = default_player_id
                                        if index not in player_polarity:
                                                player_polarity[index] = (polarity,1)

                                        player_polarity[index] = (player_polarity[index][0]+polarity,player_polarity[index][1]+1)

                                    # print(index, video_id, comment_text)

                            # if not (add or default_player_id) or not comment_text:
                            #     continue
                            if add or default_player_id:
                                # print(video_title)
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
                              
                                cur.execute(add_to_posts_table,(video_title,"youtube",comment_text[0:500], video_url[0:50], comment_published_dt,json.dumps(comment_data),0.0 ))
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

                        if (not next_page_token):
                            break