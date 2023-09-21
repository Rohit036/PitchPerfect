import os
import openai
# from dotenv import dotenv_values
import streamlit as st

openai.api_key = st.secrets["OPENAI_KEY"]

def openai_call(input_prompt): 
    return openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": input_prompt},
            ],
            max_tokens=700,
            temperature=0.25
            )