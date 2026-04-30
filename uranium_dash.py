import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import numpy as np

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(
    page_title="Uranium Macro Dashboard",
    layout="wide",
)
tab1, tab2 = st.tabs(["Dashboard", "Price Model"])

with tab1:
    # your existing dashboard code
    st.title("☢️ Uranium Macro Dashboard")

    st.markdown("""
Tracks uranium equities, ETF proxies, and structural supply-demand signals.
            

""")

# -----------------------
# UNIVERSE (KEY TICKERS)
# -----------------------
    miners = {
        "UUUU": "UUUU",
        "Cameco": "CCJ",
        "NexGen": "NXE",
        "Denison": "DNN",
        "UEC": "UEC"
}

    reactors = {
        "BWXT": "BWXT",
        "Fluor": "FLR",
        "NuScale": "SMR",
        "GE": "GE"
}
    tickers = {
        "BWXT" : "BWXT",
        "Fluor" : "FLR",
        "NuScale": "SMR",
        "GE": "GE",
        "UUUU": "UUUU",
        "Cameco": "CCJ",
        "NexGen": "NXE",
        "Denison": "DNN",
        "UEC": "UEC"
    }
    ticker = list(miners.values()) + list(reactors.values())

# -----------------------
# DATA LOADER
# -----------------------
    @st.cache_data(ttl=3600)
    def load_data(ticker):
        data = yf.download(ticker, period="2y")["Close"]
        return data

    prices = load_data(ticker)

###URANIUM MINERS GRAPH###
    st.subheader("⛏️ Uranium Miners (Commodity Beta)")

    fig_miners = go.Figure()

    for name, tkr in miners.items():
        norm = prices[tkr] / prices[tkr].iloc[0]
        fig_miners.add_trace(go.Scatter(
            x=prices.index,
            y=norm,
            name=name
    ))

    fig_miners.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig_miners, use_container_width=True)
# -----------------------REACTOR MANUFACTRERS###
    st.subheader("⚛️ Nuclear Industrial / Reactor Plays")

    fig_reactors = go.Figure()

    for name, tkr in reactors.items():
        norm = prices[tkr] / prices[tkr].iloc[0]
        fig_reactors.add_trace(go.Scatter(
            x=prices.index,
            y=norm,
            name=name
    ))

    fig_reactors.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig_reactors, use_container_width=True)



    st.subheader("📊 Miners vs Reactors Ratio")

    miners_index = prices[list(miners.values())].mean(axis=1)
    reactors_index = prices[list(reactors.values())].mean(axis=1)

    ratio = miners_index / reactors_index

    fig_ratio = go.Figure()
    fig_ratio.add_trace(go.Scatter(x=ratio.index, y=ratio, name="Miners / Reactors"))

    fig_ratio.update_layout(template="plotly_dark")
    st.plotly_chart(fig_ratio, use_container_width=True)
# -----------------------
# VOLATILITY REGIME
# -----------------------
    st.subheader("Volatility Regime (Risk Cycle Proxy)")

    returns = prices.pct_change().rolling(30).std() * 100

    fig2 = go.Figure()

    for name, tkr in tickers.items():
        fig2.add_trace(go.Scatter(
            x=returns.index,
            y=returns[tkr],
            name=name
    ))

    fig2.update_layout(height=400, template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------
# URANIUM PRICE PROXY SECTION
# -----------------------

# -----------------------
# RELATIVE VALUE MATRIX
# -----------------------
    st.subheader("Relative Value Snapshot")

    df_latest = pd.DataFrame({
        "Asset": list(tickers.keys()),
        "Last Price": [prices[v].iloc[-1] for v in tickers.values()],
        "1Y Return (%)": [
            (prices[v].iloc[-1] / prices[v].iloc[-252] - 1) * 100
            if len(prices[v].dropna()) > 252 else None
            for v in tickers.values()
    ]
})

    st.dataframe(df_latest)

    st.subheader("Uranium Structural Drivers (Core Model)")
    col1, col2, col3 = st.columns(3)

    with col1:
        inventory_years = st.number_input(
            "Global Inventory Coverage (years)",
            min_value=0.0,
            max_value=10.0,
            value=2.5,
            step=0.1
    )

    with col2:
        contracting_lbs = st.number_input(
            "Annual Utility Contracting (million lbs)",
            min_value=0.0,
            value=180.0,
            step=5.0
    )

    with col3:
        supply_lbs = st.number_input(
            "Annual Mine Supply (million lbs)",
            min_value=0.0,
            value=150.0,
            step=5.0
    )# Demand estimate (simplified global reactor demand proxy)
    reactor_demand = 180  # baseline million lbs (adjustable later)

    supply_demand_gap = reactor_demand - supply_lbs
    inventory_tightness = max(0, 3.5 - inventory_years)  # lower inventory = tighter market
    contract_pressure = contracting_lbs / reactor_demand

    st.markdown("Derived Metrics")

    st.write(f"**Supply–Demand Gap:** {supply_demand_gap:.1f} million lbs")
    st.write(f"**Inventory Tightness Score:** {inventory_tightness:.2f}")
    st.write(f"**Contracting Pressure Ratio:** {contract_pressure:.2f}")
    tightness_index = (
        (supply_demand_gap / 50) +
        inventory_tightness +
        (contract_pressure - 1)
)

    st.subheader("Uranium Tightness Index")

    st.metric(
        label="Cycle Tightness Score",
        value=f"{tightness_index:.2f}"
)
    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=tightness_index,
        title={"text": "Uranium Market Tightness"},
        gauge={
            "axis": {"range": [0, 5]},
            "steps": [
                {"range": [0, 1.5], "color": "green"},
                {"range": [1.5, 3], "color": "yellow"},
                {"range": [3, 5], "color": "red"},
        ],
    }
))

    st.plotly_chart(fig, use_container_width=True)
