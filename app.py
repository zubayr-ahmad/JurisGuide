import streamlit as st
import uuid
from datetime import datetime
from chatbot import LangGraphChat

# Initialize session state variables
def init_session_state():
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = LangGraphChat()
    
    if 'sessions' not in st.session_state:
        st.session_state.sessions = {}
    
    # Create first session if no sessions exist
    if not st.session_state.sessions:
        new_session_id = str(uuid.uuid4())
        st.session_state.sessions[new_session_id] = {
            'messages': [],
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'name': "Chat 1"
        }
        st.session_state.current_session = new_session_id
    
    # Ensure current_session is always set to a valid session
    if 'current_session' not in st.session_state or st.session_state.current_session not in st.session_state.sessions:
        st.session_state.current_session = next(iter(st.session_state.sessions))

def create_new_chat():
    new_session_id = str(uuid.uuid4())
    st.session_state.sessions[new_session_id] = {
        'messages': [],
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'name': f"Chat {len(st.session_state.sessions) + 1}"
    }
    st.session_state.current_session = new_session_id

def format_session_name(session_id):
    session = st.session_state.sessions[session_id]
    message_count = len(session['messages'])
    return f"{session['name']} ({message_count} messages)"

def main():
    # Initialize session state
    init_session_state()
    
    # Page configuration
    st.set_page_config(
        page_title="LangGraph Chatbot",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Sidebar
    with st.sidebar:
        st.header("Chat Sessions")
        
        # New chat button
        if st.button("➕ New Chat", key="new_chat_button", type="primary"):
            create_new_chat()
            st.rerun()
        
        st.divider()
        
        # Session list
        sorted_sessions = sorted(
            st.session_state.sessions.items(),
            key=lambda x: x[1]['created_at'],
            reverse=True
        )
        
        for session_id, session_data in sorted_sessions:
            # Create a unique key for each session button
            if st.button(
                format_session_name(session_id),
                key=f"session_{session_id}",
                use_container_width=True,
                type="secondary" if session_id != st.session_state.current_session else "primary"
            ):
                st.session_state.current_session = session_id
                st.rerun()
    
    # Ensure we have a valid current session
    if st.session_state.current_session not in st.session_state.sessions:
        st.session_state.current_session = next(iter(st.session_state.sessions))
    
    # Main chat interface
    st.title("LangGraph Chatbot")
    
    # Get current chat data
    current_chat = st.session_state.sessions[st.session_state.current_session]
    
    # Display current chat name
    st.subheader(current_chat['name'])
    
    # Chat messages container
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for i, msg in enumerate(current_chat['messages']):
            with st.chat_message("user"):
                st.write(msg['user'])
            
            with st.chat_message("assistant"):
                st.write(msg['response'])
                
                # References in collapsible section
                if msg.get('references'):
                    with st.expander("📚 View References"):
                        for ref_idx, reference in enumerate(msg['references'], 1):
                            st.markdown(f"**Reference {ref_idx}:**")
                            st.json(reference)
    
    # User input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Get chatbot response
        with st.spinner("Thinking..."):
            try:
                result = st.session_state.chatbot.chat(
                    user_input,
                    st.session_state.current_session
                )
                
                # Add to session history
                current_chat['messages'].append({
                    'user': user_input,
                    'response': result['response'],
                    'references': result.get('references', [])
                })
                
                st.rerun()
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()