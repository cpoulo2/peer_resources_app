# PEER School district resource inequality app
# Authors: Chris D. Poulos (cdpoulos@gmail.com), Erykah Nava (EMAIL)

import streamlit as st
from PIL import Image
import pandas as pd
import plotly.express as px
import numpy as np
from streamlit_extras.stylable_container import stylable_container


# Page config

st.set_page_config(page_title='🏫 IL school resource ≠ app', layout='wide')

# Read in and cahce data set

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

df = load_data()

@st.cache_data
def process_filtered_data(district_name):
    """Cache filtered data processing"""
    df_filtered = df[df['District Name (IRC)'] == district_name]
    return df_filtered

# Melt data into long format for charts and drop down menus.

@st.cache_data  
def calculate_funding_metrics(df_filtered):
    
    # EBF adequacy
    
    df_adequacy = pd.melt(
        df_filtered,
        id_vars=["RCDTS","District Name (IRC)","Total ASE"],
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
    
    # Actual resources 

    df_actual = pd.melt(
        df_filtered,
        id_vars=["RCDTS", "Total ASE"],
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
    
    # Adequacy gaps

    df_gaps = pd.melt(
        df_filtered,
        id_vars=["RCDTS", "Total ASE"],
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
    
    # Adequacy gaps per school

    df_gaps_perschool = pd.melt(
        df_filtered,
        id_vars=["RCDTS", "Total ASE"],
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

    # Merge adequacy and actuals

    df_merged = pd.merge(
        df_adequacy,
        df_actual,
        on=["RCDTS", "Resource", "Total ASE"],
        how="left"
    )

    # Merge gaps

    df_merged = pd.merge(
        df_merged,
        df_gaps,
        on=["RCDTS", "Resource", "Total ASE"],
        how="left"
    )

    # Merge gaps per school

    df_merged = pd.merge(
        df_merged,
        df_gaps_perschool,
        on=["RCDTS", "Resource", "Total ASE"],
        how="left"
    )

    # Demographics melt

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

    # Demographics column name formatting

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
    
    # Revenue column name formatting

    df_revenue["Revenue Source"] = df_revenue["Revenue Source"].str.replace(" (%)", "", regex=False)

    # Resource filter formatting

    resource_filter = "Total Resources (Dollar Amount)"
    df_resource = df_merged[df_merged["Resource"] == resource_filter]
    
    # Get the actual and adequate resources variables
    
    actual_resources = df_resource["Actual"].iloc[0]
    adequate_resources = df_resource["Adequate resources"].iloc[0]
    ase = df_resource["Total ASE"].iloc[0]
    
    return actual_resources, adequate_resources, ase, df_merged, df_demographics, df_revenue

# HEADER

# Adjusting logo to pop

st.markdown("""
<style>
.st-emotion-cache-7czcpc {
    background: rgba(255,255,255,0.3);
    border-radius: 16px;
    padding: 0px;
}
</style>
""", unsafe_allow_html=True)

# Header container

with stylable_container(
    key="header_container",
    css_styles="""
        {
            background-image: linear-gradient(rgba(182,183,209,0.15), rgba(182,183,209,0.15)), url('https://images.squarespace-cdn.com/content/v1/6205588be5859638b3fe122c/9d618979-ff41-429b-8ccb-a402f583056f/the+group.jpg');
            background-size: cover;
            background-position: center;
            border-radius: 10px;
            margin-bottom: 1.5rem;
            min-height: 220px;
            display: flex;
            align-items: center;
            gap: 40px;
            padding: 30px 40px;
        }
        .stImage img {
            width: 120px !important;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .header-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: white;
        text-shadow: 1px 1px 8px #000;
        text-align: left !important;
        display: block;
        width: 100%;
        margin-left: 0;
        justify-content: flex-start;
        }
    """,
):
    col1,col2 = st.columns([3,7])
    with col1:
        st.image("peer_logo.png")
    with col2:
        st.markdown('<span class="header-title">PEER School Funding Needs Lookup</span>', unsafe_allow_html=True)


# Present adequacy level by district

if df is not None:
    
# Get unique districts and set default to "Statewide"

   districts = df['District Name (IRC)'].unique() # This was a relic from when we used long data. It's superfluous now since data is wide not long but it is functional.
   default_index = 0
   if "Statewide" in districts:
       default_index = list(districts).index("Statewide")


with stylable_container(
    key="select_dist",
    css_styles="""
        {
            background-color: None;
            border-radius: 10px;
            padding: 20px;
            align-items: center;
            text-align: center;
        }

    """,
):
    st.markdown("<h5>Select a district to view resource needs</h5>",unsafe_allow_html=True)

selection = st.selectbox("", districts, index=default_index)
df_filtered = process_filtered_data(selection)

adequacy_level = df_filtered["Adequacy Level"].unique()[0]

# Adequacy level and adequacy gaps CSS

st.markdown("""
<style>

/* ✅ Download fonts, load font weights, enable font fallback */            
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;700&family=Montserrat:wght@400;500&display=swap');
                                             
/* ✅ Specify style for the following classes */                        
.adequacy-level .illinois-text {
    color: #C4384D !important;
    font-weight: 700 !important;
    font-family: 'Poppins', sans-serif !important;
}
            
.adequacy-level .district-negative {
    color: #C4384D !important;
    font-weight: 700 !important;
    font-family: 'Poppins', sans-serif !important;
}
            
.adequacy-level .district-positive {
    color: #20a3bc !important;
    font-weight: 700 !important;
    font-family: 'Poppins', sans-serif !important;
}
                                        
.header-title {
    font-size: 24px !important;
    font-family: Poppins;
    text-align: center !important;
    font-weight:bold;
    vertical-align: middle !important;
    margin-bottom: 30px !important;    
    padding: 0
   }
            

.adequacy-level {
   font-size: 24px !important;
   font-family: Poppins;
   text-align: center !important;
   font-weight: normal;
   vertical-align: middle !important; 
   margin: 20px 0 !important;
}
         
.adequacy-explained {
   font-size: 14px !important;
   font-family: Poppins !important;
   font-weight: normal;
   text-align: center !important;
   vertical-align: middle !important;
   margin-bottom: 30px !important; 
   font-style: italic !important;
}
   
.adequacy-explained-a {
   font-size: 24px !important;
   font-family: Poppins;
   font-weight: normal;
   text-align: center !important;
   vertical-align: middle !important;    
   padding: 0
 }
            
.adequacy-dollars-title {
   text-align: center !important;
   font-size: 18px !important;
  font-family: Poppins;
  font-weight: normal;
}
.adequacy-dollars-amount {
   text-align: center !important;
   font-size: 30px !important;
   font-family: Poppins;
   font-weight:normal;
   margin-bottom: 5px !important;
}
.gap-positive {
   color: #20a3bc !important;
   text-align: center !important;
   font-size: 32px !important;
   font-weight:;
   margin-bottom: 5px !important;
}        
.gap-negative {
   color: #C4384D !important;
   text-align: center !important;
   font-size: 32px !important;
   font-weight:;
   margin-bottom: 5px !important;
}
                               
</style>
""", unsafe_allow_html=True)

with stylable_container(
    key="adequacy_level_container",
    css_styles="""
        {
            background-color: #e0e7ff;
            border-radius: 10px;
            padding: 20px;
            align-items: center;
            text-align: center;
        }
    """,
):
    if selection == "Statewide":
        st.markdown(f'<h2 class="adequacy-level"><span class="illinois-text">Illinois school districts</span> have <span class="illinois-text">{adequacy_level * 100:.0f}%</span> of the state and local funding needed to be adequately funded.</h2>', unsafe_allow_html=True)
    elif adequacy_level <= 1:
        st.markdown(f'<h2 class="adequacy-level"><span class="district-negative">{selection}</span> has <span class="district-negative">{adequacy_level * 100:.0f}%</span> of the state and local funding needed to be adequately funded.</h2>', unsafe_allow_html=True)
    else:
        st.markdown(f'<h2 class="adequacy-level"><span class="district-positive">{selection}</span> has <span class="district-positive">{adequacy_level * 100:.0f}%</span> of the state and local funding needed to be adequately funded.</h2>', unsafe_allow_html=True)
    if st.button("💡 Adequate Funding Explained", key="help_button"):
        st.session_state.show_help = not st.session_state.get('show_help', False)
    if st.session_state.get('show_help', False):
        st.markdown("""
    <div class="adequacy-help-content">
    Adequate funding refers to the total cost of resources necessary to educate students (for example, teachers, support staff, computer equipment, and professional development to improve teaching). This number is calculated by Illinois' K-12 Evidence-Based Funding Formula.
    </div>
    """, unsafe_allow_html=True)

# Data processing and calculations for adequacy funding metrics

if 'df_filtered' in locals() and not df_filtered.empty:
   
   # First filter by the value "Total Resources (Dollar Amount)"

   actual_resources, adequate_resources, ase, df_merged, df_demographics, df_revenue = calculate_funding_metrics(df_filtered)
   
   # Calculate per pupil values
   
   actual_per_pupil = actual_resources / ase if ase > 0 else 0
   adequate_per_pupil = adequate_resources / ase if ase > 0 else 0
   gap_per_pupil = actual_per_pupil - adequate_per_pupil

   # Determine which values to display based on button state (full or per pupil funding)
   if 'show_per_pupil' not in st.session_state:
    st.session_state.show_per_pupil = False

   if st.session_state.show_per_pupil:
      display_adequate = adequate_per_pupil
      display_actual = actual_per_pupil
      display_gap = gap_per_pupil
      currency_format = "${:,.0f}"
      chart_title_suffix = " (Per Pupil)"
   else:
      display_adequate = adequate_resources
      display_actual = actual_resources
      display_gap = actual_resources - adequate_resources
      currency_format = "${:,.0f}"
      chart_title_suffix = ""
    

with stylable_container(
    key="adequacy_dollars",
    css_styles="""
        {
            background-color: #e0e7ff;
            border-radius: 10px;
            padding: 20px;
        }
        .st-emotion-cache-159b5ki {
        align-items: flex-end !important;  /* For flex containers */
        text-align: right !important;      /* For text content */
        }
            h4,h3,h2,h1,p {
                text-align: center !important;
                width: 100%;
                margin-left: auto;
                margin-right: auto;
                display: block;
            }
    """,
):
    if st.session_state.show_per_pupil:
        title_text = "💰 The Dollars and Cents of Adequate Funding Per Pupil 🪙"
    else:
        title_text = "💰 The Dollars and Cents of Adequate Funding 🪙"
    st.markdown(f'<h2 class="adequacy-explained-a">{title_text}</h2>', unsafe_allow_html=True)
    st.markdown("---")
    with stylable_container(
        key="school_funding_needs",
        css_styles="""
            {
                background-color: ghostwhite;
                border-radius: 10px;
                padding: 20px 0 10px 0;
                margin-bottom: 16px;
            }
        """,
    ):
        st.subheader('School Funding Needs:')
        st.markdown("---")
        st.markdown(f'<h2 class="adequacy-dollars-amount">${display_adequate:,.0f}</h2>', unsafe_allow_html=True)
    with stylable_container(
        key="school_funding_resources",
        css_styles="""
            {
                background-color: ghostwhite;
                border-radius: 10px;
                padding: 20px 0 10px 0;
                margin-bottom: 16px;
            }
        """,
    ):
        st.subheader('School Funding Resources:')
        st.markdown('---')
        st.markdown(f'<h2 class="adequacy-dollars-amount">${display_actual:,.0f}</h2>', unsafe_allow_html=True)
    with stylable_container(
        key="school_funding_gap",
        css_styles="""
            {
                background-color: ghostwhite;
                border-radius: 10px;
                padding: 20px 0 10px 0;
                margin-bottom: 16px;
            }
        """,
    ):
    
        gap_class = "gap-positive" if display_gap > 0 else "gap-negative"
        if display_gap < 0:
            st.subheader('School Funding Gap:')
            st.markdown("---")
            st.markdown(f'<h2 class="{gap_class}">${display_gap:,.0f}</h2>', unsafe_allow_html=True)
        else:
            st.subheader('School Funding Surplus:')
            st.markdown("---")
            st.markdown(f'<h2 class="{gap_class}">${display_gap:,.0f}</h2>', unsafe_allow_html=True)
    
    button_text = "🏫 View Total Funding" if st.session_state.show_per_pupil else "👩‍🎓 View Per Pupil Funding"
    if st.button(button_text, key="funding_toggle_button"):
        st.session_state.show_per_pupil = not st.session_state.show_per_pupil
        st.rerun() 

# Expander CSS

st.markdown("""
<style>
/* Center container text */

summary.st-emotion-cache-1rgl4kv.etg4nir3 > span,
summary.st-emotion-cache-1s2g4bx.etg4nir3 > span {
    width: 100% !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    text-align: center !important;
}
            
summary.st-emotion-cache-1rgl4kv.etg4nir3 > span,
summary.st-emotion-cache-1s2g4bx.etg4nir3 > span {
    width: 100% !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    text-align: center !important;
}
            
</style>
""", unsafe_allow_html=True)


with st.expander("👩‍🏫 From Dollars to Desks: Adequate Staffing 👩‍⚕️", expanded=False):
   
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
   adequacy_gap = df_resource["Gaps"].iloc[0] if not df_resource.empty else 0
   resource_type = resource_filter.lower()
   if selection == "Statewide":
        if adequacy_gap >= 0:  # Positive gap (adequately staffed)
            st.text(f"According to the EBF formula, Illinois schools are adequately staffed with {resource_type}, but this may not reflect the on the ground needs at your school.")
        else:  # Negative gap (understaffed)
            st.text(f"A fully funded EBF formula could mean {abs(adequacy_gap):,.0f} more {resource_type} in Illinois.")
   else:  # Specific district selected
       if adequacy_gap_per_school >= 0:  # Positive gap (adequately staffed)
            st.text(f"According to the EBF formula, your school district is adequately staffed with {resource_type}, but this may not reflect the on the ground needs at your school.")
       else:  # Negative gap (understaffed)
            st.text(f"A fully funded EBF formula could mean {abs(adequacy_gap_per_school):.2f} more {resource_type} per school in your district.")

# Expandable container for revenue sources

with st.expander("Revenue by source"):
    
    # Create a bar chart for revenue sources
   fig_rev = px.bar(
      df_revenue, 
      x='Revenue Source', 
      y='Revenue Percentages',
      color='Revenue Source',
      color_discrete_sequence=px.colors.qualitative.Pastel,
      labels={'Revenue Percentages': 'Percent of Total Revenue (%)', 'Revenue Source': ''},
      text='Revenue Percentages'
   )
      # Format the chart

   fig_rev.update_traces(
      
      # Format the text labels to show percentages

      texttemplate='%{text:.0%}',
      textposition='outside',
      hovertemplate=None,
      hoverinfo='skip'
   )

   # Calculate the max value to set y-axis range

   max_revenue = df_revenue['Revenue Percentages'].max()
   y_rev_max = max_revenue * 1.1  # 10% higher than max value

   fig_rev.update_layout(
      title="",
      showlegend=False,
      xaxis_title="",
      yaxis_title="Percent of Total Revenue (%)",
      height=400,
      margin=dict(t=80),
      transition_duration=500,
      transition_easing="cubic-in-out",
      plot_bgcolor='white',
      paper_bgcolor='white',
      font=dict(color='#141554'),
      xaxis=dict(
          tickfont=dict(color='#141554', size=12),
          color='#141554'
      ),
      yaxis=dict(
          tickformat='.0%',
          range=[0,y_rev_max],
          tickfont=dict(color='#141554', size=12),
          color='#141554'
      ),
   )
   fig_rev.update_yaxes(title_font_color='#141554')
   st.plotly_chart(fig_rev, use_container_width=True)

# Expandable container for demographics
    
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
       textposition='outside',
       textfont=dict(size=12, color='#141554',family='Poppins'),
       hovertemplate=None,
       hoverinfo='skip'
   )
   
   # Calculate max value and set y-axis range

   max_demographic = df_demographics['Demographic Percentages'].max()
   y_demo_max = max_demographic * 1.1  # 10% higher than max value

   fig_demo.update_layout(
       showlegend=False,
       title="",
       title_x=0.5,
       title_font_size=20,
       xaxis_title="",
       yaxis_title="Percentage of Students (%)",
  
       margin=dict(t=80),
       height=500,
       transition_duration=1000,
       transition_easing="cubic-in-out",
       plot_bgcolor='white',
       paper_bgcolor='white',
       font=dict(color='#141554'),
       xaxis=dict(
          tickfont=dict(color='#141554', size=12),
          color='#141554'
      ),
      yaxis=dict(
          tickformat='.0%',
          range=[0,y_rev_max],
          tickfont=dict(color='#141554', size=12),
          color='#141554'
      )
   )
   fig_demo.update_yaxes(title_font_color='#141554')
   
   st.plotly_chart(fig_demo, use_container_width=True)



