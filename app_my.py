from openai import OpenAI
import streamlit as st 
st.write("Secrets found:", st.secrets)
st.title('_This_ is a:blue[ title] text :speech_balloon:')
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"
