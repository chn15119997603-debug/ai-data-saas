import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import os
from openai import OpenAI

# =====================
# 🔐 OpenAI
# =====================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# =====================
# 💰 Stripe支付链接（自己替换）
# =====================
STRIPE_URL = "https://buy.stripe.com/你的支付链接"

# =====================
# 📦 本地数据库（JSON文件）
# =====================
DB_FILE = "users.json"

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({}, f)

def load_db():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# =====================
# 🌐 爬虫
# =====================
def crawl(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    return [a.get_text(strip=True) for a in soup.find_all("a") if a.get_text()]

# =====================
# 🤖 AI分析
# =====================
def ai_analyze(text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "你是商业分析AI"},
            {"role": "user", "content": f"分析网站商业价值：\n{text}"}
        ]
    )
    return response.choices[0].message.content

# =====================
# 🌐 页面
# =====================
st.title("💰 零环境AI SaaS（可收费版）")

email = st.text_input("输入邮箱（用于登录）")

db = load_db()

# =====================
# 👤 用户初始化
# =====================
if email and email not in db:
    db[email] = {"vip": False}
    save_db(db)

vip = email and db.get(email, {}).get("vip", False)

# =====================
# 💳 支付入口
# =====================
if email and not vip:
    st.sidebar.markdown(f"[💎 升级VIP ¥29/月]({STRIPE_URL})")

    if st.sidebar.button("✔ 我已支付（点击解锁VIP）"):
        db[email]["vip"] = True
        save_db(db)
        st.sidebar.success("VIP已开通 🎉")
        vip = True

# =====================
# 输入
# =====================
url = st.text_input("输入网址")

# =====================
# 🚀 执行
# =====================
if st.button("开始分析"):

    if not url:
        st.warning("请输入网址")
        st.stop()

    if not vip:
        st.warning("你是免费用户（VIP无限使用）")

    with st.spinner("AI分析中..."):

        data = crawl(url)
        text = " ".join(data)

        result = ai_analyze(text)

    st.success("分析完成")
    st.subheader("📊 AI报告")
    st.write(result)

    st.download_button("下载报告", result, "report.txt")