# -----------------------
# STRUCTURAL FRAMEWORK
# -----------------------
    st.subheader("Uranium Cycle Interpretation")

    st.markdown("""
### 1. Supply Side (tightening driver)
- Low marginal production growth
- High restart costs for idle mines
- Concentrated supply (Kazatomprom, Cameco)

### 2. Demand Side (sticky)
- Reactor fleet is expanding (China, India)
- Life extensions increase baseline demand

### 3. Price Formation
- Spot = sentiment / marginal liquidity
- Term = utility contracting reality

### 4. Key Cycle Signal
When:
- Uranium proxy trends up
- Volatility rises
- Equities lead spot

 That’s typically a **late-cycle tightening phase**
""")

# -----------------------
# FOOTER
# -----------------------
    st.markdown("---")
    st.markdown("Built for uranium cycle + equity sensitivity analysis")

with tab2:

    st.header("Uranium Price Scenario Model")

    st.markdown("""
    Estimate future uranium price based on structural drivers:
    inventory, contracting pressure, and supply-demand balance.
    """)
    col1, col2, col3 = st.columns(3)

    with col1:
        inventory_years = st.slider("Inventory (years of coverage)", 0.5, 5.0, 2.5)

    with col2:
        contracting_ratio = st.slider("Contracting (% of demand)", 0.5, 1.5, 1.0)

    with col3:
        supply_gap = st.slider("Supply Gap (million lbs)", -50, 50, 10)
    
    inv_score = max(0, 3 - inventory_years)       # lower inventory = tighter
    contract_score = contracting_ratio - 1        # above 1 = pressure
    supply_score = supply_gap / 50                # scale gap
    tightness = inv_score + contract_score + supply_score

    base_price = 70  # baseline long-term uranium price

    # nonlinear response (important)
    if tightness < 0:
        price = base_price * (1 + tightness * 0.3)
    elif tightness < 2:
        price = base_price * (1 + tightness * 0.6)
    else:
        price = base_price * (1 + tightness * 1.2)
    
    st.subheader("Model Output")

    st.metric("Implied Uranium Price ($/lb)", f"{price:.2f}")

    pct_move = (price / base_price - 1) * 100
    st.metric("Expected Move (%)", f"{pct_move:.1f}%")

    if tightness < 0:
        scenario = "🟢 Oversupplied (Bearish)"
    elif tightness < 1.5:
        scenario = "🟡 Balanced / Early Cycle"
    elif tightness < 3:
        scenario = "🟠 Tightening Market"
    else:
        scenario = "🔴 Supply Shock / Bull Market"

    st.markdown(f"### Scenario: {scenario}")

    x = np.linspace(-1, 4, 100)
    y = []

    for t in x:
        if t < 0:
            y.append(base_price * (1 + t * 0.3))
        elif t < 2:
            y.append(base_price * (1 + t * 0.6))
        else:
            y.append(base_price * (1 + t * 1.2))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, name="Price Curve"))

    fig.update_layout(
        title="Uranium Price vs Market Tightness",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)