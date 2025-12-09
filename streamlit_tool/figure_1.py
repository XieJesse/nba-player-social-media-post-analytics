import datetime
from datetime import datetime, timedelta, timezone

import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import psycopg

with psycopg.connect("dbname=project1 user=postgres password=postgres") as conn:
    # print("test")
    with conn.cursor() as cur:
        plt.rcParams.update({'font.size': 14})

        dates = []
        reddit_scores = []
        youtube_scores = []
        bluesky_scores = []
        
        curDate = datetime(2025, 10, 22) 
        for i in range(41):
            print(i)
            toxicity_scores = [0,0,0]
            num_reddit = 0
            num_youtube = 0
            num_bluesky = 0
            dates.append(curDate)
            get_posts_in_date_range_query = """
                SELECT id, platform, toxicity_score
                FROM posts
                WHERE created_time >= %s AND created_time <= %s;
            """
            cur.execute(get_posts_in_date_range_query,(curDate,curDate+timedelta(hours=24)))
            posts = cur.fetchall()

            for post in posts:
                id = post[0]
                platform = post[1]
                toxicity_score = post[2]
                if (platform == "reddit-comment" or platform == "reddit-posts"):
                    toxicity_scores[0] += toxicity_score
                    num_reddit += 1
                elif (platform == "youtube"):
                    toxicity_scores[1] += toxicity_score
                    num_youtube += 1
                elif (platform == "bluesky"):
                    toxicity_scores[2] += toxicity_score
                    num_bluesky += 1

            reddit_scores.append(toxicity_scores[0] / num_reddit)
            youtube_scores.append(toxicity_scores[1] / num_youtube)
            bluesky_scores.append(toxicity_scores[2] / num_bluesky)

            curDate = curDate + timedelta(hours=24)

        fig = plt.figure(figsize=(12, 6))
        plt.plot(dates, reddit_scores, label='Reddit', color='orange', marker='o')
        plt.plot(dates, youtube_scores, label='YouTube', color='red', marker='s')
        plt.plot(dates, bluesky_scores, label='BlueSky', color='blue', linestyle='--')

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())  
        plt.gcf().autofmt_xdate()  

        
        plt.xlabel('Date',fontsize=24)
        plt.ylabel('Average Toxicity Score',fontsize=20)
        plt.title('Average Toxicity Score Over Time',fontsize=20)
        plt.legend()
        # plt.legend(handles=[reddit_scores, youtube_scores, bluesky_scores], labels=['Reddit', 'Youtube', 'Bluesky'])
        plt.grid(True)
        # print(reddit_scores)
        # print(youtube_scores)
        # print(bluesky_scores)

        plt.show()
        st.pyplot(fig)