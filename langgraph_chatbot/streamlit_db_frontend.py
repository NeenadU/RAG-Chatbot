import streamlit as st
from langgraph_db_backend import chatbot, retrive_all_threads
from langchain_core.messages import BaseMessage, HumanMessage
import uuid 

#----------------------utitlity function-----------------
def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    st.session_state['chat_names'][str(thread_id)] = 'New Chat'
    add_thread(st.session_state['thread_id'])
    st.session_state['messages_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)

def load_conversation(thread_id):
    return chatbot.get_state(config = {'configurable': {'thread_id': thread_id}}).values['messages']



#-----------Session Setup-----------------
if 'messages_history' not in st.session_state:
    st.session_state['messages_history'] = []

if 'chat_names' not in st.session_state:
    st.session_state['chat_names'] = {}

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()
    st.session_state['chat_names'][str(st.session_state['thread_id'])] = 'New Chat'

if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread'] = retrive_all_threads()

add_thread(st.session_state['thread_id'])

# st.session_state -> dict -> store the state of the app across reruns
#-------------Sidebar-----------------
st.sidebar.title("LangGraph Chatbot")
if st.sidebar.button('New Chat'):
    reset_chat()
st.sidebar.header('My Conversations')

for thread_id in st.session_state['chat_thread'][::-1]:
    name = st.session_state['chat_names'].get(str(thread_id), 'New Chat')
    if st.sidebar.button(name, key=str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)
        temp_messages = []
        for message in messages:
            role = 'user' if isinstance(message, HumanMessage) else 'assistant'
            temp_messages.append({'role': role, 'content': message.content})
        st.session_state['messages_history'] = temp_messages

# st.sidebar.text(st.session_state['thread_id'])

for message in st.session_state['messages_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])



user_input = st.chat_input('Type here...')

if user_input:

    # Set conversation name from first message
    thread_key = str(st.session_state['thread_id'])
    if st.session_state['chat_names'].get(thread_key) in (None, 'New Chat'):
        st.session_state['chat_names'][thread_key] = user_input[:30]

    # user message
    st.session_state['messages_history'].append({'role': 'user', 'content': user_input})
    
    with st.chat_message('user'):
        st.text(user_input)

    # Call the chatbot and get the response
   # assistant message
    # st.session_state['messages_history'].append({'role': 'assistant', 'content': ai_message})
    # Config = {'configurable': {'thread_id': st.session_state['thread_id']}}

    Config = {
        "configurable": {"thread_id":str(st.session_state['thread_id'])},
        "metadata": {"thread_id": str(st.session_state['thread_id'])},
        "run_name" : "chat_run"
    }
    
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in  chatbot.stream(
                 {'messages':[HumanMessage(content= user_input)]},
                   config = Config,
                   stream_mode = 'messages'
            )
            if message_chunk.content
        )

    st.session_state['messages_history'].append({'role': 'assistant', 'content': ai_message})

    import time
    time.sleep(3)