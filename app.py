import os
import openai
import time
import streamlit as st
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# typewriter function
def stream_data(answer):
    for word in answer.split(" "):
        yield word + " "
        time.sleep(0.02)

# function to reset the history of the chat whenever the toggle switch was moved
def reset_conversation():
    st.session_state.messages = []

# localy stored background picture
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    body {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    
    st.markdown(page_bg_img, unsafe_allow_html=True)



# RAG PART - define the function to apply the logic to the user input string
def process_string(messages: str):
    client = openai.AzureOpenAI(
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key = os.getenv("AZURE_OPENAI_API_KEY"),
        api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    )
    completion = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_API_MODEL"),
        messages=messages,

        extra_body={
            "data_sources":[
                {
                    "type": "azure_search",
                    "parameters" : {
                        "endpoint": os.environ["AZURE_AI_SEARCH_ENDPOINT"],
                        "index_name": os.environ["AZURE_AI_SEARCH_INDEX"],
                        "authentication":{
                            "type": "api_key",
                            "key": os.environ["AZURE_AI_SEARCH_API_KEY"],
                        }


                    }
                }
            ]
        }
    )

    output = completion.choices[0].message.content
    return output

# ChatGPT - Define the function to apply some logic to the input string
def process_string_chat(messages):
    client = openai.AzureOpenAI(
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key = os.getenv("AZURE_OPENAI_API_KEY"),
        api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    )
    completion = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_API_MODEL"),
        messages=messages,
    )
    output = completion.choices[0].message.content
    return output

# Streamlit app
def main():
    st.set_page_config(page_title="GPT for YOUR COMPANY", page_icon="images/your_company_logo.png")
    set_background("images/your_background_picture.png")

    st.title(":red[GPT for YOUR COMPANY]")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # toggle switch
    on = st.toggle("Activate RAG feature (Default: ChatGPT)", on_change=reset_conversation)

    if on:
        st.write("RAG framework has been activated")

        # Display chat messages from the history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # React to user input
        if prompt := st.chat_input("Your question?"):
            # Display user message in chat message container
            st.chat_message("user").markdown(prompt)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("I have just connected to the APIs and I am searching in our databases, please wait..."):
                response = f"{process_string(st.session_state.messages)}"
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.write_stream(stream_data(response))
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        st.write("ChatGPT is active!")

        # Display chat messages from the history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # React to user input
        if prompt := st.chat_input("Your question?"):
            # Display user message in chat message container
            st.chat_message("user").markdown(prompt)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("I have just connected to the APIs and I am searching in our databases, please wait..."):
                response = f"{process_string_chat(st.session_state.messages)}"
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.write_stream(stream_data(response))
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()