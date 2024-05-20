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

# localy stored background picture
@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    body {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    
    st.markdown(page_bg_img, unsafe_allow_html=True)
    return

# define the click state of the button
def click_button():
    st.session_state.clicked = True

# RAG PART - define the function to apply the logic to the user input string
def process_string(input_string: str):
    client = openai.AzureOpenAI(
        azure_endpoint = "https://YOUR-ENDPOINT.openai.azure.com",
        api_key = os.getenv("AZURE_OPENAI_API_KEY"),
        api_version = "YOUR_VERSION"
    )
    completion = client.chat.completions.create(
        model="YOUR_MODEL",
        messages=[
            {"role": "user",
             "content": input_string,

            },
        ],
        extra_body={
            "data_sources":[
                {
                    "type": "azure_search",
                    "parameters" : {
                        "endpoint": os.environ.get["AZURE_AI_SEARCH_ENDPOINT"],
                        "index_name": os.environ.get["AZURE_AI_SEARCH_INDEX"],
                        "authentication":{
                            "type": "api_key",
                            "key": os.environ.get["AZURE_AI_SEARCH_API_KEY"],
                        }


                    }
                }
            ]
        }
    )

    output = completion.choices[0].message.content
    return output

# Streamlit app
def main():
    set_png_as_page_bg("PATH_TO_YOUR_LOCAL_BACKGROUND_IMAGE.gif")
    
    st.title("Title of your app")

    form = st.form(key = "my_form")
    user_input = form.text_input(label = "Your question:")
    submit_button = form.form_submit_button(label = "Submit")

    if submit_button:
        # process the input string
        result = process_string(user_input)

        # display the output string with typewriter effect
        st.write_stream(stream_data(result))

if __name__ == "__main__":
    main()