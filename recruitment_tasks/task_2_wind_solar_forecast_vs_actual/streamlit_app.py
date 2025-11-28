import streamlit as st
import pandas as pd
from functions import fetch_data_historical, fetch_data_forecast, to_cest, prep_tech, URL_historic, URL_forecast
from datetime import datetime, date


st.title("Part 2 – Wind & Solar: Forecast vs Actuals")

st.set_page_config(layout="wide")

#Task 2.1: Pick any day between 10–21 November.
picked_date = st.date_input(
    "Select a date (10–21 November)",
    value=datetime(2023, 11, 15).date(),
    min_value=datetime(2023, 11, 10).date(),
    max_value=datetime(2023, 11, 21).date(),
)

if st.button("Fetch and display data"):
    day_start = datetime.combine(picked_date, datetime.min.time())
    date_str = picked_date.isoformat()

    with st.spinner("Fetching data from BMRS..."):
        df_hist = fetch_data_historical(day_start, URL_historic)
        df_fore = fetch_data_forecast(day_start, URL_forecast)

        df_hist = to_cest(df_hist)
        df_fore = to_cest(df_fore)

        df_fore = df_fore.sort_values("startTime")
        df_fore = df_fore.drop_duplicates("settlementPeriod", keep="last")

        wind = prep_tech(df_hist, df_fore, date_str, "Wind")
        solar = prep_tech(df_hist, df_fore, date_str, "Solar")

    if wind.empty and solar.empty:
        st.error("No data available for this date.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Wind – Forecast vs Actual (CEST)")
            if not wind.empty:
                #Task 2.3: Create two graphs: one for wind, one for solar.
                #Task 2.4: On each graph, show both the forecast and the actual generation.
                st.line_chart(
                    wind.set_index("time_axis")[["forecast_MW", "actual_MW"]]
                )
            else:
                st.warning("No wind data available.")

        with col2:
            st.subheader("Solar – Forecast vs Actual (CEST)")
            if not solar.empty:
                #Task 2.3: Create two graphs: one for wind, one for solar.
                #Task 2.4: On each graph, show both the forecast and the actual generation.
                st.line_chart(
                    solar.set_index("time_axis")[["forecast_MW", "actual_MW"]]
                )
            else:
                st.warning("No solar data available.")

        col1, col2 = st.columns(2)

        with col1:
            st.caption("Wind – settlement period comparison")
            if not wind.empty:
                #Task 2.5: Add a small table under each graph with the difference by settlement period.
                st.dataframe(
                    wind[
                        ["settlementPeriod", "forecast_MW", "actual_MW", "error_MW"]
                    ],
                    use_container_width=True,
                )

        with col2:
            st.caption("Solar – settlement period comparison")
            if not solar.empty:
                #Task 2.5: Add a small table under each graph with the difference by settlement period.
                st.dataframe(
                    solar[
                        ["settlementPeriod", "forecast_MW", "actual_MW", "error_MW"]
                    ],
                    use_container_width=True,
                )

        #Task 2.6: Include a short note: what impact do you think the forecast error might have had on the system?
        st.subheader("Impact of forecast error on the system")
        st.write(
            "If the forecast is wrong, the electricity system must react quickly "
            "— either to make up for missing power "
            "or to deal with extra power — which increases costs and makes keeping the system stable more difficult."
        )
