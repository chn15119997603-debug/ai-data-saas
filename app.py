import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd


# 🧠 AI爬虫 + 分类
def crawl(url):

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=10)
    except:
        return []

    soup = BeautifulSoup(res.text, "html.parser")

    data = []

    for a in soup.find_all("a"):
        text = a.get_text(strip=True)
        link = a.get("href")

        if not text or not link:
            continue

        if link.startswith("/"):
            link = url.rstrip("/") + link

        # 🤖 AI分类逻辑
        if "商品" in text or "¥" in text or "$" in text:
            tag = "商品"
        elif "新闻" in text:
            tag = "新闻"
        elif "招聘" in text:
            tag = "招聘"
        elif len(text) < 5:
            tag = "链接"
        else:
            tag = "普通内容"

        data.append({
            "内容": text,
            "链接": link,
            "AI分类": tag
        })

    return data


# 🖥️ UI
st.set_page_config(page_title="AI商业数据系统", layout="wide")

st.title("🧠 AI商业级数据分析系统")

url = st.text_input("请输入目标网址")

if st.button("开始AI分析"):

    if url:

        data = crawl(url)

        if len(data) == 0:
            st.warning("没有抓到数据")
        else:

            df = pd.DataFrame(data)

            st.success("AI分析完成")

            # 📊 展示数据
            st.subheader("📊 数据结果")
            st.dataframe(df, use_container_width=True)

            # 📈 统计
            st.subheader("📈 AI统计分析")

            st.write("总数据量：", len(df))
            st.write("商品数量：", len(df[df["AI分类"] == "商品"]))
            st.write("新闻数量：", len(df[df["AI分类"] == "新闻"]))
            st.write("招聘数量：", len(df[df["AI分类"] == "招聘"]))

            # 💾 下载
            st.download_button(
                "下载CSV",
                df.to_csv(index=False).encode("utf-8-sig"),
                "ai_data.csv",
                "text/csv"
            )

            # 🧠 AI总结（简易版）
            st.subheader("🧠 AI分析报告")

            summary = f"""
            该页面共采集 {len(df)} 条数据。
            其中商品 {len(df[df['AI分类']=='商品'])} 条，
            新闻 {len(df[df['AI分类']=='新闻'])} 条，
            招聘 {len(df[df['AI分类']=='招聘'])} 条。

            整体来看，这是一个以“信息展示/链接导航”为主的网页。
            """

            st.write(summary)

    else:
        st.warning("请输入网址")