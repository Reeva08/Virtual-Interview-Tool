import streamlit as st
import google.generativeai as genai
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

# Helper functions to update session state
def complete_setup():
    st.session_state.setup_complete = True

def show_feedback():
    st.session_state.feedback_shown = True

# Setup stage for collecting user details
if not st.session_state.setup_complete:
    st.subheader('Personal Information')

    # Initialize session state for personal information
    if "name" not in st.session_state:
        st.session_state["name"] = ""
    if "experience" not in st.session_state:
        st.session_state["experience"] = ""
    if "skills" not in st.session_state:
        st.session_state["skills"] = ""

    # Get personal information input
    st.session_state["name"] = st.text_input("Name", value=st.session_state["name"], placeholder="Enter your name", max_chars=40)
    st.session_state["experience"] = st.text_area("Experience", value=st.session_state["experience"], placeholder="Describe your experience", max_chars=200)
    st.session_state["skills"] = st.text_area("Skills", value=st.session_state["skills"], placeholder="List your skills", max_chars=200)

    # Company and Position Section
    st.subheader('Company and Position')

    if "level" not in st.session_state:
        st.session_state["level"] = "Junior"
    if "position" not in st.session_state:
        st.session_state["position"] = "Data Scientist"
    if "company" not in st.session_state:
        st.session_state["company"] = "Amazon"

    col1, col2 = st.columns(2)
    with col1:
        st.session_state["level"] = st.radio(
            "Choose level",
            options=["Junior", "Mid-level", "Senior"],
            index=["Junior", "Mid-level", "Senior"].index(st.session_state["level"])
        )

    with col2:
        st.session_state["position"] = st.selectbox(
            "Choose a position",
            ("Data Scientist", "Data Engineer", "ML Engineer", "BI Analyst", "Financial Analyst"),
            index=("Data Scientist", "Data Engineer", "ML Engineer", "BI Analyst", "Financial Analyst").index(st.session_state["position"])
        )

    st.session_state["company"] = st.selectbox(
        "Select a Company",
        ("Amazon", "Meta", "Udemy", "365 Company", "Nestle", "LinkedIn", "Spotify"),
        index=("Amazon", "Meta", "Udemy", "365 Company", "Nestle", "LinkedIn", "Spotify").index(st.session_state["company"])
    )

    # Button to complete setup
    if st.button("Start Interview", on_click=complete_setup):
        st.write("Setup complete. Starting interview...")

# Interview phase
if st.session_state.setup_complete and not st.session_state.feedback_shown and not st.session_state.chat_complete:
    
    st.info("👋 Start by introducing yourself")

    # Initialize Gemini API
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

    if "gemini_model" not in st.session_state:
        st.session_state["gemini_model"] = "gemini-1.5-pro"

    # Ensure chatbot starts the interview immediately
    system_prompt = (
        f"You are an HR executive conducting an interview for {st.session_state['name']}."
        f"Candidate Details:\n"
        f"- Experience: {st.session_state['experience']}\n"
        f"- Skills: {st.session_state['skills']}\n"
        f"- Position: {st.session_state['level']} {st.session_state['position']}\n"
        f"- Company: {st.session_state['company']}\n\n"
        "Start the interview immediately with a structured question. Ask one question at a time and respond dynamically based on user input."
    )

    if not st.session_state.messages:
        st.session_state.messages.append({"role": "system", "content": system_prompt})

    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Handle user input
    if st.session_state.user_message_count < 5:
        prompt = st.chat_input("Your response")
        if prompt:
            with st.chat_message("user"):
                st.markdown(prompt)

            if st.session_state.user_message_count < 4:
                with st.chat_message("assistant"):
                    model = genai.GenerativeModel(st.session_state["gemini_model"])
                    response = model.generate_content(
                        f"Continue the structured job interview for {st.session_state['name']} applying for {st.session_state['position']} at {st.session_state['company']}."
                        f"Candidate's response: {prompt}\n"
                        f"HR Interviewer's response:"
                    ).text
                    st.write(response)

                st.session_state.messages.append({"role": "assistant", "content": response})

            # Increment user message count
            st.session_state.user_message_count += 1

    # Check if interview is complete
    if st.session_state.user_message_count >= 5:
        st.session_state.chat_complete = True

# Show "Get Feedback"
if st.session_state.chat_complete and not st.session_state.feedback_shown:
    if st.button("Get Feedback", on_click=show_feedback):
        st.write("Fetching feedback...")

# Show feedback screen
if st.session_state.feedback_shown:
    st.subheader("Feedback")

    conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])

    if "feedback_response" not in st.session_state:
        feedback_model = genai.GenerativeModel("gemini-1.5-pro")
        st.session_state["feedback_response"] = feedback_model.generate_content(
            f"You are an experienced HR professional. Evaluate this interview and provide feedback on the candidate's performance. "
            f"Identify strengths, weaknesses, and areas for improvement. Rate their overall performance and suggest how they can improve. "
            f"Do not ask further questions—just provide an assessment.\n\n"
            f"Interview transcript:\n{conversation_history}"
        )

    st.write(st.session_state["feedback_response"].text)
