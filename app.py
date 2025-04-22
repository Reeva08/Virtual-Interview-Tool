import streamlit as st
from google.generativeai import GenerativeModel
from streamlit_js_eval import streamlit_js_eval

# Setting up the Streamlit page configuration
st.set_page_config(page_title="StreamlitChatMessageHistory", page_icon="💬")
st.title("Chatbot")

# Initialize session state variables
if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False
if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0
if "feedback_shown" not in st.session_state:
    st.session_state.feedback_shown = False
if "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False
if "messages" not in st.session_state:
    st.session_state.messages = []


def complete_setup():
    st.session_state.setup_complete = True

def show_feedback():
    st.session_state.feedback_shown = True

if not st.session_state.setup_complete:
    st.subheader('Personal Information')
    st.session_state["name"] = st.text_input("Name", "")
    st.session_state["experience"] = st.text_area("Experience", "")
    st.session_state["skills"] = st.text_area("Skills", "")
    st.subheader('Company and Position')
    st.session_state["level"] = st.radio("Choose level", ["Junior", "Mid-level", "Senior"])
    st.session_state["position"] = st.selectbox("Choose a position", ["Data Scientist", "Data Engineer", "ML Engineer", "BI Analyst", "Financial Analyst"])
    st.session_state["company"] = st.selectbox("Select a Company", ["Amazon", "Meta", "Udemy", "365 Company", "Nestle", "LinkedIn", "Spotify"])
    if st.button("Start Interview", on_click=complete_setup):
        st.write("Setup complete. Starting interview...")

if st.session_state.setup_complete and not st.session_state.feedback_shown and not st.session_state.chat_complete:
    st.info("Start by introducing yourself", icon="👋")

    model = GenerativeModel("gemini-pro")

    if not st.session_state.messages:
        st.session_state.messages = [{"role": "system", "content": f"You are an HR executive interviewing {st.session_state['name']} with experience {st.session_state['experience']} and skills {st.session_state['skills']} for the {st.session_state['level']} {st.session_state['position']} position at {st.session_state['company']}."}]

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if st.session_state.user_message_count < 5:
        if prompt := st.chat_input("Your response", max_chars=1000):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            response = model.generate_content(prompt).text
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

            st.session_state.user_message_count += 1

    if st.session_state.user_message_count >= 5:
        st.session_state.chat_complete = True

if st.session_state.chat_complete and not st.session_state.feedback_shown:
    if st.button("Get Feedback", on_click=show_feedback):
        st.write("Fetching feedback...")

if st.session_state.feedback_shown:
    st.subheader("Feedback")
    conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])
    feedback = model.generate_content(f"Provide a score (1-10) and feedback for the following interview: {conversation_history}").text
    st.write(feedback)
    if st.button("Restart Interview", type="primary"):
        streamlit_js_eval(js_expressions="parent.window.location.reload()")
