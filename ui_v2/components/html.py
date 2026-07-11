import streamlit as st

def html(s:str): st.markdown(s, unsafe_allow_html=True)

def title(t,c): html(f"<div class='pb-title'>{t}</div><div class='pb-caption'>{c}</div>")
