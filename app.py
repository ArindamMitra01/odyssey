import streamlit as st
import pandas as pd
import google.generativeai as genai

# Page Configuration
st.set_page_config(page_title="Agentic Finance Co-pilot", layout="wide")

# --- SIDEBAR: API CONFIGURATION ---
st.sidebar.title("Configuration")
api_key = st.sidebar.text_input("Enter your Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    st.sidebar.success("API Key configured!")
else:
    st.sidebar.warning("Please enter your Gemini API Key to enable AI features.")

# --- MAIN INTERFACE ---
st.title("💰 Agentic Finance Co-pilot")
st.markdown("Upload your `transactions.csv` to analyze your spending habits with AI.")

# File Uploader
uploaded_file = st.file_uploader("Choose your transactions CSV file", type="csv")

if uploaded_file is not None:
    # Read the CSV
    df = pd.read_csv(uploaded_file)
    
    # Display the Data
    st.subheader("Transaction History")
    st.dataframe(df, use_container_width=True)
    
    # Simple Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Transactions", len(df))
    with col2:
        st.metric("Total Spend", f"₹{df['Amount'].sum():,.2f}")
    with col3:
        st.metric("Average Transaction", f"₹{df['Amount'].mean():,.2f}")

    # --- AI ANALYSIS SECTION ---
    st.divider()
    st.subheader("🤖 Ask the Co-pilot")
    user_question = st.text_input("e.g., 'What are my top 3 spending categories?' or 'Summarize my monthly budget'")

    if st.button("Run AI Analysis"):
        if not api_key:
            st.error("Please enter an API Key in the sidebar first.")
        else:
            try:
                # Prepare the data context for the LLM
                data_summary = df.to_string(index=False)
                prompt = f"""
                You are a professional financial advisor. Here is a list of transactions:
                {data_summary}
                
                User Question: {user_question}
                
                Provide a concise, helpful, and professional answer based only on the data provided.
                """
                
                model = genai.GenerativeModel('gemini-1.5-flash')
                with st.spinner("Analyzing your finances..."):
                    response = model.generate_content(prompt)
                    st.markdown("### Co-pilot Advice:")
                    st.write(response.text)
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")

else:
    st.info("Waiting for CSV file upload...")