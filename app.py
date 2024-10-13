import streamlit as st

# Page navigation using Streamlit's multipage capability
st.sidebar.title("Navigation")

# Links to pages
st.sidebar.write("[Transcription](transcription.py)")
st.sidebar.write("[Calendar](calendar.py)")

st.write("Select a page from the sidebar.")
