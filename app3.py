import streamlit as st
import pandas as pd
import json
# from openai import OpenAI
import streamlit as st
import pandas as pd
import json
import re
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI

from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent


# with open('tags.json','r') as jf:
#     outer_dict=json.load(jf)

csv_data=pd.read_csv('all_indicators.csv')

# master_data = pd.read_csv("master.csv")
# master_data['DATA_DATE'] = pd.to_datetime(master_data['DATA_DATE'], format='%d-%m-%Y')
master_data = pd.read_csv("indicator_values_2023.csv")

# Convert the date column to datetime format if it's not already
master_data['date'] = pd.to_datetime(master_data['date'])

print(master_data.info())

# # Drop the specified columns
# df_dropped = base_data2.drop(['last_modified_date', 'calculated_flag'], axis=1)
# master_data = df_dropped.dropna(subset=['value', 'date']).reset_index(drop = True)
# master_data = master_data[master_data['date'].dt.year >= 2020]


def filter_indicators_by_auto_tags(dataframe, tags, value_to_column):
    """
    Filter indicator names based on a list of tags, automatically determining the corresponding columns.
    
    :param dataframe: Pandas DataFrame containing the data.
    :param tags: List of tags to filter by.
    :param value_to_column: Dictionary mapping values to their respective columns.
    :return: DataFrame filtered by the specified criteria.
    """
    # Invert the value_to_column mapping
    column_to_values = {}
    for column, values in value_to_column.items():
        for value in values:
            column_to_values.setdefault(value, []).append(column)

    # Identify columns for each tag
    filters = {}
    for tag in tags:
        if tag in column_to_values:
            for column in column_to_values[tag]:
                if column in filters:
                    filters[column].append(tag)
                else:
                    filters[column] = [tag]

    # Apply filters
    filtered_df = dataframe.copy()
    for column, values in filters.items():
        filtered_df = filtered_df[filtered_df[column].isin(values)]

    return filtered_df

tags_dict = {'frequency': ['weekly', 'daily', 'monthly', 'quarterly', 'yearly', '10-day'], 'unit_name': ['MT', '%', 'USD/DMTU', 'USD/MT', 'USD/T', 'Index', 'RMB/T', 'Units', 'BRL', 'USD', 'RMB', 'EUR', 'AED', 'CHF', 'EGP', 'JPY', 'MZN', 'TRY', 'VND', 'MYR', 'EGP/T', 'INR/T', 'EUR/T', 'AED/T', 'RMB/WMT', 'T', 'Day', 'MT/Day', 'Billion RMB', 'PHP', 'BRL/T', 'JPY/T', 'TRY/T', 'KRW', 'GBP', 'MXN', 'THB', 'IRR', 'IDR', 'SAR', 'INR', 'SGD', 'CNY', 'ARS', 'CLP', 'TWD', '10KT', 'RMB/DMTU', 'RMB/toe', 'RUR/T', 'USD/ST'], 'unit_type': ['weight', 'generic', 'currency', 'time'], 'indicator_source_name': ['Mysteel', 'Argus', 'Platts', 'Bloomberg', 'MultiSource', 'Vale', 'Fastmarkets', 'Oxford', 'Tathya'], 'tag_value': ['China', 'Iron Ore', 'Stocks', 'Concentrates', 'Mines', 'Pig iron', 'Mills', 'Production', 'Steel', 'Metallics', 'BOF', 'Margins', 'Sinter Fines', 'Differentials', 'Seaborne', 'Prices', 'Premiums', 'Lumps', 'Scrap', 'Southeast Asia', 'HRC', 'JKT', 'Rebar', 'Spreads', 'Billet', 'Global', 'Ports', 'Shipments', 'Industrial', 'Macroeconomic', 'Freight', 'Costs', 'Australia', 'South America', 'Europe', 'Pellets', 'Ratios', 'Consumption', 'Financial', 'Slab', 'Cities', 'EAF', 'Coal', 'Coking Coal', 'Coke', 'Domestic', 'MENA', 'DRI', 'Currency', 'India', 'PCI', 'North America', 'CIS', 'Plate', 'Turkey', 'CRC', 'Sales', 'Wire Rod', 'Sinter Feed', 'HBI', 'Bunker', 'Traders', 'Utilization', 'Green', 'Premium']}

all_values_list = [item for sublist in tags_dict.values() for item in sublist]


selected_options = []
filtered_df=pd.DataFrame()
# formatted_system_message_python = "nothign"

st.title(":blue[Market Connect (Natural Language)]")

# Sidebar - Nested Multiselect for column and values
with st.sidebar:
    tags_selection = st.multiselect("Select Tags", all_values_list, key = 'tags_select')

    if tags_selection:
        filtered_df = filter_indicators_by_auto_tags(csv_data, tags_selection, tags_dict)
        indicators_selection = st.multiselect("Select indicators", filtered_df['indicator_name'].unique().tolist(), key='indicators_select')
        selected_options = indicators_selection
    else:
        selected_options = []
    
    submit_button = st.button("Submit Selection")

if submit_button:
    # @st.cache_data
    def filter_data(tags_selection):
        print(tags_selection)
        if tags_selection:
            return master_data[master_data['indicator_name'].isin(tags_selection)]
    # Filtered DataFrame
    if 'data_to_query' not in st.session_state:
        st.session_state.data_to_query = filter_data(selected_options)
    # Displaying filtered data (for reference, can be removed)
    st.write("Filtered Data:")
    st.write(st.session_state.data_to_query)
    print(st.session_state.data_to_query.info())

# OPENAI_API_KEY = "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"
openai_api_key = "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"
OPENAI_API_KEY = "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"

if "messages" not in st.session_state or st.sidebar.button("Clear conversation history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="What is this data about?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    llm = ChatOpenAI(
        temperature=0, openai_api_key=openai_api_key, streaming=True
    )
    df = st.session_state.data_to_query
    pandas_df_agent = create_pandas_dataframe_agent(OpenAI(temperature=0, openai_api_key = OPENAI_API_KEY), 
                        df, 
                        verbose=True)

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        response = pandas_df_agent.run(st.session_state.messages, callbacks=[st_cb])
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)
    