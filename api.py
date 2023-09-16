import os
import openai
from dotenv import dotenv_values
import streamlit as st

config = dotenv_values(".env")

# openai.api_key = config["OPENAI_KEY"]
openai.api_key = st.secrets["OPENAI_KEY"],

def openai_call(input_prompt): 
    return openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": input_prompt},
            ],
            max_tokens=700,
            temperature=0.25
            )
 

# # Example usage:
# response = ask_openai()
# print("OpenAI's Response:", response)