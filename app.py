import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="竞品商业分析AI", page_icon="📊")

st.title("📊 AI竞品商业分析（合法版）")

url = st.text_input("输入目标网站")

# =====================
# 🌐 抓公开数据
# =====================
def crawl(url):
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    return {
        "title": soup.title.string if soup.title else "未知",
        "links": len(soup.find_all("a")),
        "images": len(soup.find_all("img")),
        "text_len": len(soup.get_text())
    }

# =====================
# 📊 商业推算模型
# =====================
def estimate(data):

    traffic_index = data["links"] * 10 + data["images"] * 5 + data["text_len"] / 1000

    conversion_rate = 0.02
    avg_price = 99

    users = int(traffic_index * conversion_rate)
    revenue = users * avg_price

    return {
        "流量指数": round(traffic_index),
        "估算用户数": users,
        "基础用户(70%)": int(users * 0.7),
        "高级用户(25%)": int(users * 0.25),
        "企业用户(5%)": int(users * 0.05),
        "日收入估算(元)": revenue
    }

# =====================
# 🚀 执行
# =====================
if st.button("开始分析"):

    if not url:
        st.warning("请输入网址")
        st.stop()

    data = crawl(url)
    result = estimate(data)

    st.subheader("📊 网站公开数据")
    st.write(data)

    st.subheader("💰 商业模型推算")
    st.write(result)

    st.info("⚠️ 这是基于公开信息的AI推算，不是后台真实数据")
