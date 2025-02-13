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
        
    # Load existing sessions from database
    load_sessions_from_db()
    
    # Create first session if no sessions exist
    if not st.session_state.sessions:
        new_session_id = str(uuid.uuid4())
        create_session(new_session_id, "Chat 1")
    
    # Ensure current_session is always set to a valid session
    if 'current_session' not in st.session_state or st.session_state.current_session not in st.session_state.sessions:
        st.session_state.current_session = next(iter(st.session_state.sessions))

def load_sessions_from_db():
    """Load all sessions from the database"""
    try:
        # Get all sessions from database
        db_sessions = st.session_state.chatbot.db.get_all_sessions()
        
        # Update session state with database sessions
        for session_id, session_data in db_sessions.items():
            messages = st.session_state.chatbot.db.get_chat_history(session_id)
            
            st.session_state.sessions[session_id] = {
                'messages': [
                    {
                        'user_message': msg['user_message'],
                        'response': msg['response'],
                        'reference_docs': msg.get('reference_docs', [])
                    }
                    for msg in messages
                ],
                'created_at': session_data.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                'name': session_data.get('name', f"Chat {len(st.session_state.sessions) + 1}")
            }
    except Exception as e:
        st.error(f"Error loading sessions from database: {str(e)}")

def create_session(session_id, name):
    """Create a new session and save it to both state and database"""
    # Create session in state
    st.session_state.sessions[session_id] = {
        'messages': [],
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'name': name
    }
    
    # Save session metadata to database
    st.session_state.chatbot.db.create_session(
        session_id,
        {
            'created_at': st.session_state.sessions[session_id]['created_at'],
            'name': name
        }
    )

def create_new_chat():
    new_session_id = str(uuid.uuid4())
    new_chat_name = f"Chat {len(st.session_state.sessions) + 1}"
    create_session(new_session_id, new_chat_name)
    st.session_state.current_session = new_session_id

def format_session_name(session_id):
    session = st.session_state.sessions[session_id]
    return f"{session['name']}"

def main():
    # Initialize session state
    init_session_state()
    
    # Page configuration
    st.set_page_config(
        page_title="Chatbot",
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
    st.title("Chatbot")
    
    # Get current chat data
    current_chat = st.session_state.sessions[st.session_state.current_session]
    
    # Display current chat name
    st.subheader(current_chat['name'])
    
    # Chat messages container
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for i, msg in enumerate(current_chat['messages'][::-1]):
            with st.chat_message("user_message"):
                st.write(msg['user_message'])
            
            with st.chat_message("assistant"):
                st.write(msg['response'])
                
                # reference_docs in collapsible section
                if msg.get('reference_docs'):
                    with st.expander("📚 View References"):
                        for ref_idx, reference in enumerate(msg['reference_docs'], 1):
                            st.markdown(f"**Page Content:**\n> {reference['page_content']}")
                            # st.markdown(f"**Metadata:**")
                            st.markdown(f"- **Page:** {reference['metadata']['page_label']}")
                            # st.markdown(f"- **Page Label:** {reference['metadata']['page_label']}")
                            st.markdown(f"- **Source:** `{reference['metadata']['source']}`")
                            st.markdown("---")  # Adds a separator between references
    
    # User input
    user_message = st.chat_input("Type your message here...")
    
    if user_message:
        # Get chatbot response
        with st.spinner("Thinking..."):
            try:
                result = st.session_state.chatbot.chat(
                    user_message,
                    st.session_state.current_session
                )
                print("Result >>>>>>>>>>>>>>>>>>>>>", result)
                # Add to session history
                current_chat['messages'].append({
                    'user_message': user_message,
                    'response': result['response'],
                    'reference_docs': result.get('reference_docs', [])
                })
                
                st.rerun()
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()