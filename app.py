import streamlit as st
from chatbot import Chatbot

# Load or create session ID
if "session_id" not in st.session_state:
    st.session_state["session_id"] = None  # Initially set to None

# Initialize chatbot (pass session_id if resuming)
bot = Chatbot(session_id=st.session_state["session_id"])

st.title("Chatbot with Memory 🧠")

# Sidebar: List previous sessions
st.sidebar.header("Chat Sessions")
previous_sessions = bot.get_all_sessions()

if previous_sessions:
    selected_session = st.sidebar.selectbox("Select a session", previous_sessions)
    if st.sidebar.button("Load Chat"):
        st.session_state["session_id"] = selected_session
        bot = Chatbot(session_id=selected_session)  # Reload bot with selected session
        st.experimental_rerun()

# Chat history display
chat_history = bot.get_history()
st.subheader("Chat History")
for user_msg, bot_response in chat_history:
    st.markdown(f"**You:** {user_msg}")
    st.markdown(f"**Bot:** {bot_response}")

# Chat input
user_input = st.text_input("Ask me anything:", key="chat_input")

if st.button("Send"):
    if user_input:
        response, _ = bot.chat(user_input)
        st.session_state["session_id"] = bot.session_id  # Ensure session ID is stored
        st.experimental_rerun()
