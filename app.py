import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from openai import OpenAI

# =====================
# 🔑 填你的API Key（重要）
# =====================
client = OpenAI(api_key="在这里填你的API_KEY")

# =====================
# 爬虫函数
# =====================
def crawl(url):

    headers = {"User-Agent": "Mozilla/5.0"}

    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    data = []

    for a in soup.find_all("a"):
        text = a.get_text(strip=True)
        link = a.get("href")

        if not text or not link:
            continue

        data.append(text)

    return data


# =====================
# 🤖 GPT分析函数
# =====================
def ai_analyze(text):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "你是一个商业分析AI助手"
            },
            {
                "role": "user",
                "content": f"""
请分析以下网页内容：

1. 网站类型
2. 主要业务
3. 商业价值（高/中/低）
4. 是否适合做竞品
5. 总结

内容：
{text}
"""
            }
        ]
    )

    return response.choices[0].message.content


# =====================
# 🌐 页面
# =====================
st.title("🧠 AI GPT网页分析SaaS")

url = st.text_input("输入网址")

if st.button("开始分析"):

    if url:

        with st.spinner("AI正在分析中..."):

            data = crawl(url)

            text = " ".join(data)

            result = ai_analyze(text)

        st.success("分析完成")

        st.subheader("🤖 AI分析报告")
        st.write(result)

    else:
        st.warning("请输入网址")
