import streamlit as st
from ui_v2.components.html import title

def render_settings():
    title('Settings','Project and AI configuration')
    st.info('Детальные настройки будут жить рядом с действиями через ⚙. Здесь только базовые настройки проекта.')
    st.text_input('Project name', value='OrgMeter')
    st.selectbox('Default language', ['Auto','Russian','English'])
    st.selectbox('Default local model', ['qwen2.5:7b','qwen2.5:3b','qwen2.5:14b'])
