import streamlit as st
from difflib import get_close_matches
import pandas as pd
from rapidfuzz import process, fuzz, utils
# import adal
import struct
# import pyodbc
import pandas as pd
# from azure import identity
import os
# from azure.keyvault.secrets import SecretClient
# from azure.identity import DefaultAzureCredential
import json
import re
from langchain.callbacks import StreamlitCallbackHandler
from langchain.llms import OpenAI
from langchain.chat_models import AzureChatOpenAI

from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent


csv_data_woindi=pd.read_csv('all_indicators.csv')
csv_data_woindi = csv_data_woindi.pivot_table(index='indicator_name', columns='tag_key', values='tag_value', aggfunc=lambda x: ', '.join(x))

# Reset index to make 'indicator_name' a column again
csv_data_woindi.reset_index(inplace=True)

# all_indicators=pd.read_csv('pivoted_indicators.csv')
all_indicators_combined_tags=pd.read_csv('indicator_tags_combined.csv')

# predefined_list = all_indicators["indicator_name"].to_list()
predefined_list = all_indicators_combined_tags["indicator_name"].to_list()

def find_close_matches(input_string):
    # Find the closest matches in the predefined list to the input string
    temp = [match[0] for match in process.extract(input_string, all_indicators_combined_tags["indicator_feature_combined"], scorer=fuzz.WRatio, limit=5)]
    temp = match_values_and_get_names(temp)
    return temp

# Function to match values and get corresponding indicator names
def match_values_and_get_names(values):
    matched_names = []
    for value in values:
        matched_row = all_indicators_combined_tags[all_indicators_combined_tags['indicator_feature_combined'] == value]
        if not matched_row.empty:
            matched_names.append(matched_row['indicator_name'].iloc[0])
    return matched_names

### callback methods for buttons to preserve the state
def submit_button_callback_woindi():
    st.session_state.submit_button_clicked_woindi=True
def clear_button_callback_woindi():
    st.session_state.submit_button_clicked_woindi=False

st.title(":blue[Market Connect (Without Indicators)]")

# Sidebar
with st.sidebar:
    user_input = st.text_input("Enter a string:")
    if user_input:
        close_matches = find_close_matches(user_input)
    else:
        close_matches = []
    selected_options_woindi_test = st.multiselect("Select items:", options=predefined_list, default=close_matches, key= "woindicator_multiselect_test")
    if "submit_button_clicked_woindi" not in st.session_state:
        st.session_state.submit_button_clicked_woindi=False    
    submit_button_woindi_test = st.button("Submit", key="woindicator_submit_test",
                                          on_click=submit_button_callback_woindi)

data_to_query_woindi = pd.DataFrame()
# Main Page
if submit_button_woindi_test or st.session_state.submit_button_clicked_woindi:
    def filter_data_woindi(tags_selection_woindi):
        print(tags_selection_woindi)
        if tags_selection_woindi:            
            # df_woindi = pd.read_sql_query(query_woindi, engine)
            df_dropped_woindi = pd.read_csv("indicator_values_2023.csv")
            df_dropped_woindi = df_dropped_woindi[df_dropped_woindi['indicator_name'].isin(tags_selection_woindi)]
            # Drop the specified columns
            # df_dropped_woindi = df_woindi.drop(['last_modified_date', 'calculated_flag', 'unit_type', 'indicator_id', 'indicator_code', 'frequency'], axis=1)
            # df_dropped_woindi = df_dropped_woindi.dropna(subset=['value', 'date']).reset_index(drop = True)
            df_dropped_woindi['date'] = pd.to_datetime(df_dropped_woindi['date'])
            df_dropped_woindi = df_dropped_woindi.sort_values(by="date")
            tag_feature_merged_woindi = pd.merge(df_dropped_woindi, csv_data_woindi, on="indicator_name", how="left")
            print(tag_feature_merged_woindi.info())
            return tag_feature_merged_woindi
        else:
            return pd.DataFrame()

    st.write("Filtered Data:")
    data_to_query_woindi = filter_data_woindi(selected_options_woindi_test)
    st.write(data_to_query_woindi)

if "messages_woindi" not in st.session_state or st.sidebar.button("Clear conversation history", key="clear_cov_woindi", on_click=clear_button_callback_woindi):
    st.session_state["messages_woindi"] = [{"role": "assistant", 
                                    "content": "How can I help you?"}]

for msg in st.session_state.messages_woindi:
    st.chat_message(msg["role"]).write(msg["content"])


if prompt_woindi := st.chat_input(placeholder="What is this data about?",key="woindi"):
    st.session_state.messages_woindi.append({"role": "user", "content": prompt_woindi})
    st.chat_message("user").write(prompt_woindi)

    df_woindi = data_to_query_woindi

    OPENAI_API_KEY_PER = "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"
    
    pandas_df_agent_woindi = create_pandas_dataframe_agent(OpenAI(temperature=0, openai_api_key = OPENAI_API_KEY_PER), 
                        df_woindi, 
                        verbose=True)

    with st.chat_message("assistant"):
        st_cb_woindi = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        response_woindi = pandas_df_agent_woindi.run(st.session_state.messages_woindi, callbacks=[st_cb_woindi])
        st.session_state.messages_woindi.append({"role": "assistant", "content": response_woindi})
        st.write(response_woindi)
