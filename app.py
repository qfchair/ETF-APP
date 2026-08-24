import streamlit as st
import requests
import pandas as pd
import time

# 1. 網頁基本設定
st.set_page_config(page_title="ETF 即時盤中監控", layout="wide")
st.title("📊 ETF 即時股價與預估淨值儀表板")

# 2. 側邊欄：使用者可自行調整參數
st.sidebar.header("控制台")
etf_input = st.sidebar.text_input("請輸入要監控的 ETF 代號 (逗號分隔)", "0050, 00878, 0056")
refresh_sec = st.sidebar.slider("自動刷新間隔 (秒)", 3, 30, 5)

etf_list = [e.strip() for e in etf_input.split(",") if e.strip()]

# 3. 爬取證交所 MIS 即時 API
def get_etf_data(code):
    url = f"https://mis.twse.com.tw/stock/api/getEtfInfo.jsp?ex_ch=tse_{code}.tw"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=3)
        data = r.json()
        if "msgArray" in data and len(data["msgArray"]) > 0:
            info = data["msgArray"][0]
            z = info.get("z", "-")                  # 即時成交價
            b = info.get("b", "-").split("_")[0]    # 委買一
            a = info.get("a", "-").split("_")[0]    # 委賣一
            nav = info.get("f", info.get("eb", "-"))# 預估淨值
            
            # 計算折溢價率
            discount = "-"
            if z != "-" and nav != "-" and float(nav) > 0:
                diff = float(z) - float(nav)
                discount = f"{(diff / float(nav)) * 100:+.2f}%"

            return {
                "ETF代號": code,
                "名稱": info.get("n", "-"),
                "成交價": z,
                "最佳委買": b,
                "最佳委賣": a,
                "預估淨值": nav,
                "折溢價率": discount,
                "更新時間": info.get("t", "-")
            }
    except:
        pass
    return None

# 4. 抓取資料並呈現於畫面上
rows = []
for code in etf_list:
    res = get_etf_data(code)
    if res:
        rows.append(res)

if rows:
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)
    st.caption(f"最後更新時間：{time.strftime('%H:%M:%S')}")
else:
    st.warning("目前無法取得資料，請確認台股是否在盤中交易時間，或代號是否正確。")

# 5. 秒數倒數後自動刷新網頁
time.sleep(refresh_sec)
st.rerun()
