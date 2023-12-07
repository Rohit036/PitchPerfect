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


with open('tags.json','r') as jf:
    outer_dict=json.load(jf)

csv_data=pd.read_csv('database_dict.csv')

master_data = pd.read_csv("master.csv")
master_data['DATA_DATE'] = pd.to_datetime(master_data['DATA_DATE'], format='%d-%m-%Y')

import re

def extract_code_blocks(text, language=None):
    """
    Extract code blocks from a given text.
    
    :param text: The text containing code blocks.
    :param language: Optional, specify the language of the code block (e.g., 'python').
    :return: A list of code blocks found in the text.
    """
    if language:
        pattern = r'```' + language + r'[\s\S]*?\n(.*?)```'
    else:
        pattern = r'```[\s\S]*?\n(.*?)```'

    code_blocks = re.findall(pattern, text, re.DOTALL)
    return [code.strip() for code in code_blocks]

# Adjusting the filter function to match all conditions and consider lowercase
def filter_dataframe_all_conditions(df, criteria):
    # Convert relevant columns to lowercase for case-insensitive matching
    print(criteria)
    print(df.shape)
    for key in criteria.keys():
        if key in df.columns and df[key].dtype == 'object':
            df[key] = df[key].str.lower()
    # Apply filters
    for key, values in criteria.items():
        if values:  # Check if there are values to filter by
            if key in df.columns:  # Check if the column exists in the DataFrame
                # Convert values to lowercase for comparison
                lowercase_values = [value.lower() for value in values]
                # Filter the DataFrame based on the values
                # df = df[df[key].isin(lowercase_values)]
                df = df[df[key].apply(lambda x: any(value in str(x) for value in lowercase_values))]
    print(df.shape)
    return df

tags_list = []
inner_dict = {}
for k,v in outer_dict.items():
    inner_dict.update(v)
    for key,value in v.items():
        tags_list.append(key)

selected_options = []
#TODO : Make this as Dummy Full Dataframe.
# st.session_state.data_to_query = pd.DataFrame()
filtered_df=pd.DataFrame()
filter_dict={}
# formatted_system_message_python = "nothign"

st.title(":blue[Market Connect (Natural Language)]")

# Sidebar - Nested Multiselect for column and values
with st.sidebar:
    tags_selection = st.multiselect("Select Tags", tags_list, key = 'tags_select')

    if tags_selection:
        for tag in tags_selection:
            tag_values=inner_dict[tag]
            for outer_key,inner in outer_dict.items():
                if tag in inner:
                    filter_dict.update({outer_key:tag_values})
        filtered_df = filter_dataframe_all_conditions(csv_data, filter_dict)
        indicators_selection = st.multiselect("Select indicators", filtered_df['definitive_name'].to_list(), key='indicators_select')
        selected_options = indicators_selection
    else:
        selected_options = []
    
    submit_button = st.button("Submit Selection")

if submit_button:
    # @st.cache_data
    def filter_data(tags_selection):
        print(tags_selection)
        if tags_selection:
            return master_data[master_data['definitive_name'].isin(tags_selection)]
    # Filtered DataFrame
    if 'data_to_query' not in st.session_state:
        st.session_state.data_to_query = filter_data(selected_options)
    # Displaying filtered data (for reference, can be removed)
    st.write("Filtered Data:")
    st.write(st.session_state.data_to_query)
            
# SYSTEM_MESSAGE_PYTHON = """You are an AI assistant that is able to convert natural language into a properly formatted Python code including importing libraries, making any preprocessing required.  

# - The data you will be querying is called is saved in a "data_to_query" dataframe.
# - These are the columns along with their type of the data_to_query : ["DATA_DATE", "DATA_VALUE", "definitive_name"]
# - The data_date format is DD-MM-YYYY. 
# - Here are the values you need to filter the "definitive_name" of data_to_query : {selected_options_string} and answer.
# - The aggregation has to be done on the DATA_VALUE column. """

# formatted_system_message_python = SYSTEM_MESSAGE_PYTHON.format(columns_string = ", ".join(st.session_state.data_to_query.columns),
#                                                         selected_options_string= selected_options,
#                                                         filter_options = selected_options)

# print(formatted_system_message_python)
# print(st.session_state.data_to_query.head())

# OPENAI_API_KEY = "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"
openai_api_key = "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"
OPENAI_API_KEY = "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"
# client = OpenAI(api_key=OPENAI_API_KEY)

# if "openai_model" not in st.session_state:
#     st.session_state["openai_model"] = "gpt-3.5-turbo"

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
    