import streamlit as st
from datetime import datetime
import uuid
from typing import Dict
from chatbot import LangGraphChat

# Initialize session state for chats and messages
if 'chats' not in st.session_state:
    st.session_state.chats = {
        'chat_1': {
            'id': 'chat_1',
            'title': 'First Chat',
            'messages': [],
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'session_id': str(uuid.uuid4())
        }
    }

if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = 'chat_1'

if 'chatbot' not in st.session_state:
    st.session_state.chatbot = LangGraphChat()

# Page config
st.set_page_config(layout="wide", page_title="LangGraph Chatbot")

# Main layout
col1, col2 = st.columns([1, 3])

# Sidebar with chat list
with col1:
    st.header("Chats")
    
    # New chat button
    if st.button("New Chat"):
        new_chat_id = str(uuid.uuid4())
        st.session_state.chats[new_chat_id] = {
            'id': new_chat_id,
            'title': f'Chat {len(st.session_state.chats) + 1}',
            'messages': [],
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'session_id': str(uuid.uuid4())  # Unique session ID for LangGraphChat
        }
        st.session_state.current_chat_id = new_chat_id
        st.rerun()

    # Chat list
    for chat_id, chat in st.session_state.chats.items():
        if st.button(
            f"{chat['title']} - {chat['created_at']}", 
            key=f"chat_{chat_id}",
            use_container_width=True,
            type="secondary" if chat_id != st.session_state.current_chat_id else "primary"
        ):
            st.session_state.current_chat_id = chat_id
            st.rerun()

# Main chat interface
with col2:
    current_chat = st.session_state.chats[st.session_state.current_chat_id]
    st.header(f"Chat: {current_chat['title']}")

    # Display messages
    chat_container = st.container()
    with chat_container:
        for message in current_chat['messages']:
            with st.chat_message(message['role']):
                st.write(message['content'])
                
                # Display references if it's an assistant message
                if message['role'] == 'assistant' and 'references' in message:
                    with st.expander("References"):
                        for ref in message['references']:
                            if 'metadata' in ref:
                                st.markdown(f"**Source**: {ref['metadata'].get('source', 'Unknown')}")
                                if 'page' in ref['metadata']:
                                    st.markdown(f"**Page**: {ref['metadata']['page']}")
                            st.markdown(f">{ref['content']}")

    # Input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message
        current_chat['messages'].append({
            'role': 'user',
            'content': user_input
        })
        
        # Get response from LangGraphChat
        response = st.session_state.chatbot.chat(
            user_input=user_input,
            session_id=current_chat['session_id']
        )
        
        # Add assistant message
        current_chat['messages'].append({
            'role': 'assistant',
            'content': response['response'],
            'references': response['references']
        })
        
        st.rerun()

# CSS for better styling
st.markdown("""
    <style>
        .stButton button {
            text-align: left;
            padding: 10px;
            margin: 5px 0;
        }
        .chat-container {
            height: 600px;
            overflow-y: auto;
        }
        .stExpander {
            background-color: #f0f2f6;
            border-radius: 4px;
            margin: 10px 0;
            padding: 10px;
        }
    </style>
""", unsafe_allow_html=True)