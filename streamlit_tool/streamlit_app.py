import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import psycopg


pages = {
    "Dashboard": [
        st.Page("database_querying.py", title="Interactive Database Dashboard"),
    ],
    "Figures": [
        st.Page("figure_required.py", title="Posts Per Platform Over Time"),
        st.Page("figure_1.py", title="Average Toxicity Over Time"),
        st.Page("figure_2.py", title="Post Sentiment Over Time"),
        st.Page("figure_3.py", title="Post Volume Ranking vs Season Leader Ranking"),
        st.Page("figure_4.py", title="Total Sentiment Score vs Season Leader Ranking"),
        st.Page("figure_5.py", title="Average Sentiment Score vs Season Leader Ranking"),
        st.Page("figure_6.py", title="Post Sentiment Over Time Per Player"),
    ],
    "Interactive Figures": [
        st.Page("figure_1_interactive.py", title="Sentiment Score Over Time Per Player"),
        st.Page("figure_2_interactive.py", title="Toxicity Score Over Time Per Player"),
        st.Page("figure_3_interactive.py", title="Top 50 Players By Sentiment Score vs ESPN Ranking"),
    ],
    "Report": [
        st.Page("report.py", title="Report"),
    ],
}

pg = st.navigation(pages, position="top")
pg.run()