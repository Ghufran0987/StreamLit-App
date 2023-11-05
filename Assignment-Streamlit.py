import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
import streamlit as st
import requests
import pandas as pd
import plotly.express as px 

scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"],scopes=scope)
gc = gspread.authorize(credentials)

# Open Google Sheets file
sheet = gc.open('ETL SHEET NEW')

# Read data from Google Sheets and convert it to a DataFrame
sheet_info = sheet.get_worksheet(0)
data = sheet_info.get_all_records()
df = pd.DataFrame(data)
# Initialize Google Sheets API
# scope = [
#     'https://spreadsheets.google.com/feeds',
#     'https://www.googleapis.com/auth/spreadsheets',
#     'https://www.googleapis.com/auth/drive.file',
#     'https://www.googleapis.com/auth/drive'
# ]

# credentials = ServiceAccountCredentials.from_se('etl-assignment-sheet-ed01e63f249c.json', scope)
# gc = gspread.authorize(credentials)

# # Open Google Sheets file
# sheet = gc.open('ETL SHEET NEW')

# # Read data from Google Sheets and convert it to a DataFrame
# sheet_info = sheet.get_worksheet(0)
# data = sheet_info.get_all_records()
# df = pd.DataFrame(data)

# Default Setup
st.set_page_config(
    page_title="Real-Time Data Science Dashboard",
    page_icon="✅",
    layout="wide",
)

# Streamlit UI
st.title("Consumer Financial Complaints Dashboard")

# DropDown
state_url = "https://gist.githubusercontent.com/mshafrir/2646763/raw/8b0dbb93521f5d6889502305335104218454c2bf/states_hash.json"
state_list = list(requests.get(state_url).json().keys())

state_list.insert(0, "All States")

state_filter = st.selectbox("Select the State", state_list, index=0)

# Define a function to calculate metrics based on the selected state
def calculate_metrics_for_state(df, selected_state):
    if selected_state == "All States":
        state_filtered_data = df
    else:
        state_filtered_data = df[df['state'] == selected_state]

    consumer_count = len(state_filtered_data)
    closed_complaints_count = len(state_filtered_data[state_filtered_data['company_response'].str.contains('Closed|Closed with explanation')])
    timely_responded_count = len(state_filtered_data[state_filtered_data['timely'] == 'Yes'])
    in_progress_count = len(state_filtered_data[state_filtered_data['company_response'] == 'In progress'])

    return consumer_count, closed_complaints_count, timely_responded_count, in_progress_count

# Set KPI

# create four columns
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

# Calculate metrics based on the selected state
consumer_count, closed_complaints, timely_responded, in_progress = calculate_metrics_for_state(df, state_filter)

# Fill in those columns with respective metrics or KPIs
kpi1.metric(
    label="Consumer Count",
    value=consumer_count
)

kpi2.metric(
    label="Closed Complaints",
    value=closed_complaints
)

kpi3.metric(
    label="Timely Responded",
    value=timely_responded
)

kpi4.metric(
    label="In Progress",
    value=in_progress
)
def complaints_by_product_chart(df, selected_state):
    # Filter data based on the selected state
    if selected_state == "All States":
        state_filtered_data = df
    else:
        state_filtered_data = df[df['state'] == selected_state]

    # Calculate the sum of complaints aggregated by product
    product_complaints_sum = state_filtered_data.groupby('product').size().reset_index(name='Number of Complaints')

    # Create a bar chart using Plotly Express
    fig = px.bar(product_complaints_sum, x='Number of Complaints', y='product', orientation='h')
    return fig

def complaints_by_month_year_chart(df, selected_state):
    # Filter data based on the selected state
    if selected_state == "All States":
        state_filtered_data = df
    else:
        state_filtered_data = df[df['state'] == selected_state]

    state_filtered_data['date'] = pd.to_datetime(state_filtered_data['date_received'])
    state_filtered_data['MonthYear'] = state_filtered_data['date'].dt.strftime('%Y-%m')
    complaints_by_month_year = state_filtered_data.groupby('MonthYear').size().reset_index(name='Number of Complaints')

    fig = px.line(complaints_by_month_year, x='MonthYear', y='Number of Complaints', title="Complaints by Month and Year")
    return fig

