import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.colors as mcolors

# Load the data from the Excel file
file_path = './1acre.xlsx'
campaign_df = pd.read_excel(file_path, sheet_name='Sheet1 (2)')

# Drop the unnamed column
campaign_df.drop(columns=['Unnamed: 0'], inplace=True)

# Fill missing values
campaign_df['Sales'].fillna(0, inplace=True)
campaign_df['Checkouts'].fillna(0, inplace=True)
campaign_df['Clicks'].fillna(0, inplace=True)
campaign_df['Leads'].fillna(0, inplace=True)
campaign_df['Cost per results'].fillna(campaign_df['Cost per results'].mean(), inplace=True)

# Sidebar for filters
st.sidebar.header('Filters')
campaign_names = campaign_df['Campaign name'].unique()
selected_campaigns = st.sidebar.multiselect('Select Campaigns', campaign_names, campaign_names)

# Filter the dataframe
filtered_df = campaign_df[campaign_df['Campaign name'].isin(selected_campaigns)]

# Summary statistics
total_spent = filtered_df['Amount spent (INR)'].sum()
total_sales = filtered_df['Sales'].sum()
total_leads = filtered_df['Leads'].sum()
total_checkouts = filtered_df['Checkouts'].sum()

# Display summary statistics as tile cards with improved formatting
st.markdown("""
    <style>
        .metric-box {
            border: 2px solid #ccc;
            padding: 10px;
            border-radius: 10px;
            background-color: #f0f0f0;
            text-align: center;
            margin-bottom: 10px;
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
        }
    </style>
""", unsafe_allow_html=True)

st.header('1acre Meta Statistics')
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"<div class='metric-box'>Total Spent (INR)<br>{total_spent:,.2f}</div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-box'>Total Sales<br>{total_sales}</div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='metric-box'>Total Leads<br>{total_leads}</div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"<div class='metric-box'>Total Checkouts<br>{total_checkouts}</div>", unsafe_allow_html=True)

# Interactive scatter plot for campaign data excluding 0 sales campaigns
st.header('Persona Sales Matrix')
non_zero_sales_df = filtered_df[filtered_df['Sales'] > 0]

fig = px.scatter(
    non_zero_sales_df,
    x='Cost per results',
    y='Sales',
    text='Campaign name',
    color='Sales',
    color_continuous_scale='Viridis',
    size_max=20,
    hover_data={
        'Campaign name': True,
        'Cost per results': ':.2f',
        'Sales': True,
    }
)

fig.update_traces(
    marker=dict(size=15, line=dict(width=2, color='DarkSlateGrey')),
    selector=dict(mode='markers+text')
)
fig.update_layout(
    title='Cost per Result vs. Number of Sales',
    xaxis_title='Cost per Result (INR)',
    yaxis_title='Number of Sales',
    height=700,  # Increase the height for better visibility
    margin=dict(l=40, r=40, b=40, t=40),  # Adjust margins for more space
    font=dict(size=14, family='Arial')
)

st.plotly_chart(fig)

# Display sales split by campaign, excluding those with 0 sales
st.header('Sales by Campaign')
sales_by_campaign = non_zero_sales_df.groupby('Campaign name')['Sales'].sum().sort_values(ascending=False)

# Create a bar chart with adjusted Y-axis and data labels
fig_bar = go.Figure(data=[
    go.Bar(
        x=sales_by_campaign.index,
        y=sales_by_campaign.values,
        text=sales_by_campaign.values,
        textposition='outside',
        marker=dict(color='skyblue')
    )
])

fig_bar.update_layout(
    yaxis=dict(range=[0, max(sales_by_campaign.values) + 15]),  # Adjust the range for more Y-axis space
    title='Sales by Campaign',
    xaxis_title='Campaign Name',
    yaxis_title='Number of Sales',
    font=dict(size=14, family='Arial'),
    height=600,  # Increase height for better visibility
    margin=dict(l=40, r=40, b=40, t=40)
)

st.plotly_chart(fig_bar)

# Filter campaigns with 0 sales and non-sales campaigns
zero_sales_df = filtered_df[(filtered_df['Sales'] == 0) & (filtered_df['Leads'] == 0) & (filtered_df['Checkouts'] == 0)]
zero_sales_df = zero_sales_df[['Campaign name', 'Amount spent (INR)']]

# Display table for campaigns with 0 sales
st.header('Campaigns with 0 Sales')

# Define font color based on amount spent
def get_font_color(spent):
    if spent < 5000:
        return 'green'
    elif 5000 <= spent <= 20000:
        return 'yellow'
    else:
        return 'red'

zero_sales_df['Font Color'] = zero_sales_df['Amount spent (INR)'].apply(get_font_color)

# Generate the table with colored text
fig = go.Figure(data=[go.Table(
    header=dict(values=['Campaign Name', 'Total Spent (INR)'],
                fill_color='darkslategray',
                align='left',
                font=dict(color='white', size=14)),
    cells=dict(values=[zero_sales_df['Campaign name'], zero_sales_df['Amount spent (INR)']],
               fill=dict(color=['black']),
               align='left',
               font=dict(color=['white', zero_sales_df['Font Color']]))
)])

st.plotly_chart(fig)

# Cost analysis of all campaigns
st.header('Cost Analysis of All Campaigns')

# Create a table with campaign names, total spent, and cost per result
cost_analysis_df = filtered_df[['Campaign name', 'Amount spent (INR)', 'Cost per results', 'Sales', 'Leads', 'Checkouts']]

# Display the table
st.dataframe(cost_analysis_df)

# Create a bar chart to visualize the total amount spent per campaign
fig_cost_bar = go.Figure(data=[
    go.Bar(
        x=cost_analysis_df['Campaign name'],
        y=cost_analysis_df['Amount spent (INR)'],
        text=cost_analysis_df['Amount spent (INR)'],
        textposition='outside',
        marker=dict(color='coral')
    )
])

fig_cost_bar.update_layout(
    title='Total Amount Spent by Campaign',
    xaxis_title='Campaign Name',
    yaxis_title='Amount Spent (INR)',
    font=dict(size=14, family='Arial'),
    height=600,  # Increase height for better visibility
    margin=dict(l=40, r=40, b=40, t=40)
)

st.plotly_chart(fig_cost_bar)
