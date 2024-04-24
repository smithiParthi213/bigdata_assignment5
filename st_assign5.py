# import streamlit as st
# import pandas as pd
# import snowflake.connector
# import openai
# import os

# # Snowflake connection parameters
# SNOWFLAKE_USER = "bigdata"
# SNOWFLAKE_PASSWORD = "BigData!123"
# SNOWFLAKE_ACCOUNT = "BZGXZMK-FE07643"
# SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
# SNOWFLAKE_DATABASE = "ASSIGN5"
# SNOWFLAKE_SCHEMA = "ASSIGN"

# # OpenAI API key
# OPENAI_API_KEY = "sk-proj-c1NChzaa8P0IrtHEbw4wT3BlbkFJO5KhK5YR1FmFgnVVSPy9"


# # Initialize OpenAI
# openai.api_key = OPENAI_API_KEY

# # Function to connect to Snowflake and fetch data
# #@st.cache(ttl=3600)  # Cache data for one hour to avoid re-fetching too often
# def fetch_data():
#     ctx = snowflake.connector.connect(
#         user=SNOWFLAKE_USER,
#         password=SNOWFLAKE_PASSWORD,
#         account=SNOWFLAKE_ACCOUNT,
#         warehouse=SNOWFLAKE_WAREHOUSE,
#         database=SNOWFLAKE_DATABASE,
#         schema=SNOWFLAKE_SCHEMA
#     )
#     cs = ctx.cursor()
#     try:
#         cs.execute("SELECT title, learning_outcomes FROM ASSIGN5_TABLE")
#         data = cs.fetchall()
#         df = pd.DataFrame(data, columns=['title', 'learning_outcomes'])
#     finally:
#         cs.close()
#     ctx.close()
#     return df


# primer = "You are a summary generation bot. designed to provide intelligent answers based on the information provided. If the information is not available, you truthfully say, 'I don't know'."


# # Function to generate summary using OpenAI
# def generate_summary(text):

    
#     prompt="Summarize the following learning outcomes: " + text
#     messages = [{"role": "system", "content": primer}, {"role": "user", "content": prompt}]
#     response = openai.chat.completions.create(
#         messages=messages,
#         model="gpt-3.5-turbo"
        
#     )
#     return response.choices[0].message.content.strip()

# # Streamlit app
# def main():
#     st.title("Learning Outcome Summarizer")
    
#     # Fetch data from Snowflake
#     data = fetch_data()
    
#     # Dropdown to select the title
#     title = st.selectbox("Select a Title", data['title'].unique())
    
#     # Button to generate summary
#     if st.button('Generate Summary'):
#         # Get learning outcomes for the selected title
#         learning_outcomes = data[data['title'] == title]['learning_outcomes'].iloc[0]
#         summary = generate_summary(learning_outcomes)
#         st.write(summary)

# if __name__ == "__main__":
#     main()



import streamlit as st
import pandas as pd
import snowflake.connector
import openai
import os
import pinecone

from pinecone import Pinecone
from pinecone import PodSpec


# Initialize OpenAI and Pinecone
api_key = "sk-proj-c1NChzaa8P0IrtHEbw4wT3BlbkFJO5KhK5YR1FmFgnVVSPy9"
client = openai.OpenAI(api_key=api_key)

papi_key="baff9b5e-e1a4-4e38-8929-0ba3276ce9bf"
pinecone = Pinecone(api_key=papi_key)


# Snowflake connection parameters
SNOWFLAKE_USER = "bigdata"
SNOWFLAKE_PASSWORD = "BigData!123"
SNOWFLAKE_ACCOUNT = "BZGXZMK-FE07643"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
SNOWFLAKE_DATABASE = "ASSIGN5"
SNOWFLAKE_SCHEMA = "ASSIGN"

# Function to connect to Snowflake and fetch data
#@st.cache(ttl=3600)  # Cache data for one hour
def fetch_data():
    ctx = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )
    cs = ctx.cursor()
    try:
        cs.execute("SELECT title, learning_outcomes FROM ASSIGN5_TABLE")
        data = cs.fetchall()
        df = pd.DataFrame(data, columns=['title', 'learning_outcomes'])
    finally:
        cs.close()
    ctx.close()
    return df



index_name = 'generate-summary'
#pinecone.create_index(index_name, dimension=1536)  # Adjust dimension based on the embedding model used
#pinecone.create_index(name=index_name, dimension=1536, spec = PodSpec(environment="gcp-starter"))
index = pinecone.Index(name=index_name)

# Function to generate embeddings and summary using OpenAI
def generate_summary_and_embeddings(title, text, namespace):
    
    # Generate embeddings
    embeddings_response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    embeddings = embeddings_response.data[0].embedding
    
    # Store embeddings in Pinecone
    index.upsert(vectors=[(title, embeddings)], namespace=namespace)
    
    
    
    # Generate summary
    primer = "You are a summary generation bot designed to provide intelligent answers."
    prompt = "Summarize the following learning outcomes: " + text
    messages = [{"role": "system", "content": primer}, {"role": "user", "content": prompt}]
    summary_response = openai.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo"
    )
    summary = summary_response.choices[0].message.content.strip()
    return summary


# Streamlit app
def main():
    st.title("Learning Outcome Summarizer")
    
    # Fetch data from Snowflake
    data = fetch_data()
    
    # Dropdown to select the title
    title = st.selectbox("Select a Title", data['title'].unique())
    
    # Button to generate summary
    if st.button('Generate Summary'):
        # Get learning outcomes for the selected title
        learning_outcomes = data[data['title'] == title]['learning_outcomes'].iloc[0]
        namespace = title
        summary = generate_summary_and_embeddings(title, learning_outcomes,namespace)
        st.write(summary)

if __name__ == "__main__":
    main()

