import streamlit as st
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta    


# Function to fetch and parse SEMO XML data
def fetch_parse_semo_report(dt: datetime):
    resource_time = dt.strftime("%Y%m%d%H%M")
    resource_name = f"PUB_5MinImbalPrcSuppInfo_{resource_time}.xml"
    url = f"http://reports.sem-o.com/documents/{resource_name}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        rows = [elem.attrib for elem in root.findall(".//PUB_5MinImbalPrcSuppInfo")]
        if not rows:
            return pd.DataFrame(), f"No data found in report for {dt}"
        return pd.DataFrame(rows), None
    except Exception as e:
        return pd.DataFrame(), str(e)

# Streamlit UI
st.title("SEMO 5-Min Imbalance Price Support Report Viewer")

# Separate date and time inputs
selected_date = st.date_input("Select date")
selected_time = st.time_input("Select time (5-min increments)",step=timedelta(minutes=5), key="selected_time")

# Combine into a datetime object
selected_datetime = datetime.combine(selected_date, selected_time)

# Button to fetch and parse report
if st.button("Fetch Report"):
    df, error = fetch_parse_semo_report(selected_datetime)
    if error:
        st.error(error)
    else:
        st.success(f"Report loaded for {selected_datetime.strftime('%Y-%m-%d %H:%M')}.")
        st.dataframe(df)

        # Optional CSV download
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"SEMO_BM027_{selected_datetime.strftime('%Y%m%d%H%M')}.csv",
            mime="text/csv"
        )
