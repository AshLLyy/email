#%%
import streamlit as st
import requests
import json
import logging
from typing import Optional

#load environment variables if needed

#constant (dari langflow)
BASE_API_URL = "http://127.0.0.1:7860"
FLOW_ID = "e7396134-9c1b-49b8-a7e2-06fede98624d"
ENDPOINT = "mail" # The endpoint name of the flow

# You can tweak the flow by adding a tweaks dictionary
# e.g {"OpenAI-XXXXX": {"model_name": "gpt-4"}}
TWEAKS = {
  "ChatInput-stfLm": {},
  "ChatOutput-ZEZD0": {},
  "OpenAIModel-lfgyD": {},
  "Prompt-IRQAZ": {},
  "TextInput-xT4CS": {},
  "TextInput-rmKJa": {}
}

#initialize logging  easy can do the debug
logging.basicConfig(level=logging.INFO)

#Funtion to run the flow (ni dari langflow)
def run_flow(message: str,
  endpoint: str,
  output_type: str = "chat",
  input_type: str = "chat",
  tweaks: Optional[dict] = None,
  api_key: Optional[str] = None) -> dict:
    """
    Run a flow with a given message and optional tweaks.

    :param message: The message to send to the flow
    :param endpoint: The ID or the endpoint name of the flow
    :param tweaks: Optional tweaks to customize the flow
    :return: The JSON response from the flow
    """
    api_url = f"{BASE_API_URL}/api/v1/run/{endpoint}"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if api_key:
        headers = {"x-api-key": api_key}
    response = requests.post(api_url, json=payload, headers=headers)
    #return response.json()

    #log the reponse for debugging
    logging.info(f"Response Status Code: {response.status_code}")
    logging.info(f"Response Text: {response.text}")

    try:
        return response.json()
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON from the server response.")
        return{}

#Function to extract the assistance's message from the response
def extract_message(response: dict) -> str:
    try: 
        #extract the response message
        return response['outputs'][0]['outputs'][0]['results']['message']['text']
    except(KeyError, IndexError):
        logging.error("No valid message found in response.")
        return "No valid message found in response."
    
#streamlit application
def main():
    st.title("Langflow Chatbot")

    #sidebar twearking inouts
    with st.sidebar:
        st.title('Email helper chatbot')
        st.markdown('''## Who do you want to send? Please provide information.''')

        #text inputs for user to specify input value 
        recipient_email = st.text_input("Recipient email: ", placeholder="Please provide recipient email here.")
        recipient_name = st.text_input("Receipient name: ", placeholder="Please provide recipient name here.")

        #if these inputs are provided, update TWEAKS (UPD)
        if recipient_email:
            TWEAKS["TextInput-xT4CS"]['input_value'] = recipient_email
        if recipient_name:
            TWEAKS["TextInput-rmKJa"]['input_value'] = recipient_name

        st.success("Parameters updated successfull")

    #initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    #display previous messages with avatars
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=message["avatar"]):
            st.write(message["content"])

    #input box for user message
    if query := st.chat_input("please provide your email criteria here"):
        #add user message to session state
        st.session_state.messages.append(
            {
                "role": "user",
                "content": query,
                "avatar": "👀", #emoji for user
            }
        ) 
        with st.chat_message("user", avatar="👀"): #display user message
            st.write(query)

        #call the langflow API and get the assistant's response
        with st.chat_message("assistant", avatar="👩‍🦳"): #emoji for assistance
            message_placeholder = st.empty()
            with st.spinner("Thinking..."):
                #Fetch response from langflow with updated TWEAKS and using query
                assistant_response = extract_message(run_flow(query, endpoint=ENDPOINT, tweaks=TWEAKS))
                message_placeholder.write(assistant_response)

        #add assistant ressponse to session state
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": assistant_response,
                "avatar": "👩‍🦳", #emoji
            }
        )

if __name__ == "__main__":
    main()

# %%
