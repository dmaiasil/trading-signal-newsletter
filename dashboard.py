import streamlit as st
import pandas as pd
from database import engine

# Set up the page layout
st.set_page_config(page_title="Trading Signals", page_icon="📈", layout="wide")

st.title("📈 Trading Signals Dashboard")
st.markdown("View and filter your real-time trading signals.")

# We cache the data for 10 seconds so we don't overwhelm the database 
# if you click around the UI quickly.
@st.cache_data(ttl=10)
def load_data():
    # Fetch data directly into a Pandas DataFrame
    query = "SELECT timestamp, ticker, action, price, list_name, interval FROM signals ORDER BY timestamp DESC"
    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn)
    
    # Convert timestamp string to actual datetime objects for better formatting
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

df = load_data()

if df.empty:
    st.info("No signals found in the database yet.")
else:
    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filters")
    
    actions = df['action'].unique().tolist()
    selected_actions = st.sidebar.multiselect("Action (Buy/Sell)", actions, default=actions)
    
    lists = df['list_name'].unique().tolist()
    selected_lists = st.sidebar.multiselect("Lists", lists, default=lists)

    # Apply the filters to our dataframe
    filtered_df = df[(df['action'].isin(selected_actions)) & (df['list_name'].isin(selected_lists))]

    # --- METRICS ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Signals", len(filtered_df))
    col2.metric("Buy Signals", len(filtered_df[filtered_df['action'] == 'buy']))
    col3.metric("Sell Signals", len(filtered_df[filtered_df['action'] == 'sell']))

    # --- DATA TABLE ---
    st.subheader("Signal History")
    st.dataframe(filtered_df.style.format({"price": "${:.2f}"}), use_container_width=True, hide_index=True)