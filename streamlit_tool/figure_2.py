import datetime
from datetime import datetime, timedelta, timezone

import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import psycopg

with psycopg.connect(
    host=st.secrets["postgres"]["host"],
    port=st.secrets["postgres"]["port"],
    dbname=st.secrets["postgres"]["dbname"],
    user=st.secrets["postgres"]["user"],
    password=st.secrets["postgres"]["password"],
) as conn:
    # print("test")
    with conn.cursor() as cur:
        plt.rcParams.update({'font.size': 14})
        start_date = datetime(2025, 10, 22)
        end_date = start_date + timedelta(days=41)

        query = """
            SELECT 
                DATE(p.created_time) AS day,
                p.platform,
                AVG(pp.sentiment_score) AS avg_sentiment
            FROM posts p
            JOIN player_posts pp
                ON p.id = pp.post_id
            WHERE p.created_time BETWEEN %s AND %s
            GROUP BY DATE(p.created_time), p.platform
            ORDER BY day, platform;
        """

        cur.execute(query, (start_date, end_date))
        rows = cur.fetchall()

        data = {}
        for day, platform, avg in rows:
            data.setdefault(day, {})
            data[day][platform] = avg

        dates = []
        reddit_scores = []
        youtube_scores = []
        bluesky_scores = []

        current = start_date
        for _ in range(41):
            d = current.date()
            dates.append(current)

            reddit_scores.append(
                data.get(d, {}).get("reddit-posts")
                or data.get(d, {}).get("reddit-comment")
            )
            youtube_scores.append(data.get(d, {}).get("youtube"))
            bluesky_scores.append(data.get(d, {}).get("bluesky"))

            current += timedelta(days=1)
            
        fig = plt.figure(figsize=(12, 6))
        plt.plot(dates, reddit_scores, label='Reddit', color='orange', marker='o')
        plt.plot(dates, youtube_scores, label='YouTube', color='red', marker='s')
        plt.plot(dates, bluesky_scores, label='BlueSky', color='blue', linestyle='--')

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())  
        plt.gcf().autofmt_xdate()  

        
        plt.xlabel('Date',fontsize=24)
        plt.ylabel('Average Sentiment Score',fontsize=20)
        plt.title('Post Sentiment Over Time',fontsize=20)
        plt.legend()
        # plt.legend(handles=[reddit_scores, youtube_scores, bluesky_scores], labels=['Reddit', 'Youtube', 'Bluesky'])
        plt.grid(True)
        print(reddit_scores)
        print(youtube_scores)
        print(bluesky_scores)
        
        plt.show()
        st.pyplot(fig)