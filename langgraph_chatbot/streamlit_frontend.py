import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

# st.session_state -> dict -> store the state of the app across reruns
Config = {'configurable': {'thread_id': 'thread-1'}}

if 'messages_history' not in st.session_state:
    st.session_state['messages_history'] = []


for message in st.session_state['messages_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])



user_input = st.chat_input('Type here...')

if user_input:

    # user message
    st.session_state['messages_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # Call the chatbot and get the response
    response = chatbot.invoke({'messages': [HumanMessage(content=user_input)]}, config = Config)
    ai_message = response['messages'][-1].content
    # assistant message
    st.session_state['messages_history'].append({'role': 'assistant', 'content': ai_message})
    with st.chat_message('assistant'):
        st.text(ai_message)