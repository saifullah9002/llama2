import streamlit as st
import os
from together import Together

# App title
st.set_page_config(page_title="🦙💬 Llama 2 Chatbot")

# Together.ai Credentials
with st.sidebar:
    st.title('🦙💬 Llama 2 Chatbot')
    if 'TOGETHER_API_KEY' in st.secrets:
        st.success('API key already provided!', icon='✅')
        together_api = st.secrets['TOGETHER_API_KEY']
    else:
        together_api = "06ae5e599e89f3dc4a8b52f53432c9811567c5341238b8479c96ff45d5861b88"
        if not together_api:
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')

    # Refactored from https://github.com/a16z-infra/llama2-chatbot
    st.subheader('Models and parameters')
    selected_model = st.sidebar.selectbox('Choose a model', ['Mixtral-8x7B-Instruct-v0.1'], key='selected_model')
    
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.sidebar.slider('max_length', min_value=64, max_value=4096, value=512, step=8)
    
    st.markdown('📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')
os.environ['TOGETHER_API_KEY'] = together_api

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating Together.ai response
def generate_together_response(prompt_input):
    client = Together(api_key=together_api)
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
    response = client.chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        messages=[{"role": "user", "content": prompt_input}],
        temperature=temperature,
        top_p=top_p,
        max_length=max_length,
    )
    return response.choices[0].message.content

# User-provided prompt
if prompt := st.chat_input(disabled=not together_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_together_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
