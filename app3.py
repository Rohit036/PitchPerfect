import streamlit as st
import pandas as pd
import json
# from openai import OpenAI
import re
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI

from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent


# with open('tags.json','r') as jf:
#     outer_dict=json.load(jf)

csv_data=pd.read_csv('all_indicators.csv')
csv_data = csv_data.pivot_table(index='indicator_name', columns='tag_key', values='tag_value', aggfunc=lambda x: ', '.join(x))

# Reset index to make 'indicator_name' a column again
csv_data.reset_index(inplace=True)

# master_data = pd.read_csv("master.csv")
# master_data['DATA_DATE'] = pd.to_datetime(master_data['DATA_DATE'], format='%d-%m-%Y')
master_data = pd.read_csv("indicator_values_2023.csv")

# Convert the date column to datetime format if it's not already
master_data['date'] = pd.to_datetime(master_data['date'])

print(master_data.info())

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
# formatted_system_message_python = "nothign"

### callback methods for buttons to preserve the state
def submit_button_callback():
    st.session_state.submit_button_clicked=True
def clear_button_callback():
    st.session_state.submit_button_clicked=False

# OPENAI_API_KEY = "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"
openai_api_key = "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"
OPENAI_API_KEY = "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"
### Title of the app
st.title(":blue[Market Connect VALE (Natural Language)]")

# Sidebar - Nested Multiselect for column and values
with st.sidebar:
    selected_tab = st.radio("Select an option to query", ["With Indicators", "Without Indicators"])
if selected_tab == "With Indicators":
    with st.sidebar:
        tags_selection = st.multiselect("Select Tags", all_values_list, key = 'tags_select')
        if tags_selection:
            filtered_df = filter_indicators_by_auto_tags(csv_data, tags_selection)
            indicators_selection = st.multiselect("Select indicators", filtered_df['indicator_name'].unique().tolist(), key='indicators_select')
            selected_options = indicators_selection
        else:
            selected_options = []
        
        ## adding button click to session to preserve state 
        if "submit_button_clicked" not in st.session_state:
            st.session_state.submit_button_clicked=False
        submit_button = st.button("Submit Selection",key='button_submit',on_click=submit_button_callback)
    data_to_query=pd.DataFrame()

    ## check if button click is true since default session state for button becomes false on refresh 
    if submit_button or st.session_state.submit_button_clicked:
        # @st.cache_data
        def filter_data(tags_selection):
            print(tags_selection)
            if tags_selection:
                tag_feature_merged = pd.merge(master_data[master_data['indicator_name'].isin(tags_selection)].drop(["frequency"], axis=1), csv_data, on="indicator_name", how="left")
                return tag_feature_merged
            else:
                return pd.DataFrame()
        
        st.write("Filtered Data:")
        data_to_query = filter_data(selected_options)
        st.write(data_to_query)
        # st.write(st.session_state.data_to_query)
    
    if "messages" not in st.session_state or st.sidebar.button("Clear conversation history",on_click=clear_button_callback):
        st.session_state["messages"] = [{"role": "assistant", 
                                         "content": """Step 1. Match the indicator using contains in the indicator_name column of the dataframe. Ignore the case while matching.
                                                    Step 2. Ignore the text after special character like $ in the column name while matching.  
                                                    Step 3. Put the filter based on the above indicator_name selected and sort the values on date.
                                                    Step 4. Run the right mathematical operation based on above step 3 selection.
                                                    Step 5. For latest/maximum/current questions, sort_values based on date column only and answer for the highest date.
                                                    """}] 

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if len(tags_selection)> 0:
        if prompt := st.chat_input(placeholder="What is this data about?",key="with_tag"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)

            if not openai_api_key:
                st.info("Please add your OpenAI API key to continue.")
                st.stop()

            llm = ChatOpenAI(
                temperature=0, openai_api_key=openai_api_key, streaming=True
            )
            df = data_to_query
            pandas_df_agent = create_pandas_dataframe_agent(OpenAI(temperature=0, openai_api_key = OPENAI_API_KEY), 
                                df, 
                                verbose=True)

            with st.chat_message("assistant"):
                st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
                response = pandas_df_agent.run(st.session_state.messages, callbacks=[st_cb])
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.write(response)

    else:
        if prompt := st.chat_input(placeholder="Test", key="without_tag"): 
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            print("Readche here")
            with st.chat_message("assistant"):
                #st.session_state.messages.append({"role": "assistant", "content": "this hai "})
                st.write("Please select indicator to continue.")

elif selected_tab == "Without Indicators":
    if "messages" not in st.session_state or st.sidebar.button("Clear conversation history"):
        st.session_state["messages"] = [{"role": "assistant", 
                                         "content": """How can I help you?"""}] 
        
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input(placeholder="Enter your query"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)

            if not openai_api_key:
                st.info("Please add your OpenAI API key to continue.")
                st.stop()

            llm = ChatOpenAI(
                temperature=0, openai_api_key=openai_api_key, streaming=True
            )
            df = csv_data
            pandas_df_agent = create_pandas_dataframe_agent(OpenAI(temperature=0, openai_api_key = OPENAI_API_KEY), 
                                df, 
                                verbose=True)

            with st.chat_message("assistant"):
                st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
                response = pandas_df_agent.run(st.session_state.messages, callbacks=[st_cb])
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.write(response)

        
      
        
