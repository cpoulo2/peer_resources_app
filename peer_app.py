import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Page config
st.set_page_config(page_title='How under resourced is your district', layout='wide')

# Generate data
#np.random.seed(42)
#df = pd.DataFrame({
#    'Date': pd.date_range('2024-01-01', periods=100),
#    'Sales': np.random.randint(500, 2000, size=100),
#    'Region': np.random.choice(['North', 'South', 'East', 'West'], size=100),
#    'Product': np.random.choice(['Product A', 'Product B', 'Product C'], size=100)
#})

# Header
st.header("BABIES!!!!")

# Add CSS styling for headers
st.markdown("""
<style>
   .top-title-title {
      font-size: 12px !important;
      text-align: center !important;
      color: #4CAF50 !important; /* Green color */
      font-weight: bold !important;
      margin: 0 !important;
   }
</style>
""", unsafe_allow_html=True)

# Create expander separately
with st.expander("Clicky clicky"):
    st.markdown('<h1 class="top-title-title">STUFF</h1>', unsafe_allow_html=True)
    st.write("More content here")
    st.button("A button inside the expander", key="header_button")

# Sidebar filters
st.sidebar.title('Filters')

a = st.sidebar.radio('Choose:',[1,2], help= "Select your district using the drop down or typing in the name.")

#regions = st.sidebar.multiselect('Select Region', df['Region'].unique(), default=df['Region'].unique())
#products = st.sidebar.multiselect('Select Product', df['Product'].unique(), default=df['Product'].unique())

# Filter data
#filtered_df = df[(df['Region'].isin(regions)) & (df['Product'].isin(products))]

# Metrics
col1, col2, col3 = st.columns(3)

# Add CSS that targets a specific class
col1.markdown("""
<style>
   .custom-text {
      font-size: 24px;
      text-align: left;
      color: #4CAF50; /* Green color */
      font-weight: bold;
   }
</style>
""", unsafe_allow_html=True)

# Use the custom class in your content
col1.markdown('<p class="custom-text">Crampus is hEr3??</p>', unsafe_allow_html=True)
col2.title("COlumn 2",help='This column will show you X,Y,Z')
col2.write("what is the difference between title and write?")

# Add CSS for title styling

col3.markdown("""
<style>
   h2.custom-title {
      font-size: 12px !important;
      text-align: center !important;
      color: #0000FF !important; /* Red color */
      font-weight: bold !important;
      margin-bottom: 10px !important;
   }
</style>
""", unsafe_allow_html=True)


col3.markdown("""
<style>
   h1.custom-title {
      font-size: 32px !important;
      text-align: center !important;
      color: #FF6B6B !important; /* Red color */
      font-weight: bold !important;
      margin-bottom: 10px !important;
   }
</style>
""", unsafe_allow_html=True)

# Use h1 tag for title (equivalent to st.title())
col3.markdown('<h1 class="custom-title">Col 3 is here</h1>', unsafe_allow_html=True)

# Add an expander/accordion
with col3.expander("Click to expand more details"):
    st.markdown('<h2 class="custom-title">Col 3 iz the bessst</h2>', unsafe_allow_html=True)
    st.write("More content here")
    st.button("A button inside the expander", key="col3_button")
#col1.metric("Total Sales", f"${filtered_df['Sales'].sum():,}")
#col2.metric("Average Sales", f"${filtered_df['Sales'].mean():.0f}")
#col3.metric("Records", len(filtered_df))

# Charts
#col1, col2 = st.columns(2)

#with col1:
#    fig_line = px.line(filtered_df, x='Date', y='Sales', color='Region', title='Sales Over Time')
#   st.plotly_chart(fig_line, use_container_width=True)

#with col2:
#    region_sales = filtered_df.groupby('Region')['Sales'].sum().reset_index()
#    fig_bar = px.bar(region_sales, x='Region', y='Sales', title='Total Sales by Region')
#    st.plotly_chart(fig_bar, use_container_width=True)

# Data table
st.subheader("Filtered Data")
#st.dataframe(filtered_df)

st.markdown("""
<style>
   h3.subhead-title {
      font-size: 12px !important;
      text-align: center !important;
      color: #0000FF !important; /* Red color */
      font-weight: bold !important;
      margin-bottom: 10px !important;
   }
</style>
""", unsafe_allow_html=True)

st.markdown('<h3 class="subhead-title">Subheader here</h1>', unsafe_allow_html=True)