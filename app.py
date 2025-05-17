
import streamlit as st
import pandas as pd
import numpy as np
import openai

# Title and Instructions
st.title("Contract Coverage & Opportunity Analyzer")
st.write("Upload your procurement spend data to analyze contract coverage and identify areas needing attention.")

# File upload
uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    try:
        # Read file based on extension
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Validate columns
        expected_cols = ["Category", "Supplier", "Spend", "Contract in Place"]
        if not all(col in df.columns for col in expected_cols):
            st.error("File must contain the following columns: Category, Supplier, Spend, Contract in Place")
        else:
            # Group and analyze
            summary = df.groupby(['Category', 'Contract in Place'])['Spend'].sum().unstack(fill_value=0)
            summary['Total Spend'] = summary.sum(axis=1)
            summary['% Uncontracted'] = (summary.get("No", 0) / summary['Total Spend']) * 100
            summary['Action Needed'] = np.where(
                (summary.get("No", 0) > 100000) | (summary['% Uncontracted'] > 30), 
                "Yes", 
                "No"
            )

            # Show summary
            st.subheader("Analysis Summary")
            st.dataframe(summary.round(2))

            # Recommendations using OpenAI (optional, needs API key)
            openai_api_key = st.text_input("Enter OpenAI API Key for recommendations (optional)", type="password")
            if openai_api_key:
                openai.api_key = openai_api_key
                st.subheader("AI-Powered Recommendations")
                for category, row in summary.iterrows():
                    if row['Action Needed'] == "Yes":
                        prompt = f"Provide recommendations to improve contract coverage for the procurement category '{category}' with {row['% Uncontracted']:.1f}% of spend uncontracted and total spend of ${row['Total Spend']:,.0f}."
                       client = openai.OpenAI(api_key=openai_api_key)
client = openai.OpenAI(api_key=openai_api_key)
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)
                        st.markdown(f"**{category}:** {response.choices[0].message['content']}")

    except Exception as e:
        st.error(f"An error occurred: {e}")
