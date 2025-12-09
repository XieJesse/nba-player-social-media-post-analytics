import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import psycopg

espn_df = pd.read_csv("espn_rankings.csv")
espn_df["date"] = pd.to_datetime(espn_df["date"])

with psycopg.connect("dbname=project1 user=postgres password=postgres") as conn:
    with conn.cursor() as cur:
        get_posts_in_date_range_query = """
            WITH daily_totals AS (
                SELECT 
                    p.name AS player_name,
                    DATE(po.created_time) AS day,
                    SUM(pp.sentiment_score) AS daily_sentiment
                FROM 
                    player_posts pp
                JOIN 
                    posts po ON pp.post_id = po.id
                JOIN
                    players p ON pp.player_id = p.id
                WHERE 
                    po.created_time BETWEEN '2025-10-28' AND '2025-12-3'
                GROUP BY 
                    p.name, DATE(po.created_time)
            ),
            cumulative AS (
                SELECT
                    player_name,
                    day,
                    SUM(daily_sentiment) OVER (
                        PARTITION BY player_name
                        ORDER BY day
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    ) AS cumulative_sentiment
                FROM daily_totals
            )
            SELECT *
            FROM cumulative
            ORDER BY day, cumulative_sentiment DESC;
        """

        rows = []
        cur.execute(get_posts_in_date_range_query)
        posts = cur.fetchall()
        for post in posts:
            name, day, score = post
            rows.append({
                "player": name, 
                "date": day,
                "sentiment": score,
            })
        
        df = pd.DataFrame(rows, columns=["player", "date", "sentiment"])
        df["date"] = pd.to_datetime(df["date"])

        min_day = df["date"].min().date()
        max_day = df["date"].max().date()

        selected_day = st.slider(
            "Select a day:",
            min_value=min_day,
            max_value=max_day,
            value=min_day, 
            format="YYYY-MM-DD"
        )

        df_day = df[df["date"].dt.date == selected_day]
        df_day = df_day.sort_values("sentiment", ascending=False).reset_index(drop=True)
        df_day["rank"] = df_day.index + 1

        espn_day = espn_df[espn_df["date"].dt.date == selected_day][["rank", "name"]]
        espn_day.rename(columns={"name": "espn_player"}, inplace=True)

        df_day = pd.merge(df_day, espn_day, on="rank", how="left")

        df_day = df_day[["rank", "player", "espn_player", "sentiment"]]

        st.dataframe(df_day,hide_index=True)
