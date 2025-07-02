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

# Add per pupil button to toggle between total and per pupil funding
# Initialize session state for button toggle
if 'show_per_pupil' not in st.session_state:
    st.session_state.show_per_pupil = False

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
      font-size: 18px !important;
      text-align: center !important;
      vertical-align: middle !important;
      margin-bottom: 30px !important; 
      font-style: italic !important;
   }
</style>
""", unsafe_allow_html=True)

st.markdown('<h2 class="adequacy-explained">[SHORTEN TEXT/ADD PHONE SPECIFIC CHANGE] Adequate funding is the total cost of resources necessary to educate students, this includes things like teachers, support staff, computer equipment, and professional development to improve teaching. This number is calculated by Illinois\' K-12 Evidence-Based Funding Formula.</h2>',unsafe_allow_html=True)

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

st.markdown('<h1 class="adequacy-explained-a">💰 The Dollars and cents of adequate funding 🪙</h1>', unsafe_allow_html=True)

# Adequacy target and gap 

# Create animated bar chart comparing actual vs adequate resources
if 'df_filtered' in locals() and not df_filtered.empty:
   # First filter by the value "Total Resources (Dollar Amount)"
   resource_filter = "Total Resources (Dollar Amount)"
   df_resource = df_filtered[df_filtered["Resource"] == resource_filter]
    
   # Get the financial data for the chart
   actual_resources = df_resource["Actual"].iloc[0]
   adequate_resources = df_resource["Adequate resources"].iloc[0]

   # Get ASE to create per pupil counts
   ase = df_resource["Total ASE"].iloc[0]
   
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
# CSS styles for the columns
   st.markdown("""
   <style>
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
         margin-bottom: 0px !important;
      }
   </style>
   """, unsafe_allow_html=True)


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

# CSS styles for the columns
   st.markdown("""
   <style>
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
       height=500,
       transition_duration=1000,
       transition_easing="cubic-in-out"
   )

   #st.plotly_chart(fig, use_container_width=True)

    # Display the chart spanning col1 and col2
#   col1_col2 = st.columns([2, 1])  # 2/3 width for chart, 1/3 for gap column
#   with col1_col2[0]:
#     st.plotly_chart(fig, use_container_width=True)

   # Add per pupil button to change the chart.
   # If clicked the data for the chart and adequacy-dollars will use per pupil values
   # The button will then display View Total Funding

# Create an expandable container to show adequacy gaps in terms of positions per school
with st.expander("Adequacy Gaps by Position"):
    st.text("Add a expandable container to show what that means in terms of particular resources per school")

st.text("Add another expandable box to show current local resources.")

with st.expander("Revenue by source"):
    st.text("Add a expandable container to show what that means in terms of particular resources per school")

st.text("Add a dropdown to show demographics of the district")

with st.expander("Demographics"):
    st.text("Add a expandable container to show what that means in terms of particular resources per school")




