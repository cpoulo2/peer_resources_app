import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Page config
st.set_page_config(page_title='Explore your district\'s resource needs', layout='wide')

# Load in app data

# Load data
@st.cache_data
def load_data():
    """Load the PEER app CSV"""
    try:
        df = pd.read_csv(r"app_data.csv.gz")
        return df
    except FileNotFoundError:
        st.error("Data file not found. Please ensure the CSV file is in the correct location.")
        return None

# Load the data
df = load_data()

st.markdown("""
<style>
   .header-title {
      font-size: 24px !important;
      text-align: center !important;
      font-weight: bold !important;
      vertical-align: middle !important;
      margin-bottom: 30px !important;    
      padding: 0
   }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="header-title">Select a district to look at school resources</h1>', unsafe_allow_html=True)

# Only show the sidebar if data loaded successfully
if df is not None:
    
    # Get unique districts and set default to "Statewide"
    districts = df['District Name (IRC)'].unique()
    default_index = 0
    if "Statewide" in districts:
        default_index = list(districts).index("Statewide")
    
    a = st.selectbox('Choose a district:', districts, index=default_index, help= "Select your district using the drop down or typing in the name.")

    df_filtered = df[df['District Name (IRC)'] == a]

# Adequacy level

adequacy_level = df_filtered["Adequacy Level"].unique()[0]

st.markdown("""
<style>
   .adequacy-level {
      font-size: 24px !important;
      text-align: center !important;
      font-weight: bold !important;
      vertical-align: middle !important; 
      margin: 20px 0 !important;
   }
</style>
""", unsafe_allow_html=True)

if a == "Statewide":
    st.markdown(f'<h2 class="adequacy-level"><span style="font-size: 32px; font-weight: bold; color: #FF0000;">Illinois school districts</span> have <span style="font-size: 32px; font-weight: bold; color: #FF0000;">{adequacy_level * 100:.0f}%</span> of the state and local funding needed to be adequately funded.</h2>', unsafe_allow_html=True)
elif adequacy_level <= 1:
   st.markdown(f'<h2 class="adequacy-level"><span style="font-size: 32px; font-weight: bold; color: #FF0000;">{a}</span> has <span style="font-size: 32px; font-weight: bold; color: #FF0000;">{adequacy_level * 100:.0f}%</span> of the state and local funding needed to be adequately funded.</h2>', unsafe_allow_html=True)
else:
   st.markdown(f'<h2 class="adequacy-level"><span style="font-size: 32px; font-weight: bold; color: #008000;">{a}</span> has <span style="font-size: 32px; font-weight: bold; color: #008000;">{adequacy_level * 100:.0f}%</span> of the state and local funding needed to be adequately funded.</h2>', unsafe_allow_html=True)

st.markdown("""
<style>
   .adequacy-explained {
      font-size: 12px !important;
      text-align: center !important;
      vertical-align: middle !important;
      margin-bottom: 30px !important; 
      font-style: italic !important;
   }
</style>
""", unsafe_allow_html=True)

st.markdown('<h2 class="adequacy-explained">[SHORTEN TEXT] Adequate funding is the total cost of resources necessary to educate students, this includes things like teachers, support staff, computer equipment, and professional development to improve teaching. This number is calculated by Illinois\' K-12 Evidence-Based Funding Formula.</h2>',unsafe_allow_html=True)

st.markdown("""
<style>
   .adequacy-explained-a {
      font-size: 24px !important;
      text-align: center !important;
      font-weight: bold !important;
      vertical-align: middle !important;    
      padding: 0
   }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="adequacy-explained-a">The<br>💰 Dollars and cents 🪙<br>of adequate funding</h1>', unsafe_allow_html=True)

# Adequacy target and gap 

# Create animated bar chart comparing actual vs adequate resources
if 'df_filtered' in locals() and not df_filtered.empty:
    # First filter by the first resource type
    resource_filter = df_filtered["Resource"].unique()[0]
    df_resource = df_filtered[df_filtered["Resource"] == resource_filter]
    
    # Get the financial data for the chart
    actual_resources = df_resource["Actual"].iloc[0]
    adequate_resources = df_resource["Adequate resources"].iloc[0]
    
    # Create data for the bar chart
    chart_data = pd.DataFrame({
        'Category': ['Actual Resources', 'Adequate Resources'],
        'Amount': [actual_resources, adequate_resources],
        'Color': ['#FF6B6B', '#4CAF50']  # Red for actual, green for adequate
    })
    
    # Create the animated bar chart using Plotly
    fig = px.bar(
        chart_data, 
        x='Category', 
        y='Amount',
        color='Category',
        color_discrete_map={'Actual Resources': '#FF6B6B', 'Adequate Resources': '#4CAF50'},
        labels={'Amount': 'Dollars ($)', 'Category': ''},
        text='Amount'
    )
    
    # Format the chart
    fig.update_traces(
        texttemplate='$%{text:,.0f}',
        textposition='outside'
    )
    
    fig.update_layout(
        showlegend=False,
        title_x=0.5,  # Center the title
        title_font_size=20,
        xaxis_title="",
        yaxis_title="Funding Amount ($)",
        yaxis=dict(tickformat='$,.0f'),
        height=500
    )
    
    # Add animation effect by updating the layout
    fig.update_layout(
        transition_duration=1000,
        transition_easing="cubic-in-out"
    )

    # Add CSS for metrics styling
    st.markdown("""
    <style>
       .adequacy-dollars-title {
          color: #FF0000 !important;
          text-align: center !important;
          font-size: 18px !important;
          margin-bottom: 5px !important;
       }
       .adequacy-dollars-amount {
          color: #333 !important;
          text-align: center !important;
          font-size: 32px !important;
          font-weight: bold !important;
          margin-top: 0 !important;
       }
    </style>
    """, unsafe_allow_html=True)

    # Add some metrics below the chart
    col1, col2, col3 = st.columns(3)

    with col1:
      st.markdown('<h3 class="adequacy-dollars-title">Adequate Funding</h3>', unsafe_allow_html=True)
      st.markdown(f'<h2 class="adequacy-dollars-amount">${adequate_resources:,.0f}</h2>', unsafe_allow_html=True)

    with col2:
      st.markdown('<h3 class="adequacy-dollars-title">Current Funding</h3>', unsafe_allow_html=True)
      st.markdown(f'<h2 class="adequacy-dollars-amount">${actual_resources:,.0f}</h2>', unsafe_allow_html=True)
    with col3:
        gap = adequate_resources - actual_resources
        st.markdown('<h3 class="adequacy-dollars-title">Funding Gap</h3>', unsafe_allow_html=True)
        st.markdown(f'<h2 class="adequacy-dollars-amount">${gap:,.0f}</h2>', unsafe_allow_html=True)

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

st.text("Add a expandable container to show what that means in terms of particular resources per school")

st.text("Add another expandable box to show current local resources.")

st.text("Add a dropdown to show demographics of the district")




