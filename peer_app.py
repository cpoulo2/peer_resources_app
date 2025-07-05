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
    """Load the PEER app parquet file"""
    try:
        df = pd.read_parquet(r"app_data_wide.parquet")
        return df
    except FileNotFoundError:
        st.error("Data file not found. Please ensure the parquet file is in the correct location.")
        return None
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Load the data
df = load_data()

@st.cache_data
def process_filtered_data(district_name):
    """Cache filtered data processing"""
    df_filtered = df[df['District Name (IRC)'] == district_name]
    return df_filtered

@st.cache_data  
def calculate_funding_metrics(df_filtered):
    
    # Adequacy and actuals melt
    
    df_adequacy = pd.melt(
        df_filtered,
        id_vars=["RCDTS","District Name (IRC)","Total ASE"],  # ✅ Total ASE is here
        value_vars=[
            "Adequacy Target",
            "Adequacy Target Per Student",
            "Adequate Core and Specialist Teachers",
            "Adequate Special Education Teachers",
            "Adequate Counselors",
            "Adequate Nurses",
            "Adequate Psychologists",
            "Adequate Principals",
            "Adequate Assistant Principals",
            "Adequate EL Teachers"
            ],
            var_name="Resource",
            value_name="Adequate resources"
            )
    df_adequacy["Resource"] = df_adequacy["Resource"].str.replace("Adequate ", "", regex=False)
    df_adequacy["Resource"] = df_adequacy["Resource"].str.replace("Adequacy Target", "Total Resources (Dollar Amount)", regex=False)
    df_adequacy["Resource"] = df_adequacy["Resource"].str.replace("Adequate Target Per Student", "Total Resources Per Student (Dollar Amount)", regex=False)
    
    df_actual = pd.melt(
        df_filtered,
        id_vars=["RCDTS", "Total ASE"],  # ✅ ADD Total ASE here
        value_vars=[
            "Actual Resources",
            "Actual Core and Specialist Teachers Count (EIS)",
            "Actual Special Education Teachers Count (EIS)",
            "Actual Counselors Count (IRC)",
            "Actual Nurses Count (IRC)",
            "Actual Psychologists Count (IRC)",
            "Actual Principals Count (EIS)",
            "Actual Assistant Principals Count (EIS)",
            "Actual EL Teachers (EIS)"
        ],
        var_name="Resource",
        value_name="Actual"
        )
    df_actual["Resource"] = df_actual["Resource"].str.replace("Actual ", "", regex=False)
    df_actual["Resource"] = df_actual["Resource"].str.replace(" Count (EIS)", "", regex=False)
    df_actual["Resource"] = df_actual["Resource"].str.replace(" (EIS)", "", regex=False)
    df_actual["Resource"] = df_actual["Resource"].str.replace(" Count (IRC)", "", regex=False)
    df_actual["Resource"] = df_actual["Resource"].str.replace("Resources", "Total Resources (Dollar Amount)", regex=False)
    df_actual["Resource"] = df_actual["Resource"].str.replace("Resources Per Student", "Total Resources Per Student (Dollar Amount)", regex=False)
    
    df_gaps = pd.melt(
        df_filtered,
        id_vars=["RCDTS", "Total ASE"],  # ✅ ADD Total ASE here
        value_vars=[
             "Adequacy Funding Gap",
            "Adequacy Funding Gap Per Student",
            "Core and Specialist Teachers Gap (EIS)",
            "Special Education Teachers Gap (EIS)",
            "Counselors Gap (IRC)",
            "Nurses Gap (IRC)",
            "Psychologists Gap (IRC)",
            "Principals Gap (EIS)",
            "Assistant Principals Gap (EIS)",
            "EL Teachers Gap (EIS)"
        ],
        var_name="Resource",
        value_name="Gaps"
        )
    df_gaps["Resource"] = df_gaps["Resource"].str.replace("Adequacy Funding Gap", "Total Resources (Dollar Amount)", regex=False)
    df_gaps["Resource"] = df_gaps["Resource"].str.replace("Adequacy Funding Gap Per Student", "Total Resources Per Student (Dollar Amount)", regex=False)
    df_gaps["Resource"] = df_gaps["Resource"].str.replace(" Gap (EIS)", "", regex=False)
    df_gaps["Resource"] = df_gaps["Resource"].str.replace(" Gap (IRC)", "", regex=False)
    
    df_gaps_perschool = pd.melt(
        df_filtered,
        id_vars=["RCDTS", "Total ASE"],  # ✅ ADD Total ASE here
        value_vars=[
             "Adequacy Funding Gap Per School",
            "Core and Specialist Teachers Gap Per School",
            "Special Education Teachers Gap Per School",
            "Counselors Gap Per School",
            "Nurses Gap Per School",
            "Psychologists Gap Per School",
            "Principals Gap Per School",
            "Assistant Principals Gap Per School",
            "EL Teachers Gap Per School"
        ],
        var_name="Resource",
        value_name="Gaps Per School"
        )
    df_gaps_perschool["Resource"] = df_gaps_perschool["Resource"].str.replace(" Gap Per School", "", regex=False)

    # Update merge keys to include Total ASE
    df_merged = pd.merge(
        df_adequacy,
        df_actual,
        on=["RCDTS", "Resource", "Total ASE"],  # ✅ ADD Total ASE to merge
        how="left"
    )

    df_merged = pd.merge(
        df_merged,
        df_gaps,
        on=["RCDTS", "Resource", "Total ASE"],  # ✅ ADD Total ASE to merge
        how="left"
    )

    df_merged = pd.merge(
        df_merged,
        df_gaps_perschool,
        on=["RCDTS", "Resource", "Total ASE"],  # ✅ ADD Total ASE to merge
        how="left"
    )

    df_demographics = pd.melt(
    df_filtered,
    id_vars=["RCDTS", "District Name (IRC)", "Total ASE"],
    value_vars=[
        "White (%)", "Black (%)", "Latine (%)", "Asian (%)",
        "Native Hawaiian or Other Pacific Islander (%)",
        "American Indian or Alaska Native (%)","IEP (%)", "EL (%)", "Low Income (%)"
    ],
    var_name="Demographic Group",
    value_name="Demographic Percentages"
    )

    df_demographics["Demographic Group"] = df_demographics["Demographic Group"].str.replace(" (%)", "", regex=False)

    # Revenue melt
    df_revenue = pd.melt(
        df_filtered,
        id_vars=["RCDTS"],
        value_vars=[
             "Local Property Taxes (%)", "Other Local Funding (%)", 
            "Evidence-Based Funding (%)", "Other State Funding (%)", 
            "Federal Funding (%)"
        ],
        var_name="Revenue Source",
        value_name="Revenue Percentages"
        )
    
    df_revenue["Revenue Source"] = df_revenue["Revenue Source"].str.replace(" (%)", "", regex=False)

    """Cache funding calculations"""
    resource_filter = "Total Resources (Dollar Amount)"
    df_resource = df_merged[df_merged["Resource"] == resource_filter]
    # Get the actual and adequate resources
    actual_resources = df_resource["Actual"].iloc[0]
    adequate_resources = df_resource["Adequate resources"].iloc[0]
    ase = df_resource["Total ASE"].iloc[0]
    
    return actual_resources, adequate_resources, ase, df_merged, df_demographics, df_revenue

