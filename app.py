import streamlit as st
from chatbot import Chatbot

st.title("🔍 Automatic RAG Chatbot")

bot = Chatbot()

# Sidebar: Chat History
st.sidebar.title("Chat History")
history = bot.get_history()
for user_input, bot_response in history:
    st.sidebar.write(f"**You:** {user_input}")
    st.sidebar.write(f"**Bot:** {bot_response}")

# Chat Interface
query = st.text_input("Ask something:")
if query:
    response, docs = bot.chat(query)
    
    st.write("🤖 **Bot:**", response)
    st.write("📄 **Sources:**", [doc.metadata.get("source", "Unknown") for doc in docs])
