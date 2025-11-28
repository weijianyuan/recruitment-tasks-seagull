import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from imbalance_functions import local_period_sorting, pick_latest_and_prev, plot_latest_and_delta, TODAY, REFRESH_SECONDS


st.title("Part 1 - Imbalance visual data")

st.set_page_config(layout="wide")

st.sidebar.header("Settings")

#Task 1.4: Add a refresh loop so the values update automatically when new data appears.
st_autorefresh(interval=REFRESH_SECONDS * 1000, key="refresh")

#state default settings
if "mode" not in st.session_state:
    st.session_state["mode"] = None

if st.sidebar.button("Select a date"):
    st.session_state["mode"] = "historical_date"

if st.sidebar.button("Current day"):
    st.session_state["mode"] = "current_date"

#Task 1.1: Pick any day between 10–21 November.
if st.session_state["mode"] == "historical_date":
    selected_date_input = st.sidebar.date_input(
        "User input date",
        value=None, 
        min_value=date(2025, 11, 10), 
        max_value=date(2025, 11, 21)
        )

    if selected_date_input:
        st.write(selected_date_input)

        #local_period_sorting calls fetch_data function and sort settlementPeriod
        data_sorted = local_period_sorting(selected_date_input)

        #data for graph with latest and prev shown
        data_latest_prev = pick_latest_and_prev(data_sorted)
    
        st.dataframe(data_sorted)
        st.dataframe(data_latest_prev)

#Task 1.2: Plot indicatedImbalance for all settlement periods.
        fig = plot_latest_and_delta(data_latest_prev, selected_date_input)
        st.plotly_chart(fig, use_container_width=True)

#Task 1.3: Create an extra graph for the current day (this dataset updates twice per hour).
elif st.session_state["mode"] == "current_date":
    st.write(TODAY)
    
    data_current_sorted = local_period_sorting(TODAY)

    data_latest_prev = pick_latest_and_prev(data_current_sorted)
   
    st.dataframe(data_current_sorted)
    st.dataframe(data_latest_prev)

    fig = plot_latest_and_delta(data_latest_prev, TODAY)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Select the option in sidebar")

if st.sidebar.button("Refresh now"):
    st.rerun()