# Move this to the top, after loading data
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
   .adequacy-level {
      font-size: 24px !important;
      text-align: center !important;
      font-weight: bold !important;
      vertical-align: middle !important; 
      margin: 20px 0 !important;
   }
   .adequacy-explained {
      font-size: 18px !important;
      text-align: center !important;
      vertical-align: middle !important;
      margin-bottom: 30px !important; 
      font-style: italic !important;
   }
   .adequacy-explained-a {
      font-size: 24px !important;
      text-align: center !important;
      font-weight: bold !important;
      vertical-align: middle !important;    
      padding: 0
   }
   .adequacy-dollars-title {
      color: #333 !important;
      text-align: center !important;
      font-size: 18px !important;
   }
   .adequacy-dollars-amount {
      color: #333 !important;
      text-align: center !important;
      font-size: 32px !important;
      font-weight: bold !important;
      margin-bottom: 5px !important;
   }
   .gap-positive {
      color: #FF0000 !important;
      text-align: center !important;
      font-size: 32px !important;
      font-weight: bold !important;
      margin-bottom: 5px !important;
   }        
   .gap-negative {
      color: #008000 !important;
      text-align: center !important;
      font-size: 32px !important;
      font-weight: bold !important;
      margin-bottom: 5px !important;
   }
   .stButton {
      display: flex !important;
      justify-content: center !important;
   }
   .stButton > button {
      margin-bottom: 20px !important;
   }   
