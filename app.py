import streamlit as st
import pandas as pd
import google.generativeai as genai
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import time

# 1. CORE SYSTEM CONFIG
st.set_page_config(page_title="Agentic Finance Pilot", layout="wide")

# High-End UI Styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    [data-testid="stMetricValue"] { font-size: 1.8rem; color: #00ffcc; font-weight: bold; }
    .ai-briefing {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #00ffcc;
        margin-bottom: 25px;
        color: #e0e0e0;
        max-height: 300px;
        overflow-y: auto;
    }
    .dashboard-header {
        background: linear-gradient(90deg, #1e2130 0%, #0e1117 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- AI Reasoning Engine (FIXED FOR 2026 PRODUCTION) ---
@st.cache_data(show_spinner=False)
def get_ai_analysis(prompt, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"💡 Intelligence Offline: {str(e)}"

# --- Algorithmic Engines ---
def calculate_pbv(df):
    if 'Category' not in df.columns or 'Amount' not in df.columns:
        return 0.0, 0.0
    weights = df.groupby('Category')['Amount'].sum() / df['Amount'].sum()
    indices = {"Food": 4.1, "Shopping": 2.2, "Transport": 4.8, "Bills": 1.7}
    p_cpi = sum(weights.get(cat, 0) * indices.get(cat, 3.4) for cat in weights.index)
    return round(p_cpi, 2), round(p_cpi - 3.4, 2)

def run_gwts_sieve(tickers, goal):
    results = []
    for t in tickers:
        try:
            info = yf.Ticker(t).info
            pe = info.get("trailingPE", 0)
            if pe and pe > 0:
                results.append({
                    "Ticker": t, "Price": info.get("currentPrice"),
                    "PE": pe, "Yield": info.get("dividendYield", 0) or 0,
                    "Sector": info.get("sector")
                })
        except: continue
    df = pd.DataFrame(results)
    if df.empty: return df
    df['rank'] = df['PE'].rank() + (df['Yield'] * 10).rank(ascending=False)
    return df.sort_values('rank').head(3)

# --- 2. SIDEBAR WITH FULL ALGORITHM DOCUMENTATION ---
with st.sidebar:
    st.title("🛡️ System Control")
    with st.expander("🔑 System Authentication", expanded=True):
        api_key = st.text_input("Access Token", type="password")
    st.divider()
    shield = st.toggle("Privacy Shield", value=True)
    objective = st.selectbox("Objective", ["Capital Preservation", "Aggressive Growth"])
    st.divider()
    st.subheader("Algorithmic Logic")
    with st.expander("🔬 GWTS Logic (Market)", expanded=True):
        st.latex(r"Score = \text{rank}(PE) + 10 \cdot \text{rank}(Yield_{inv})")
    with st.expander("🧮 PBV Logic (Variance)", expanded=True):
        st.latex(r"P_{CPI} = \sum_{i=1}^{n} (W_i \times C_i)")
    st.status("Engines: Nominal", state="complete")

if not api_key:
    st.warning("⚠️ Enter Access Token.")
    st.stop()

# --- 3. GLOBAL DASHBOARD HEADER ---
st.markdown('<div class="dashboard-header">', unsafe_allow_html=True)
st.title("Agentic Finance Dashboard")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Current Mode", objective)
k2.metric("Risk Profile", "Conservative" if objective == "Capital Preservation" else "High-Beta")
p_val = st.session_state.get('p_cpi', 0.0)
d_val = st.session_state.get('delta', 0.0)
k3.metric("Personal CPI", f"{p_val}%", f"{d_val}% Variance")
k4.metric("Agent Engine", "Active")
st.markdown('</div>', unsafe_allow_html=True)

# --- 4. FUNCTIONAL TABS ---
t1, t2, t3 = st.tabs(["💰 Ledger Intelligence", "📈 Market Screening", "⚖️ Variance Strategy"])

with t1:
    st.header("Operational Ledger")
    up = st.file_uploader("Upload CSV", type="csv")
    if up:
        df = pd.read_csv(up)
        st.session_state.df = df
        p, d = calculate_pbv(df)
        st.session_state.p_cpi, st.session_state.delta = p, d
        with st.spinner("Analyzing..."):
            prompt = f"Executive summary for {objective} in 3 bullet points. Focus on top variance driver. Under 80 words:\n{df.to_string()}"
            brief = get_ai_analysis(prompt, api_key)
            st.markdown(f'<div class="ai-briefing"><b>🤖 Executive Brief:</b><br>{brief}</div>', unsafe_allow_html=True)
        col_l, col_r = st.columns([2, 1])
        disp = df.copy()
        if shield: disp['Description'] = "PROTECTED_PII"
        col_l.dataframe(disp, use_container_width=True)
        weights = df.groupby('Category')['Amount'].sum()
        fig, ax = plt.subplots(); fig.patch.set_facecolor('#0e1117')
        ax.pie(weights, labels=weights.index, autopct='%1.1f%%', textprops={'color': "w"})
        col_r.pyplot(fig)

with t2:
    st.header("Market Intelligence")
    if st.button("Run Sieve"):
        with st.spinner("Sieving..."):
            res = run_gwts_sieve(["RELIANCE.NS", "TCS.NS", "INFY.NS", "ITC.NS", "HDFCBANK.NS"], objective)
            prompt = f"Justify these 3 assets for {objective} in 3 short points. Max 80 words:\n{res.to_string()}"
            brief = get_ai_analysis(prompt, api_key)
            st.markdown(f'<div class="ai-briefing"><b>🤖 Market Synthesis:</b><br>{brief}</div>', unsafe_allow_html=True)
            st.table(res[["Ticker", "Price", "PE", "Sector", "Yield"]])

with t3:
    st.header("Economic Variance")
    if 'df' in st.session_state:
        p, d = st.session_state.p_cpi, st.session_state.delta
        with st.spinner("Strategy..."):
            prompt = f"Personal CPI is {p}%. List 3 ECE sector hedges (VLSI/Embedded) for {objective}. 3 bullets only, under 80 words."
            brief = get_ai_analysis(prompt, api_key)
            st.markdown(f'<div class="ai-briefing"><b>🤖 Strategy Recommendation:</b><br>{brief}</div>', unsafe_allow_html=True)
        st.metric("Personal CPI Variance", f"{p}%", f"{d}% over baseline")
        st.bar_chart(pd.DataFrame({"Rate": [3.4, p]}, index=["National Avg", "Personal Index"]))
