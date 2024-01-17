import streamlit as st
from difflib import get_close_matches
import pandas as pd
from rapidfuzz import process, fuzz, utils
# import adal
import struct
# import pyodbc
import pandas as pd
import json
import re
from langchain.callbacks import StreamlitCallbackHandler
from langchain.llms import OpenAI
from langchain.chat_models import AzureChatOpenAI

from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent


csv_data_indi=pd.read_csv('all_indicators.csv')
csv_data_indi = csv_data_indi.pivot_table(index='indicator_name', columns='tag_key', values='tag_value', aggfunc=lambda x: ', '.join(x))

# Reset index to make 'indicator_name' a column again
csv_data_indi.reset_index(inplace=True)

def filter_indicators_by_auto_tags(df, input_list):
    columns_for_values = {}
    for value in input_list:
        for key, values in tags_dict.items():
            if value in values:
                columns_for_values.setdefault(key, []).append(value)
                break

    # Apply filters to the dataframe
    # Use OR within each column for multiple values and AND among columns
    filtered_conditions = []
    for key, values in columns_for_values.items():
        condition = df[key].str.contains('|'.join(values), na=False)
        filtered_conditions.append(condition)

    # Combine all conditions with AND
    final_condition = pd.concat(filtered_conditions, axis=1).all(axis=1)

    # Apply the final condition to the transformed dataframe
    filtered_result_with_multiple_values = df[final_condition]

    # Display the filtered dataframe
    return filtered_result_with_multiple_values

tags_dict = {'region': ['China', 'Southeast Asia', 'JKT', 'Global', 'Australia', 'South America', 'Europe', 'MENA', 'India', 'North America', 'CIS', 'Turkey'], 'type': ['Iron Ore', 'Concentrates', 'Pig iron', 'Steel', 'Metallics', 'BOF', 'Sinter Fines', 'Lumps', 'Scrap', 'HRC', 'Rebar', 'Billet', 'Macroeconomic', 'Freight', 'Pellets', 'Slab', 'EAF', 'Coal', 'Coking Coal', 'Coke', 'DRI', 'PCI', 'Plate', 'CRC', 'Wire Rod', 'Sinter Feed', 'HBI', 'Bunker', 'Green'], 'frequency': ['weekly', 'daily', 'monthly', 'quarterly', 'yearly', '10-day'], 'source': ['Mysteel', 'Argus', 'Platts', 'Bloomberg', 'MultiSource', 'Vale', 'Fastmarkets', 'Oxford', 'Tathya'], 'functionality': ['Stocks', 'Mines', 'Mills', 'Production', 'Margins', 'Differentials', 'Seaborne', 'Prices', 'Premiums', 'Spreads', 'Ports', 'Shipments', 'Industrial', 'Costs', 'Ratios', 'Consumption', 'Financial', 'Cities', 'Domestic', 'Currency', 'Sales', 'Traders', 'Utilization', 'Premium']}

all_values_list = [item for sublist in tags_dict.values() for item in sublist]

selected_options = []
filtered_df=pd.DataFrame()

### callback methods for buttons to preserve the state
def submit_button_callback_indi():
    st.session_state.submit_button_clicked_indi=True
def clear_button_callback_indi():
    st.session_state.submit_button_clicked_indi=False

st.title(":blue[Market Connect (Without Indicators)]")

# Sidebar
with st.sidebar:
    tags_selection_indi = st.multiselect("Select Tags", all_values_list, key = 'tags_select')
    if tags_selection_indi:
        filtered_df = filter_indicators_by_auto_tags(csv_data_indi, tags_selection_indi)
        indicators_selection = st.multiselect("Select indicators", filtered_df['indicator_name'].unique().tolist(), key='indicators_select_indi')
        selected_options = indicators_selection
    else:
        selected_options = []
    
    ## adding button click to session to preserve state 
    if "submit_button_clicked" not in st.session_state:
        st.session_state.submit_button_clicked=False
    submit_button = st.button("Submit Selection",key='button_submit',on_click=submit_button_callback_indi)

data_to_query_indi = pd.DataFrame()
# Main Page
if submit_button_callback_indi or st.session_state.submit_button_clicked_indi:
    def filter_data_indi(tags_selection_indi):
        print(tags_selection_indi)
        if tags_selection_indi:
            df_dropped_indi = pd.read_csv("indicator_values_2023.csv")
            df_dropped_indi = pd.merge(df_dropped_indi[df_dropped_indi['indicator_name'].isin(tags_selection_indi)].drop(["frequency"], axis=1), csv_data_indi, on="indicator_name", how="left")
            df_dropped_indi['date'] = pd.to_datetime(df_dropped_indi['date'])
            df_dropped_indi = df_dropped_indi.sort_values(by="date")
            return df_dropped_indi
        else:
            return pd.DataFrame()

    st.write("Filtered Data:")
    data_to_query_indi = filter_data_indi(selected_options)
    st.write(data_to_query_indi)

if "messages_indi" not in st.session_state or st.sidebar.button("Clear conversation history", key="clear_cov_indi", on_click=clear_button_callback_indi):
    st.session_state["messages_indi"] = [{"role": "assistant", 
                                    "content": "How I can Help You?"}]

for msg in st.session_state.messages_indi:
    st.chat_message(msg["role"]).write(msg["content"])


if prompt_indi := st.chat_input(placeholder="What is this data about?",key="indi"):
    st.session_state.messages_indi.append({"role": "user", "content": prompt_indi})
    st.chat_message("user").write(prompt_indi)

    df_indi = data_to_query_indi

    OPENAI_API_KEY_PER = "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"
    
    pandas_df_agent_indi = create_pandas_dataframe_agent(OpenAI(temperature=0, model_name="gpt-3.5-turbo-instruct", openai_api_key = OPENAI_API_KEY_PER), 
                        df_indi, 
                        verbose=True)

    with st.chat_message("assistant"):
        st_cb_indi = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        response_indi = pandas_df_agent_indi.run(st.session_state.messages_indi, callbacks=[st_cb_indi])
        st.session_state.messages_indi.append({"role": "assistant", "content": response_indi})
        st.write(response_indi)
