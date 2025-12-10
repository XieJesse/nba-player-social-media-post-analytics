import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import psycopg
from datetime import datetime, timedelta, timezone
import pandas as pd


with psycopg.connect(
    host=st.secrets["postgres"]["host"],
    port=st.secrets["postgres"]["port"],
    dbname=st.secrets["postgres"]["dbname"],
    user=st.secrets["postgres"]["user"],
    password=st.secrets["postgres"]["password"],
) as conn:
    # print("test")
    with conn.cursor() as cur:
        selected_platforms = []
        date_range = ()
        toxicity_score_range = ()
        with st.sidebar:  
            st.header("Filters", divider=True)
        
            platforms = ["youtube","bluesky","reddit-post","reddit-comment"]
            selected_platforms = st.multiselect("Platform: ", platforms, placeholder="Filter by platform",default=platforms)

            startDate = datetime(2025, 10, 21) 
            maxDate = datetime(2025, 12, 2) 

            date_range = st.slider(
                "Select a date range",
                min_value=startDate,
                max_value=maxDate,
                value=(startDate, maxDate),
                format="MM/DD/YY"
            )

            toxicity_score_range = st.slider("Post Toxicity", 0.0, 1.0, (0.0,1.0))

        
    
        get_posts_in_date_range_query = """
            SELECT id,title,platform,content,url,created_time,toxicity_score
            FROM posts
            ORDER BY id
        """
        cur.execute(get_posts_in_date_range_query)
        rows = cur.fetchall()

        st.header("Posts Table")
        df = pd.DataFrame(rows, columns=["id","title","platform","content","url","created_time","toxicity_score"])
        filtered_data = df[df['created_time'].between(pd.to_datetime(date_range[0], utc=True), pd.to_datetime(date_range[1], utc=True)) & df['toxicity_score'].between(toxicity_score_range[0], toxicity_score_range[1]) & df['platform'].isin(selected_platforms)]
        st.dataframe(filtered_data,selection_mode="single-row",hide_index=True)
            