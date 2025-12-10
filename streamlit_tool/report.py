import streamlit as st
import os

pdf_file_path = "./report.pdf"

if os.path.exists(pdf_file_path):
    st.pdf(pdf_file_path)
elif (os.path.exists("../report.pdf")):
    st.pdf("../report.pdf")
elif (os.path.exists("/mount/src/nba-player-social-media-post-analytics/streamlit_tool/report.pdf")):
    st.pdf("/mount/src/nba-player-social-media-post-analytics/streamlit_tool/report.pdf")
else:
    st.error(f"Path not found: "+pdf_file_path)
    current_file_path = os.path.abspath(__file__)
    st.write(f"{current_file_path}")