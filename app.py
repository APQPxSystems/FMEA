# FMEA PDCA Viewer
# Katigbak, Kent Jym B. --- Staff
# Systems Engineering
#______________________________________________________________________________
# Editable Content
fmea_date = "February 01, 2024"
fmea_maker_model = "Daihatsu D54B"
fmea_line = "Line 3144"
fmea_time = "8:00-9:15"

npra_date = "February 03, 2024"
npra_maker_model = "Toyota Land Cruiser"
npra_line = "Land Cruiser Event Area"
npra_time = "10:00 - 12:00"
#_______________________________________________________________________________

# Start of Source Code. Do Not Edit!

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta, date

# Streamlit Configurations
st.set_page_config(page_title="Apps by Systems Eng", layout="wide")
hide_st_style = """
                <style>
                #MainMenu {visibility:hidden;}
                footer {visibility:hidden;}
                header {visibility:hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Landing Page
st.markdown("<h2 style='text-align:center; background-color:#1e6262; font-family: Arial, sans-serif;'>WELCOME TO FMEA ONLINE!</h2>", unsafe_allow_html=True)

schedule_container = st.container(border=True)
with schedule_container:
    st.markdown("<h3 style='text-align:center; font-family: Arial, sans-serif;'><u>FMEA Checking Schedule:</u></h3>", unsafe_allow_html=True)
    top_col1, top_col2 = st.columns([1,1])

    with top_col1:
        fmea_schedule_container = st.container(border=True)
        with fmea_schedule_container:
            st.subheader("FMEA Line Checking:")
            st.write(fmea_date)
            st.write(fmea_maker_model)
            st.write(fmea_line)
            st.write(fmea_time)
        
    with top_col2:
        npra_schedule_container = st.container(border=True)
        with npra_schedule_container:
            st.subheader("NPRA Checking")
            st.write(npra_date)
            st.write(npra_maker_model)
            st.write(npra_line)
            st.write(npra_time)

# Read FMEA PDCA Excel File
fmea_pdca = pd.read_csv("FMEA_PDCA.csv", encoding="ISO-8859-1")

# Drop Unnecessary Columns
fmea_pdca = fmea_pdca[["Car Maker", "Car Model", "Line", "Findings",
                        "Items to Check/Action", "Department",
                        "Person in Charge", "Status", "Target Date"]]
    
# Convert Line Column to String
fmea_pdca["Line"] = fmea_pdca["Line"].astype(str)
    
# Convert Target Date to Datetime
fmea_pdca["Target Date"] = pd.to_datetime(fmea_pdca["Target Date"], errors="coerce")

department_options = list(fmea_pdca["Department"].unique())

department_selection_container = st.container(border=True)
with department_selection_container:
    department = st.selectbox("Please select your department:", department_options)

first_part_container = st.container(border=True)
with first_part_container:
    if department != "___________________________":
        # First Part -- General
        st.title(f"Here's the FMEA Dashboard for {department}")
        
        department_fmea_pdca = fmea_pdca[fmea_pdca["Department"].isin([department])]
        
        # First Chart --- Open and Close Items per Car Maker
        open_count = len(department_fmea_pdca[department_fmea_pdca["Status"]== "OPEN"])
        st.subheader(f"You have {open_count} OPEN items in total!")
        first_chart = alt.Chart(department_fmea_pdca).mark_bar().encode(
            x=alt.X('Car Maker:N', title='Car Maker'),
            y=alt.Y('count():Q', title='Count'),
            color='Status:N'
        ).properties(
            title = f"{department} Status of Items per Car Maker"
        )
        st.altair_chart(first_chart, use_container_width=True)
    
car_maker_container = st.container(border=True)
with car_maker_container:
    # Second Part -- Filter by Car Maker
    car_maker = st.selectbox("Select a car maker:", department_fmea_pdca["Car Maker"].unique())
    
    # Filter by Car Maker
    car_maker_department_fmea_pdca = department_fmea_pdca[department_fmea_pdca["Car Maker"].isin([car_maker])]
    
second_part_container = st.container(border=True)
with second_part_container:
    # Second Chart --- Status of Each Department per Line
    open_count_2 = len(car_maker_department_fmea_pdca[car_maker_department_fmea_pdca["Status"]== "OPEN"])
    st.subheader(f"You have {open_count_2} OPEN items in {car_maker}!")
    second_chart = alt.Chart(car_maker_department_fmea_pdca).mark_bar().encode(
        x=alt.X('Line:N', title='Line'),
        y=alt.Y('count():Q', title='Count'),
        color='Status:N'
    ).properties(
        title = f"{department} Status of Items per Line in {car_maker}"
    )
    st.altair_chart(second_chart, use_container_width=True)
    
third_part_container = st.container(border=True)
with third_part_container:
    # Third Part --- Filter by Line
    line = st.selectbox("Select line:", car_maker_department_fmea_pdca["Line"].unique())
    
    line_cm_dept_fmea_pdca = car_maker_department_fmea_pdca[car_maker_department_fmea_pdca["Line"].isin([line])]
    line_cm_dept_fmea_pdca = line_cm_dept_fmea_pdca[line_cm_dept_fmea_pdca["Status"]=="OPEN"]
    
    # Filter data for delayed items with OPEN status and Target Date less than today
    df_delayed_items = line_cm_dept_fmea_pdca[
        (line_cm_dept_fmea_pdca["Status"] == "OPEN") &
        ((pd.to_datetime(line_cm_dept_fmea_pdca["Target Date"]) < datetime.today()) | line_cm_dept_fmea_pdca["Target Date"].isnull())
    ]

    # Display count of delayed items
    st.subheader(f"{len(df_delayed_items)} OPEN Item/s are DELAYED!")
    
    df_final_filter_styled = line_cm_dept_fmea_pdca.style.apply(
        lambda row: ['background-color: red' if row['Status'] == 'OPEN'
                    and (pd.isna(row['Target Date']) or row['Target Date'].date() < date.today()) else
                    'background-color: red' if pd.isna(row['Target Date']) else '' for _ in row],
        axis=1
    )

    # Display the DataFrame with Styler
    st.dataframe(df_final_filter_styled)
    
    # Download Button for Final Generated PDCA
    @st.cache_data
    def convert_df(df):
        return df.to_csv().encode("utf-8")

    csv = convert_df(line_cm_dept_fmea_pdca)

    st.download_button(
        label=f"Download {department} FMEA PDCA OPEN Items on Line {line}",
        data=csv,
        file_name=f"Line {line} FMEA PDCA OPEN Items - {department}.csv",
        mime="text/csv"
    )



st.write("_____________________________________________________________")
st.markdown("<p style='font-family: Georgia, serif; text-align: right'>SYSTEMS ENG'G || ME DEPT</p>", unsafe_allow_html=True)
    
