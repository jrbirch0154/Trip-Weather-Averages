# Trip Weather Averages

A Streamlit app for planning trips around historical weather. Enter any city and a date range, and the app fetches ten years of climate data from the Open-Meteo archive API to show you what weather to realistically expect — not a forecast, but a data-backed historical average.

**Live App: [trip-weather-planning.streamlit.app](https://trip-weather-planning.streamlit.app/)**

---

## How It Works

The app geocodes your city using `geopy`, then queries the [Open-Meteo Archive API](https://open-meteo.com/) for your specified month/day range across 2015–2025. It aggregates daily highs, lows, precipitation, and wind speed into per-day averages, then plots the results interactively with Plotly.

Results are cached for 24 hours so repeated queries don't hammer the API.

---

## Features

- **Temperature range chart** — avg daily high and low across 10 years, with min/max reference lines
- **Precipitation bar chart** — average expected rainfall per day over the trip window
- Supports any city worldwide via geocoding
- Trip window capped at 31 days
- Year-over-year wrapping handled automatically (e.g. a Dec 28 – Jan 5 date range)

---

## Usage

1. Open the [live app](https://trip-weather-planning.streamlit.app/)
2. Enter a city name
3. Select your trip's start and end dates (up to 31 days)
4. Click **Run**

---

## Running Locally

```bash
git clone https://github.com/jrbirch0154/Trip-Weather-Averages.git
cd Trip-Weather-Averages
pip install -r requirements.txt
streamlit run historical_weather_planner.py
```

---

## Dependencies

- `streamlit`
- `pandas`
- `plotly`
- `requests`
- `geopy`

---

## Data Source

Historical weather data is provided by the free [Open-Meteo Archive API](https://archive-api.open-meteo.com/). No API key required.
