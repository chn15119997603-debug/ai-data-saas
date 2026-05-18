import streamlit as st
import json
import os
from openai import OpenAI
import requests
from bs4 import BeautifulSoup

# ========== 安全读取 ==========
api_key = st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.error("缺少 OPENAI_API_KEY")
    st.stop()

client = OpenAI(api_key=api_key)

DB_FILE = "users.json"

# ========== 初始化数据库 ==========
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({}, f)

def load_db():
    return json.load(open(DB_FILE))

def save_db(db):
    json.dump(db, open(DB_FILE, "w"))

# ========== 用户 ==========
st.title("💰 AI SaaS商业系统")

email = st.text_input("输入邮箱")

db = load_db()

if email and email not in db:
    db[email] = {"vip": False, "count": 0}
    save_db(db)

vip = db.get(email, {}).get("vip", False)
count = db.get(email, {}).get("count", 0)

# ========== 免费限制 ==========
FREE_LIMIT = 3

# ========== 支付链接（你后面改） ==========
PAY_URL = "https://你的支付链接"

if email and not vip:
    st.sidebar.markdown(f"[💰 升级VIP ¥29]({PAY_URL})")

# ========== 爬虫 ==========
def crawl(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")
    return [a.get_text(strip=True) for a in soup.find_all("a")]

# ========== AI ==========
def ai(text):
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "你是商业分析AI"},
            {"role": "user", "content": text}
        ]
    )
    return res.choices[0].message.content

url = st.text_input("输入网址")

if st.button("开始分析"):

    if not email:
        st.warning("请输入邮箱")
        st.stop()

    if not vip and count >= FREE_LIMIT:
        st.error("免费次数已用完，请升级VIP")
        st.stop()

    if url:

        with st.spinner("AI分析中..."):

            data = crawl(url)
            text = " ".join(data)
            result = ai(text)

            # 更新次数
            if not vip:
                db[email]["count"] = count + 1
                save_db(db)

        st.success("完成")
        st.write(result)

    else:
        st.warning("请输入网址")
