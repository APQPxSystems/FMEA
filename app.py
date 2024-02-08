import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta, date

# Landing Page
st.title("WELCOME TO FMEA ONLINE!")

# Read FMEA PDCA Excel File
fmea_pdca = pd.read_csv("FMEA PDCA\FMEA_PDCA.csv", encoding="ISO-8859-1")

# Drop Unnecessary Columns
fmea_pdca = fmea_pdca[["Car Maker", "Car Model", "Line", "Findings",
                        "Items to Check/Action", "Department",
                        "Person in Charge", "Status", "Target Date"]]
    
# Convert Line Column to String
fmea_pdca["Line"] = fmea_pdca["Line"].astype(str)
    
# Convert Target Date to Datetime
fmea_pdca["Target Date"] = pd.to_datetime(fmea_pdca["Target Date"], errors="coerce")

department_options = ["___________________________"] + list(fmea_pdca["Department"].unique())
department = st.selectbox("Please select your department:", department_options)
st.write("_________________________________________________________")

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
    st.write("_________________________________________________________")
    
    # Second Part -- Filter by Car Maker
    car_maker = st.selectbox("Select a car maker:", department_fmea_pdca["Car Maker"].unique())
    
    # Filter by Car Maker
    car_maker_department_fmea_pdca = department_fmea_pdca[department_fmea_pdca["Car Maker"].isin([car_maker])]
    
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
    st.write("_________________________________________________________")
    
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
    st.title(f"{len(df_delayed_items)} OPEN Item/s are DELAYED!")
    
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
