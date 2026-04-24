import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from database import engine

# Set up the page layout
st.set_page_config(page_title="Trading Signals", page_icon="📈", layout="wide")

st.title("📈 Sinais M3 USA")
st.markdown("View and filter your real-time trading signals. Sinais não concretizados também sao registrados. Sempre cheque gráficos.")

# --- TRADINGVIEW WIDGET ---
components.html(
    """
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container" style="height:100%;width:100%">
      <div id="tradingview_widget" style="height:100%;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {
      "autosize": true,
      "symbol": "NASDAQ:SPY",
      "interval": "D",
      "timezone": "Etc/UTC",
      "theme": "light",
      "style": "1",
      "locale": "en",
      "enable_publishing": false,
      "allow_symbol_change": true,
      "container_id": "tradingview_widget"
      }
      );
      </script>
    </div>
    <!-- TradingView Widget END -->
    """,
    height=500,
)

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
    
    if not df.empty:
        df['Month'] = df['timestamp'].dt.strftime('%B %Y')
        week_start = df['timestamp'] - pd.to_timedelta(df['timestamp'].dt.dayofweek, unit='d')
        week_end = week_start + pd.Timedelta(days=6)
        df['Week Window'] = week_start.dt.strftime('%b %d') + " - " + week_end.dt.strftime('%b %d')
        
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

    def highlight_tier(row):
        # Highlight only Tier 1 signals (using a subtle blue background)
        if row['List'] == 'Tier 1':
            color = "rgba(59, 130, 246, 0.15)"
        else:
            color = "transparent"
        return [f"background-color: {color}"] * len(row)

    # --- DATA TABLE ---
    st.subheader("Signal History")
    
    if filtered_df.empty:
        st.info("No signals match your filters.")
    else:
        # Display grouped by Month and Week
        months = filtered_df['Month'].unique()
        
        for month in months:
            st.markdown(f"### {month}")
            month_df = filtered_df[filtered_df['Month'] == month]
            
            weeks = month_df['Week Window'].unique()
            for week in weeks:
                # Use expanders to make it mobile-friendly and easily scrollable
                with st.expander(f"Week: {week}", expanded=True):
                    week_df = month_df[month_df['Week Window'] == week].copy()
                    
                    # Format strings and capitalize for a cleaner display
                    week_df['Date'] = week_df['timestamp'].dt.strftime('%b %d, %I:%M %p')
                    week_df['action'] = week_df['action'].str.upper()
                    
                    # Select and rename columns for the final table
                    display_df = week_df[['Date', 'ticker', 'action', 'price', 'list_name', 'interval']].rename(
                        columns={'ticker': 'Ticker', 'action': 'Action', 'price': 'Price', 'list_name': 'List', 'interval': 'Interval'}
                    )
                    
                    styled_df = display_df.style.format({"Price": "${:.2f}"}).apply(highlight_tier, axis=1)
                    st.dataframe(styled_df, use_container_width=True, hide_index=True)