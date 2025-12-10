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
        post_volume_rankings = []

        season_leader_rankings = []   

        colors = []
        print("figure 3")
        with open("data.csv", 'r') as file_object:
            next(file_object)
            for line in file_object:
                data = line.split(",")
                name = data[0]
                # print(data[1])
                total_sentiment_score = float(data[1])
                num_posts = int(data[2])
                average_sentiment_score = float(data[3])
                total_sentiment_score_ranking = int(data[4])
                num_posts_ranking = int(data[5])
                average_sentiment_score_ranking = int(data[6])
                espn_score = float(data[7])
                espn_score_ranking = int(data[8].strip())

                

                if (espn_score_ranking < 1):
                    continue
                else:
                    post_volume_rankings.append(num_posts_ranking)
                    season_leader_rankings.append(espn_score_ranking)
                    # print((num_posts_ranking,espn_score_ranking))
                    colors.append("blue")

            
        print((post_volume_rankings))
        print((season_leader_rankings))
        fig = plt.figure(figsize=(12, 6))
        plt.scatter(post_volume_rankings, season_leader_rankings, c=colors, alpha=0.5, cmap='viridis')
        plt.gca().invert_xaxis()
        plt.gca().invert_yaxis()
        plt.xlabel("Post Volume Rankings",fontsize=20)
        plt.ylabel("Season Leader Rankings",fontsize=20)
        plt.title("Post Volume Ranking vs Season Leader Ranking")

        plt.show()
        st.pyplot(fig)