</style>
""", unsafe_allow_html=True)

# Add per pupil button to toggle between total and per pupil funding
# Initialize session state for button toggle
if 'show_per_pupil' not in st.session_state:
    st.session_state.show_per_pupil = False

st.markdown('<h1 class="header-title">Select a district to look at school resources</h1>', unsafe_allow_html=True)

# Only show the sidebar if data loaded successfully
if df is not None:
    
   # Get unique districts and set default to "Statewide"
   districts = df['District Name (IRC)'].unique()
   default_index = 0
   if "Statewide" in districts:
       default_index = list(districts).index("Statewide")
    
   a = st.selectbox('Choose a district:', districts, index=default_index, help= "Select your district using the drop down or typing in the name.")

   # Use cached function instead of direct filtering
   df_filtered = process_filtered_data(a)

# Adequacy level

adequacy_level = df_filtered["Adequacy Level"].unique()[0]

if a == "Statewide":
    st.markdown(f'<h2 class="adequacy-level"><span style="font-size: 32px; font-weight: bold; color: #FF0000;">Illinois school districts</span> have <span style="font-size: 32px; font-weight: bold; color: #FF0000;">{adequacy_level * 100:.0f}%</span> of the state and local funding needed to be adequately funded.</h2>', unsafe_allow_html=True)
elif adequacy_level <= 1:
   st.markdown(f'<h2 class="adequacy-level"><span style="font-size: 32px; font-weight: bold; color: #FF0000;">{a}</span> has <span style="font-size: 32px; font-weight: bold; color: #FF0000;">{adequacy_level * 100:.0f}%</span> of the state and local funding needed to be adequately funded.</h2>', unsafe_allow_html=True)
else:
   st.markdown(f'<h2 class="adequacy-level"><span style="font-size: 32px; font-weight: bold; color: #008000;">{a}</span> has <span style="font-size: 32px; font-weight: bold; color: #008000;">{adequacy_level * 100:.0f}%</span> of the state and local funding needed to be adequately funded.</h2>', unsafe_allow_html=True)

st.markdown('<h2 class="adequacy-explained">[SHORTEN TEXT/ADD PHONE SPECIFIC CHANGE] Adequate funding is the total cost of resources necessary to educate students, this includes things like teachers, support staff, computer equipment, and professional development to improve teaching. This number is calculated by Illinois\' K-12 Evidence-Based Funding Formula.</h2>',unsafe_allow_html=True)

st.markdown('<h1 class="adequacy-explained-a">💰 The Dollars and cents of adequate funding 🪙</h1>', unsafe_allow_html=True)

# Adequacy target and gap 

# Create animated bar chart comparing actual vs adequate resources
if 'df_filtered' in locals() and not df_filtered.empty:
   # First filter by the value "Total Resources (Dollar Amount)"

   actual_resources, adequate_resources, ase, df_merged, df_demographics, df_revenue = calculate_funding_metrics(df_filtered)
   # Calculate per pupil values
   actual_per_pupil = actual_resources / ase if ase > 0 else 0
   adequate_per_pupil = adequate_resources / ase if ase > 0 else 0
   gap_per_pupil = adequate_per_pupil - actual_per_pupil

   # Determine which values to display based on button state
   if st.session_state.show_per_pupil:
      display_adequate = adequate_per_pupil
      display_actual = actual_per_pupil
      display_gap = gap_per_pupil
      currency_format = "${:,.0f}"
      chart_title_suffix = " (Per Pupil)"
   else:
      display_adequate = adequate_resources
      display_actual = actual_resources
      display_gap = adequate_resources - actual_resources
      currency_format = "${:,.0f}"
      chart_title_suffix = ""

   # Update the metrics with dynamic values - Create 5 columns to add + signs
   col1, plus1, col2, plus2, col3 = st.columns([3, 0.5, 3, 0.5, 3])

   with col1:
       title_text = "Adequate Funding" + (" Per Pupil" if st.session_state.show_per_pupil else "")
       st.markdown(f'<h3 class="adequacy-dollars-title">{title_text}</h3>', unsafe_allow_html=True)
       st.markdown(f'<h2 class="adequacy-dollars-amount">${display_adequate:,.0f}</h2>', unsafe_allow_html=True)

   with plus1:
       # Add some vertical spacing to align with the dollar amounts
       st.markdown('<div style="height: 25px;"></div>', unsafe_allow_html=True)  # Space for title
       st.markdown('<h2 style="text-align: center; color: #FF0000; font-size: 64px; font-weight: bold;">-</h2>', unsafe_allow_html=True)

   with col2:
       title_text = "Current Funding" + (" Per Pupil" if st.session_state.show_per_pupil else "")
       st.markdown(f'<h3 class="adequacy-dollars-title">{title_text}</h3>', unsafe_allow_html=True)
       st.markdown(f'<h2 class="adequacy-dollars-amount">${display_actual:,.0f}</h2>', unsafe_allow_html=True)

   with plus2:
       # Add some vertical spacing to align with the dollar amounts
       st.markdown('<div style="height: 25px;"></div>', unsafe_allow_html=True)  # Space for title
       st.markdown('<h2 style="text-align: center; color: #FF0000; font-size: 64px; font-weight: bold;">=</h2>', unsafe_allow_html=True)

   # Col 3
   with col3:
      title_text = "Funding Gap" + (" Per Pupil" if st.session_state.show_per_pupil else "")
       
      # Determine CSS class based on gap value
      gap_class = "gap-positive" if display_gap > 0 else "gap-negative"
       
      st.markdown(f'<h3 class="adequacy-dollars-title">{title_text}</h3>', unsafe_allow_html=True)
      st.markdown(f'<h2 class="{gap_class}">${display_gap:,.0f}</h2>', unsafe_allow_html=True)

   # Center the button using columns (most reliable)
   _, center_col, _ = st.columns([1, 1, 1])
   
   with center_col:
      button_text = "🏫 View Total Funding" if st.session_state.show_per_pupil else "👩‍🎓 View Per Pupil Funding"
      if st.button(button_text, key="funding_toggle_button"):
          st.session_state.show_per_pupil = not st.session_state.show_per_pupil
          st.rerun()


   # Update the chart data
   chart_data = pd.DataFrame({
       'Category': ['Actual Resources', 'Adequate Resources'],
       'Amount': [display_actual, display_adequate],
       'Color': ['#FF6B6B', '#4CAF50']
   })

   # Create the animated bar chart with updated data
   fig = px.bar(
       chart_data, 
       x='Category', 
       y='Amount',
       color='Category',
       color_discrete_map={'Actual Resources': '#FF6B6B', 'Adequate Resources': '#4CAF50'},
       labels={'Amount': f'Dollars ($){chart_title_suffix}', 'Category': ''},
       text='Amount',
       title=f"Funding Comparison{chart_title_suffix}"
   )
   # Format the chart (keep existing formatting code)
   fig.update_traces(
       texttemplate='$%{text:,.0f}',
       textposition='outside'
   )

   fig.update_layout(
       showlegend=False,
       title_x=0.5,
       title_font_size=20,
       xaxis_title="",
       yaxis_title=f"Funding Amount ($){chart_title_suffix}",
       yaxis=dict(tickformat='$,.0f'),
       height=400,
       transition_duration=500,
       transition_easing="cubic-in-out"
   )

   #st.plotly_chart(fig, use_container_width=True)

# Create an expandable container to show adequacy gaps in terms of positions per school
with st.expander("Adequacy Gaps by Position"):
   
   # Create a drop down menue that filters by resource types:
   resource_filter = st.selectbox("Select Resource Type", options=[
       "Core and Specialist Teachers",
       "Special Education Teachers",
       "Counselors",
       "Nurses",
       "Psychologists",
       "Principals",
       "Assistant Principals",
       "EL Teachers"
   ])   
   
   # Filter the dataframe based on the selected resource type

   df_resource = df_merged[df_merged["Resource"] == resource_filter]

   # Get the adequacy gap per school for the selected resource type

   adequacy_gap_per_school = df_resource["Gaps Per School"].iloc[0] if not df_resource.empty else 0
   
   st.text(f"This is the {resource_filter} and this is the adequacy gap per school: {adequacy_gap_per_school:.2f} positions per school.") 

with st.expander("Revenue by source"):
    
    # Create a bar chart for revenue sources
   fig_rev = px.bar(
      df_revenue, 
      x='Revenue Source', 
      y='Revenue Percentages',
      color='Revenue Source',
      color_discrete_sequence=px.colors.qualitative.Pastel,
      labels={'Revenue Percentages': 'Percent of Total Revenue (%)', 'Revenue Source': ''},
      text='Revenue Percentages',
      title="Revenue Sources"
   )
      # Format the chart
   fig_rev.update_traces(
      # Format the text labels to show percentages
      texttemplate='%{text:.0%}',
      textposition='outside'
   )
   fig_rev.update_layout(
      showlegend=False,
      title_x=0.5,
      title_font_size=20,
      xaxis_title="",
      yaxis_title="Percent of Total Revenue (%)",
      yaxis=dict(tickformat='.0f'),
      height=400,        
      transition_duration=500,
      transition_easing="cubic-in-out"
   )
   st.plotly_chart(fig_rev, use_container_width=True)
    
with st.expander("Demographics"):
   
   # Create a bar chart for demographics
   fig_demo = px.bar(
       df_demographics, 
       x='Demographic Group', 
       y='Demographic Percentages',
       color='Demographic Group',
       color_discrete_sequence=px.colors.qualitative.Pastel,
       labels={'Demographic Percentages': 'Percentage of Students (%)', 'Demographic Group': ''},
       text='Demographic Percentages',
       title="Student Demographics"
   )
    
   # Format the chart
   fig_demo.update_traces(
       texttemplate='%{text:.0%}',
       textposition='outside'
   )
   
   fig_demo.update_layout(
       showlegend=False,
       title_x=0.5,
       title_font_size=20,
       xaxis_title="",
       yaxis_title="Percentage of Students (%)",
       yaxis=dict(tickformat='.0%'),
       height=500,
       transition_duration=1000,
       transition_easing="cubic-in-out"
   )
   
   st.plotly_chart(fig_demo, use_container_width=True)




