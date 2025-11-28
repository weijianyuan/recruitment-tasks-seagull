import time
from datetime import datetime, timedelta, date
import json
import requests
import pandas as pd
import plotly.graph_objects as go


#Parameters
BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1/forecast/indicated/day-ahead/evolution"
REFRESH_SECONDS = 1800
TODAY = datetime.now().date()

#Get data using endpoint
def fetch_data(user_date: date) -> dict:
    selected_day = requests.get(
        BASE_URL,
        params={
            "settlementDate": user_date,
            "settlementPeriod": list(range(1, 47)),
            "format": "json"
        },
        timeout=10
        )
    
    selected_day.raise_for_status()
    selected_data = selected_day.json()["data"]
    
    previous_day = requests.get(
        BASE_URL,
        params={
            "settlementDate": (user_date - timedelta(days=1)),
            "settlementPeriod": [47, 48],
            "format": "json"
        },
        timeout=10
    )

    previous_day.raise_for_status()
    previous_data = previous_day.json()["data"]

    merged_dict = selected_data + previous_data

    return merged_dict

#Sort data to get local_period
def local_period_sorting(user_input_day: date) -> pd.DataFrame:
    raw_json = fetch_data(user_input_day)
    df_unsorted = pd.DataFrame(raw_json)

    #Convert data out of API to 1. date format, 2. integer
    df_unsorted["settlementDate"] = pd.to_datetime(df_unsorted["settlementDate"]).dt.date
    df_unsorted["settlementPeriod"] = df_unsorted["settlementPeriod"].astype(int)

    df_sorted = df_unsorted.sort_values(["settlementDate", "settlementPeriod"])

    df_sorted["local_period"] = range(1, len(df_sorted) + 1)

    return df_sorted

#Task 1.2.1: Data is UTC, but we work in CEST.
#So the graph should show periods 47–48 from the previous UTC day, plus periods 1–46 of the selected day
def pick_latest_and_prev(df):
    rows = []
    order = [47, 48] + list(range(1, 47))

    for i, sp in enumerate(order, start=1):
        d = df[df["settlementPeriod"] == sp].sort_values("publishTime")
        if d.empty:
            continue

        latest = d.iloc[-1]["indicatedImbalance"]
        prev   = d.iloc[-2]["indicatedImbalance"] if len(d) > 1 else latest

        rows.append([i, sp, latest, prev])

    out = pd.DataFrame(rows, columns=["local_period", "settlementPeriod", "latest", "prev"])
    out["delta"] = out["latest"] - out["prev"]

    return out

#Task 1.5: Include a visual indicator showing how the forecast changed vs the previous version.
def plot_latest_and_delta(delta_latest_prev, selected_date):
    colors = [
        "green" if d > 0 else "red" if d < 0 else "gray"
        for d in delta_latest_prev["delta"]
    ]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=delta_latest_prev["local_period"],
        y=delta_latest_prev["latest"],
        mode="lines+markers",
        name="Latest forecast"
    ))

    fig.add_trace(go.Bar(
        x=delta_latest_prev["local_period"],
        y=delta_latest_prev["delta"],
        marker_color=colors,
        opacity=0.5,
        name="Delta vs previous"
    ))


    fig.update_xaxes(
        tickmode="array",
        tickvals=delta_latest_prev["local_period"],
        ticktext=delta_latest_prev["settlementPeriod"].astype(str),
        title="Settlement period (47, 48, 1..46)"
    )

    fig.update_layout(
        title=f"Latest Forecast & Delta vs Previous {selected_date}",
        yaxis_title="Indicated Imbalance [MW]",
        bargap=0,
        template="plotly_dark"
    )

    return fig
