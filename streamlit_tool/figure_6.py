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
        player_sentiment_scores = [[(0,0) for j in range(41)] for i in range(50)] 
        # (total_score, num_posts)
        startDate = datetime(2025, 10, 22)
        get_player_posts_query = """
                    SELECT player_id, post_id, sentiment_score
                    FROM player_posts ;
        """
        get_post_query = """
                    SELECT created_time
                    FROM posts
                    WHERE id = %s ;
        """
        cur.execute(get_player_posts_query)
        player_posts = cur.fetchall()
        # print(len(player_posts))
        for player_post in player_posts:
            player_id = player_post[0]
            post_id = player_post[1]
            sentiment_score = player_post[2]
            cur.execute(get_post_query,(post_id,))
            post = cur.fetchone()
            created_time = post[0]
            dateIndex = (created_time - startDate).days
            # if (dateIndex == 1 and player_id == 36 and sentiment_score < -0.5):
            #     print(post_id)
            if dateIndex >= 41 or dateIndex < 0:
                # print(dateIndex)
                continue
            else:
                player_sentiment_scores[player_id-1][dateIndex] = (player_sentiment_scores[player_id-1][dateIndex][0] + sentiment_score, player_sentiment_scores[player_id-1][dateIndex][1] + 1)
            # except:
                # print(dateIndex)
        # print(player_sentiment_scores)
        average_player_sentiment_scores = [[player_sentiment_scores[i][j][0] / player_sentiment_scores[i][j][1] for j in range(41)] for i in range(50)] 
        dates = []
        curDate = datetime(2025, 10, 22) 
        for i in range(41):
            dates.append(curDate)
            curDate = curDate + timedelta(hours=24)


        # fig = plt.figure(1)
        fig = plt.figure(figsize=(12, 6))

        # plt.plot(dates, average_player_sentiment_scores[0], label='LeBron James', color='#552583', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[1], label='Stephen Curry', color='#006BB6', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[2], label='Kevin Durant', color='#CE1141', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[3], label='Damian Lillard', color='#E03A3E', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[4], label='Jayson Tatum', color='#007A33', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[5], label='Jaylen Brown', color='#007A33', marker='s')
        # plt.plot(dates, average_player_sentiment_scores[6], label='James Harden', color='#c8102E', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[7], label='Kyrie Irving', color='#00538C', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[8], label='Anthony Davis', color='#00538C', marker='s')
        # plt.plot(dates, average_player_sentiment_scores[9], label='Jalen Brunson', color='#006BB6', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[10], label='Cade Cunningham', color='#C8102E', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[11], label='Anthony Edwards', color='#0C2340', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[12], label='Darius Garland', color='#860038', marker='x')
        # plt.plot(dates, average_player_sentiment_scores[13], label='Tyler Herro', color='#98002E', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[14], label='Jaren Jackson Jr.', color='#5D76A9', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[15], label='Evan Mobley', color='#860038', marker='s')
        # plt.plot(dates, average_player_sentiment_scores[16], label='Jalen Williams', color='#007ac1', marker='o')
        plt.plot(dates, average_player_sentiment_scores[17], label='Shai Gilgeous-Alexander', color='#007ac1', marker='s')
        plt.plot(dates, average_player_sentiment_scores[18], label='Nikola Jokic', color='#0E2240', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[19], label='Donovan Mitchell', color='#860038', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[20], label='Pascal Siakam', color='#FDBB30', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[21], label='Karl-Anthony Towns', color='#006BB6', marker='s')
        # plt.plot(dates, average_player_sentiment_scores[22], label='Alperen Sengun', color='#CE1141', marker='s')
        plt.plot(dates, average_player_sentiment_scores[23], label='Victor Wembanyama', color='#000000', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[24], label='Trae Young', color='#C8102E', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[25], label='Joel Embiid', color='#ed174c', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[26], label='Cooper Flagg', color='#00538C', marker='x')
        # plt.plot(dates, average_player_sentiment_scores[27], label='Domantas Sabonis', color='#542e91', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[28], label='LaMelo Ball', color='#1d1160', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[29], label='Franz Wagner', color='#0077c0', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[30], label='Paolo Banchero', color='#0077c0', marker='s')
        # plt.plot(dates, average_player_sentiment_scores[31], label='De’Aaron Fox', color='#000000', marker='s')
        # plt.plot(dates, average_player_sentiment_scores[32], label='Tyrese Haliburton', color='#FDBB30', marker='s')
        # plt.plot(dates, average_player_sentiment_scores[33], label='Kawhi Leonard', color='#c8102E', marker='s')
        plt.plot(dates, average_player_sentiment_scores[34], label='Luka Doncic', color='#552583', marker='s')
        plt.plot(dates, average_player_sentiment_scores[35], label='Tyrese Maxey', color='#ed174c', marker='s')
        # plt.plot(dates, average_player_sentiment_scores[36], label='Devin Booker', color='#e56020', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[37], label='Julius Randle', color='#0C2340', marker='s')
        # plt.plot(dates, average_player_sentiment_scores[38], label='Zach LaVine', color='#542e91', marker='s')
        # plt.plot(dates, average_player_sentiment_scores[39], label='Rudy Gobert', color='#0C2340', marker='x')
        # plt.plot(dates, average_player_sentiment_scores[40], label='Jamal Murray', color='#0E2240', marker='s')
        # plt.plot(dates, average_player_sentiment_scores[41], label='Amen Thompson', color='#CE1141', marker='x')
        plt.plot(dates, average_player_sentiment_scores[42], label='Giannis Antetokounmpo', color='#00471B', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[43], label='Bam Adebayo', color='#98002E', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[44], label='Ja Morant', color='#5D76A9', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[45], label='Chet Holmgren', color='#007ac1', marker='x')
        # plt.plot(dates, average_player_sentiment_scores[46], label='Jimmy Butler', color='#006BB6', marker='s')
        # plt.plot(dates, average_player_sentiment_scores[47], label='Zion Williamson', color='#85714D', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[48], label='Scottie Barnes', color='#ce1141', marker='o')
        # plt.plot(dates, average_player_sentiment_scores[49], label='Lauri Markkanen', color='#002B5C', marker='o')

        # print(player_sentiment_scores[35])
        # print(average_player_sentiment_scores[35])
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())  
        plt.gcf().autofmt_xdate()  

        
        plt.xlabel('Date')
        plt.ylabel('Average Sentiment Score')
        plt.title('Post Sentiment Over Time Per Player')
        plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left", fontsize=8)
        plt.grid(True)
        plt.tight_layout()
        
        plt.show()
        st.pyplot(fig)