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
        # \item Post Sentiment Over Time (line graph)
        #     \item X Axis: Date
        #     \item Y Axis: Average Sentiment Score
        #     \item Legend: Reddit (Posts, Comments), YouTube, BlueSky
        get_posts_in_date_range_query = """
            SELECT 
                p.name AS player_name,
                DATE(po.created_time) AS day,
                SUM(pp.sentiment_score) AS total_sentiment
            FROM 
                player_posts pp
            JOIN 
                posts po ON pp.post_id = po.id
            JOIN
                players p ON pp.player_id = p.id
            WHERE 
                po.created_time BETWEEN '2025-10-22' AND '2025-12-2'
            GROUP BY 
                p.name, DATE(po.created_time)
            ORDER BY
                p.name, day;
        """

        rows = []
        cur.execute(get_posts_in_date_range_query)
        posts = cur.fetchall()
        for post in posts:
            name, date, score = post
            rows.append({
                "player": name, 
                "date": date,
                "sentiment": score,
            })
        
        df = pd.DataFrame(rows)
        df["date"] = pd.to_datetime(df["date"])

        players = df["player"].unique()
        selected_players = st.multiselect(
            "Selected player:",
            players,
            default=["Victor Wembanyama"]   
        )

        filtered_df = df[df["player"].isin(selected_players)]

        fig = px.line(
            filtered_df,
            x="date",
            y="sentiment",
            color="player",
            markers=True,
            title="Sentiment Score Over Time Per Player"
        )
        fig.update_xaxes(dtick="D1")


        st.plotly_chart(fig)