import requests
from datetime import timedelta, datetime, date
import json
import pandas as pd


URL_historic = "https://data.elexon.co.uk/bmrs/api/v1/generation/actual/per-type/wind-and-solar"
URL_forecast = "https://data.elexon.co.uk/bmrs/api/v1/forecast/generation/wind-and-solar/day-ahead"

#Download historical data as JSON, then converts to pd.DataFrame
def fetch_data_historical(user_input_date: datetime, URL) -> pd.DataFrame:
    response = requests.get(
        URL,
        params = {
            "from": user_input_date,
            "to": (user_input_date + timedelta(days=1)),
            "format": "json"
        }
    )
    
    response.raise_for_status()
    resp_json = response.json()

    return pd.DataFrame(resp_json["data"])

#Download historical data as JSON, then converts to pd.DataFrame
def fetch_data_forecast(user_input_date: datetime, URL) -> pd.DataFrame:
    response = requests.get(
        URL,
        params = {
            "from": user_input_date,
            "to": (user_input_date + timedelta(days=1)),
            "processType": "intraday total",
            "format": "json"
        }
    )
    response.raise_for_status()
    resp_json = response.json()

    return pd.DataFrame(resp_json["data"])
    
#Task 2.2: Convert timestamps to CEST.
def to_cest(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    #Transform startTime to pd.to_datetime format
    df["startTime"] = pd.to_datetime(df["startTime"], utc=True)

    #Convert UTC to CEST
    df["time_cest"] = df["startTime"].dt.tz_convert("Europe/Warsaw")

    return df

#Create merged DF based on selected tech
def prep_tech(df_hist, df_fore, date_str, tech):

    historic = df_hist[
        (df_hist["settlementDate"] == date_str)
        & (df_hist["businessType"].str.contains(tech, case=False, na=False))
    ][["settlementPeriod", "quantity"]]

    forecast = df_fore[
        (df_fore["settlementDate"] == date_str)
        & (df_fore["businessType"].str.contains(tech, case=False, na=False))
    ][["settlementPeriod", "quantity", "time_cest"]]

    historic = (
        historic.groupby("settlementPeriod", as_index=False)["quantity"]
                .sum()
                .rename(columns={"quantity": "actual_MW"})
    )

    forecast = (
        forecast.sort_values("time_cest")
                .groupby("settlementPeriod", as_index=False)
                .tail(1)
                .rename(columns={"quantity": "forecast_MW", "time_cest": "time_forecast"})
    )

    full_sp = pd.DataFrame({"settlementPeriod": range(1, 49)})

    merged = full_sp.merge(forecast, on="settlementPeriod", how="left")
    merged = merged.merge(historic, on="settlementPeriod", how="left")


    base = datetime.fromisoformat(date_str)

    merged["time_axis"] = merged["settlementPeriod"].apply(
        lambda sp: base + timedelta(minutes=(sp - 1) * 30)
    )
    merged["error_MW"] = merged["actual_MW"] - merged["forecast_MW"]


    return merged.sort_values("settlementPeriod").reset_index(drop=True)


