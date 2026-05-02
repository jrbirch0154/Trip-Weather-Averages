# Trip Planner
# Thu Apr 30 18:18:13 2026
# Jacob Birch

#%% Init
from geopy.geocoders import Nominatim
from datetime import date, timedelta
import requests
import pandas as pd
import time
import plotly.graph_objects as go
import streamlit as st



geolocator = Nominatim(user_agent='BongoApp')


def grab_long_lat(location: str) -> list:
    raw = geolocator.geocode(location)
    
    return [raw.latitude, raw.longitude]

@st.cache_data(show_spinner=False,ttl=86400) # caches data for 1 day so that it doesn't recall the API over and over
def get_historical_weather_estimate(lat, lon, month_day_start, month_day_end, years=range(2015, 2025)) -> pd.DataFrame:
    """
    Estimate weather for a future date range using historical averages.
    month_day_start / month_day_end: "MM-DD" strings
    """
    all_data = []
    
    month_day_start = month_day_start.strftime('%m-%d')
    month_day_end = month_day_end.strftime('%m-%d')

    for year in years:
        start = f"{year}-{month_day_start}"
        # If end month is before start month, end date is in the next year
        if month_day_end < month_day_start:
            end = f"{year + 1}-{month_day_end}"
        else:
            end = f"{year}-{month_day_end}"

        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start,
            "end_date": end,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "windspeed_10m_max"
            ],
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch",
            "timezone": "auto"
        }
        
        time.sleep(.5)
        resp = requests.get(url, params=params)
        data = resp.json()
        # print(data)

        df = pd.DataFrame(data["daily"])
        df["year"] = year
        all_data.append(df)

    combined = pd.concat(all_data, ignore_index=True)
 
    combined["month_day"] = pd.to_datetime(combined["time"]).dt.strftime('%m-%d')
    # print(combined.head(20))
    # print(combined.dtypes)
 
    summary = combined.groupby("month_day").agg(
        avg_high=("temperature_2m_max", "mean"),
        avg_low=("temperature_2m_min", "mean"),
        avg_precip=("precipitation_sum", "mean"),
        avg_wind=("windspeed_10m_max", "mean"),
    ).round(1)
 
    # Reset index so month_day becomes a column, then sort chronologically
    summary = summary.reset_index()
    summary["sort_key"] = pd.to_datetime("2000-" + summary["month_day"])
    summary = summary.sort_values("sort_key").drop(columns="sort_key").reset_index(drop=True)
 
    return summary


def temp_chart(df: pd.DataFrame, city: str) -> go.Figure:
    
    fig = go.Figure()
    
    padding = 25
    
    lowest = df['avg_low'].min()
    highest = df['avg_high'].max()


    fig.add_scatter(
        x=df['month_day'],
        y=df['avg_high'],
        name='avg_high',
        mode='lines',
        line=dict(color='tomato',width=2)
        # fill='tonexty',
        # fillcolor='rgba(255, 99, 71, 0.15)',
        )
    
    fig.add_scatter(
        x=df['month_day'],
        y=df['avg_low'],
        name='Avg Low',
        mode='lines',
        line=dict(color='steelblue', width=2),
        )
    
    fig.update_traces(hovertemplate="%{y:.1f} F")
    
    fig.add_hline(y=lowest,annotation_text=f'Lowest avg: {lowest}F',annotation_position='bottom left',line_color='steelblue',line_dash='dash')
    
    fig.add_hline(y=highest,annotation_text=f'Highest avg: {highest}F',annotation_position='top left',line_color='tomato',line_dash='dash')



    fig.update_layout(
            title=dict(text=f'Expected Temperature Range in {city}', font=dict(size=20)),
            xaxis=dict(title='Date', tickangle=-45, showgrid=False,
                       type='category',tickmode='array',
                       tickvals=df['month_day'].tolist(),
                       ticktext=df['month_day'].tolist()
                       ),
            yaxis=dict(title='Temperature (°F)', showgrid=True, gridcolor='rgba(200,200,200,0.3)',range=[lowest - padding, highest + padding]),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            plot_bgcolor='white',
            hovermode='x unified',     # shows both traces in one tooltip on hover
            margin=dict(l=40, r=20, t=60, b=60),
        )
    
    
    return fig

def precip_chart(df: pd.DataFrame, city: str) -> go.Figure:
    fig = go.Figure()
    
    fig.add_bar(
        x=df['month_day'],
        y=df['avg_precip'],
        name='Precipitation',
        # line=dict(color='indigo',width=2
        )
    
    fig.update_traces(hovertemplate="%{x}: %{y:.2f} inches")
    
    fig.update_layout(
        title=f'Expected precipitation in {city}',
        xaxis=dict(title='Date',tickangle=-45,showgrid=False,
                   tickvals=df['month_day'].tolist(),
                   ticktext=df['month_day'].tolist()
                   ),
        yaxis=dict(
            title='Rainfall (in)',
            range=[0, df['avg_precip'].max() + 0.5])
        )
    

    
    return fig
    
    

#%% Streamlit

st.set_page_config(page_title="Weather Planner", layout="wide")

st.title("Weather Planning Chart")

city = st.text_input('Enter a city: ')

city = city.title() # Title case

dates = st.date_input('Select trip dates (31 days max)',
                           value=(date.today(), date.today() + timedelta(days=7)))


if st.button('Run'):
    if len(dates) != 2:
        st.warning('Please select both a start and an end date.')
        st.stop()
    start_date, end_date = dates
    if city and start_date and end_date:
        if ((end_date - start_date).days > 31):
            st.warning('Dates must be within 31 days of each other')
            st.stop()
        else:    
            try:            
                with st.spinner('Fetching data...',show_time=True):
                    [lat, lon] = grab_long_lat(city)
                    df = get_historical_weather_estimate(lat, lon, start_date, end_date)
 
            except Exception as e:
                st.error('City not found.')
                print(f'Error: {e}') # for local debugging only
                st.stop()
            
            tc = temp_chart(df,city)
            pc = precip_chart(df,city)
            
            st.header('2015 - 2025 Averages')
            st.plotly_chart(tc)
            st.plotly_chart(pc)



