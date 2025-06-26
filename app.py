import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import streamlit as st

def get_gold_prices(date_str):
    url = f"https://rate.bot.com.tw/gold/quote/{date_str}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        target_section = None
        for td in soup.select("td"):
            if "臺銀金鑽條塊" in td.text:
                target_section = td.find_parent("table")
                break
        if not target_section:
            return None

        rows = target_section.find_all("tr")
        result = {}
        for tr in rows:
            cells = tr.find_all("td")
            for i, cell in enumerate(cells):
                if "本行賣出" in cell.text:
                    result["sell"] = cells[i + 1].text.strip().replace(",", "")
                elif "本行買進" in cell.text:
                    result["buy"] = cells[i + 1].text.strip().replace(",", "")
        if "sell" in result and "buy" in result:
            return float(result["sell"]), float(result["buy"])
    except:
        return None

# Streamlit UI
st.title("💰 Taiwan Bank Gold Brick Price Viewer")

start_date = st.date_input("Start Date", datetime.today() - timedelta(days=10))
end_date = st.date_input("End Date", datetime.today())

if start_date > end_date:
    st.error("Start date must be before end date.")
else:
    if st.button("Get Prices"):
        data = []
        current = start_date
        with st.spinner("Fetching data..."):
            while current <= end_date:
                date_str = current.strftime("%Y-%m-%d")
                result = get_gold_prices(date_str)
                if result:
                    sell, buy = result
                    data.append({
                        "Date": date_str,
                        "Bank Sell": sell,
                        "Bank Buy": buy
                    })
                current += timedelta(days=1)

        if data:
            df = pd.DataFrame(data)
            st.success("✅ Data fetched!")
            st.line_chart(df.set_index("Date")[["Bank Sell", "Bank Buy"]])
            st.dataframe(df)
        else:
            st.warning("No data found in the selected date range.")