def complaints_by_submitted_via_chart(df, selected_state):
    # Filter data based on the selected state
    if selected_state == "All States":
        state_filtered_data = df
    else:
        state_filtered_data = df[df['state'] == selected_state]

    complaints_by_submitted_via = state_filtered_data.groupby('submitted_via').size().reset_index(name='Number of Complaints')

    fig = px.pie(complaints_by_submitted_via, values='Number of Complaints', names='submitted_via', title="Complaints by Submitted Via")
    return fig

def complaints_by_issue_and_sub_issue_chart(df, selected_state):
    # Filter data based on the selected state
    if selected_state == "All States":
        state_filtered_data = df
    else:
        state_filtered_data = df[df['state'] == selected_state]

    complaints_by_issue_and_sub_issue = state_filtered_data.groupby(['issue', 'sub_issue']).size().reset_index(name='Number of Complaints')

    fig = px.treemap(complaints_by_issue_and_sub_issue, path=['issue', 'sub_issue'], values='Number of Complaints', title="Complaints by Issue and Sub-Issue (Treemap)")
    return fig

# create two columns for charts
fig_col1, fig_col2 = st.columns(2,gap='large')


with fig_col1:
        # # Calculate the sum of complaints aggregated by product
        # product_complaints_sum = df.groupby('product').size().reset_index(name='Number of Complaints')

        # # Create a bar chart using Plotly Express
        # fig = px.bar(product_complaints_sum, x='Number of Complaints', y='product', orientation='h')
        # # Streamlit UI
        # st.title("Number of Complaints by Product")
        # st.plotly_chart(fig)

        st.title("Number of Complaints by Product")
        fig = complaints_by_product_chart(df, state_filter)
        st.plotly_chart(fig)

with fig_col2:
     st.title("Complaints by Month and Year")
     fig = complaints_by_month_year_chart(df, state_filter)
     st.plotly_chart(fig)



fig_col3, fig_col4 = st.columns(2,gap='large')

with fig_col3:
    #  complaints_by_submitted_via = df.groupby('submitted_via').size().reset_index(name='Number of Complaints')

    #  fig = px.pie(complaints_by_submitted_via, values='Number of Complaints', names='submitted_via', title="Complaints by Submitted Via")

    #  # Streamlit UI
    #  st.title("Number of Complaints by Submitted Via Channel")

    #  # Show the pie chart
    #  st.plotly_chart(fig)
    st.title("Number of Complaints by Submitted Via Channel")
    fig = complaints_by_submitted_via_chart(df, state_filter)
    st.plotly_chart(fig)

with fig_col4:
        # # Calculate the sum of complaints aggregated by "Issue" and "Sub-Issue"
        # complaints_by_issue_and_sub_issue = df.groupby(['issue', 'sub_issue']).size().reset_index(name='Number of Complaints')

        # # Create a treemap using Plotly Express
        # fig = px.treemap(complaints_by_issue_and_sub_issue, path=['issue', 'sub_issue'], values='Number of Complaints', title="Complaints by Issue and Sub-Issue")

        # # Streamlit UI
        # st.title("Number of Complaints by Issue and Sub-Issue (Treemap)")

        # # Show the treemap
        # st.plotly_chart(fig)
        st.title("Number of Complaints by Issue and Sub-Issue (Treemap)")
        fig = complaints_by_issue_and_sub_issue_chart(df, state_filter)
        st.plotly_chart(fig)


footer_html = """
<footer style="text-align: center;">
    &copy; 2023 Muhammad Ghufran Ashfaq. All rights reserved.
</footer>
"""

# Display the HTML footer using Streamlit's Markdown component
st.markdown(footer_html, unsafe_allow_html=True)

