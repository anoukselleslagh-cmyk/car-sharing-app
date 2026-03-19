import streamlit as st
import pandas as pd

st.title("Car Sharing Dashboard")

# Function to load CSV files into dataframes
@st.cache_data
def load_data():
    trips = pd.read_csv("data/trips.csv")
    cars = pd.read_csv("data/cars.csv")
    cities = pd.read_csv("data/cities.csv")
    return trips, cars, cities

trips, cars, cities = load_data()

# Merge trips with cars (joining on car_id)
trips_merged = trips.merge(cars, left_on="car_id", right_on="id", suffixes=("", "_car"))

# Merge with cities for car's city (joining on city_id)
trips_merged = trips_merged.merge(cities, on="city_id", suffixes=("", "_city"))

# Clean useless columns
trips_merged = trips_merged.drop(columns=[
    col for col in ["id_car", "city_id", "id_customer", "id"]
    if col in trips_merged.columns
])

# Update the Trips Date Format
trips_merged["pickup_date"] = pd.to_datetime(trips_merged["pickup_time"]).dt.date
trips_merged["dropoff_date"] = pd.to_datetime(trips_merged["dropoff_time"]).dt.date

# ── Sidebar Filters ───────────────────────────────────────────────────────────
st.sidebar.header("Filters")
cars_brand = st.sidebar.multiselect(
    "Select the Car Brand",
    trips_merged["brand"].unique(),
    default=trips_merged["brand"].unique()
)

# Filter dataframe by selected brands
trips_merged = trips_merged[trips_merged["brand"].isin(cars_brand)]

# ── Business Metrics ──────────────────────────────────────────────────────────
st.header("Business Metrics")

total_trips    = len(trips_merged)
total_distance = trips_merged["distance"].sum()
top_car        = trips_merged.groupby("model")["revenue"].sum().idxmax()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Trips", value=total_trips)
with col2:
    st.metric(label="Top Car Model by Revenue", value=top_car)
with col3:
    st.metric(label="Total Distance (km)", value=f"{total_distance:,.2f}")

# ── Preview Data ──────────────────────────────────────────────────────────────
st.header("Data Preview")
st.write(trips_merged.head())

# ── Visualizations ────────────────────────────────────────────────────────────
st.header("Visualizations")

# 1. Trips Over Time
st.subheader("Trips Over Time")
trips_over_time = trips_merged.groupby("pickup_date").size().reset_index(name="trips")
trips_over_time = trips_over_time.set_index("pickup_date")
st.line_chart(trips_over_time)

# 2. Revenue Per Car Model
st.subheader("Revenue Per Car Model")
revenue_by_model = trips_merged.groupby("model")["revenue"].sum().sort_values(ascending=False)
st.bar_chart(revenue_by_model)

# 3. Cumulative Revenue Growth Over Time
st.subheader("Cumulative Revenue Growth Over Time")
cumulative_revenue = trips_merged.groupby("pickup_date")["revenue"].sum().cumsum()
st.area_chart(cumulative_revenue)

# 4. Number of Trips Per Car Model
st.subheader("Number of Trips Per Car Model")
trips_by_model = trips_merged.groupby("model").size().sort_values(ascending=False)
st.bar_chart(trips_by_model)

# 5. Revenue by City
st.subheader("Revenue by City")
revenue_by_city = trips_merged.groupby("city_name")["revenue"].sum().sort_values(ascending=False)
st.bar_chart(revenue_by_city)

# 6. Average Trip Duration by City (bonus)
st.subheader("Average Trip Distance by City")
avg_distance_city = trips_merged.groupby("city_name")["distance"].mean().sort_values(ascending=False)
st.bar_chart(avg_distance_city)
