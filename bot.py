import streamlit as st
from utils import write_message
# tag::import_agent[]
from agent import generate_response
# end::import_agent[]

# tag::setup[]
# Page Config
st.set_page_config("Graph Chatbot", page_icon=":book:",layout ="centered")
# end::setup[]

# tag::session[]
# Set up Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi, I'm the Graph Chatbot!  How can I help you?"},
    ]
# end::session[]

# tag::submit[]
# Submit handler
def handle_submit(message):
    # Handle the response
    with st.spinner('searching in the knowelge Graph...'):
        # Call the agent
        response = generate_response(message)
        write_message('assistant', response)
        
# end::submit[]
st.title("Graph chatbot :book:")
st.markdown(
    """
    Welcome to the Graph Chatbot! Ask me anything in the graph data.
    """, 
    unsafe_allow_html=True
)
# tag::chat[]
# Display messages in Session State
for message in st.session_state.messages:
    write_message(message['role'], message['content'], save=False)

# Handle any user input
if prompt := st.chat_input("Send message"):
    # Display user message in chat message container
    write_message('user', prompt)

    # Generate a response
    handle_submit(prompt)
# end::chat[]
