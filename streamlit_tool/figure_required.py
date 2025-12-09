import datetime
from datetime import datetime, timedelta, timezone

import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import psycopg

def figure_required_reddit_posts_only():
    data_labels = ["reddit-post"]

    startDate = datetime(2025, 10, 22)
    dates = [startDate + timedelta(days=i) for i in range(41)]

    data = [[0 for _ in range(41)] for _ in range(4)]

    query = """
        SELECT
            DATE_TRUNC('day', created_time) AS day,
            platform,
            COUNT(*) AS post_count
        FROM posts
        GROUP BY day, platform
        ORDER BY day;
    """

    cur.execute(query)
    rows = cur.fetchall()

    for day, platform, count in rows:
        day_only = day.date()

        for i, d in enumerate(dates):
            if d.date() == day_only:
                # if platform == "bluesky":
                #     data[0][i] = count
                # elif platform == "reddit-comment":
                #     data[1][i] = count
                if platform == "reddit-post":
                    data[0][i] = count
                # elif platform == "youtube":
                #     data[3][i] = count
                break

    fig = plt.figure(figsize=(12, 6))

    for idx, label in enumerate(data_labels):
        plt.plot(dates, data[idx], label=label)

    plt.gca().xaxis.set_major_locator(mdates.DayLocator()) 
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d')) 

    plt.title('Posts Per Platform Over Time')
    plt.xlabel('Day',fontsize=24)
    plt.ylabel('Number of Posts',fontsize=20)
    plt.legend(title='Platform')
    plt.xticks(rotation=45) 
    plt.tight_layout()
    plt.show()

    st.pyplot(fig)

with psycopg.connect("dbname=project1 user=postgres password=postgres") as conn:
    # print("test")
    with conn.cursor() as cur:
        plt.rcParams.update({'font.size': 14})
        data_labels = ["bluesky", "reddit-comments", "reddit-post", "youtube"]

        startDate = datetime(2025, 10, 22)
        dates = [startDate + timedelta(days=i) for i in range(41)]

        data = [[0 for _ in range(41)] for _ in range(4)]

        query = """
            SELECT
                DATE_TRUNC('day', created_time) AS day,
                platform,
                COUNT(*) AS post_count
            FROM posts
            GROUP BY day, platform
            ORDER BY day;
        """

        cur.execute(query)
        rows = cur.fetchall()

        for day, platform, count in rows:
            day_only = day.date()

            for i, d in enumerate(dates):
                if d.date() == day_only:

                    if platform == "bluesky":
                        data[0][i] = count
                    elif platform == "reddit-comment":
                        data[1][i] = count
                    elif platform == "reddit-post":
                        data[2][i] = count
                    elif platform == "youtube":
                        data[3][i] = count
                    break

        fig = plt.figure(figsize=(12, 6))

        for idx, label in enumerate(data_labels):
            plt.plot(dates, data[idx], label=label)

        plt.gca().xaxis.set_major_locator(mdates.DayLocator()) 
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d')) 

        plt.title('Posts Per Platform Over Time',fontsize=20)
        plt.xlabel('Day',fontsize=24)
        plt.ylabel('Number of Posts',fontsize=20)
        plt.legend(title='Platform')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        st.pyplot(fig)
        figure_required_reddit_posts_only()