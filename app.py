import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import hashlib
import time

# =====================
# 🤖 GPT客户端
# =====================
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

# =====================
# 🚀 页面设置
# =====================
st.set_page_config(page_title="AI网页分析工具", page_icon="🚀")

st.title("🚀 GPT网页分析（IP限制版）")

st.write("输入网址，AI帮你分析商业价值")

# =====================
# 🚀 免费次数
# =====================
FREE_LIMIT = 3

# =====================
# 🧠 获取用户IP（核心）
# =====================
def get_user_id():
    try:
        ip = st.context.headers.get("X-Forwarded-For")
        if not ip:
            ip = "unknown_ip"
    except:
        ip = "unknown_ip"

    return hashlib.md5(ip.encode()).hexdigest()

user_id = get_user_id()

# =====================
# 🗄️ 用户存储（内存版）
# =====================
if "users" not in st.session_state:
    st.session_state.users = {}

if user_id not in st.session_state.users:
    st.session_state.users[user_id] = 0

# =====================
# 🌐 爬虫
# =====================
def crawl(url):

    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    texts = []

    for a in soup.find_all("a"):
        t = a.get_text(strip=True)
        if t:
            texts.append(t)

    text = " ".join(texts)

    return text[:1200]

# =====================
# 🤖 GPT分析
# =====================
def ask_gpt(text):

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "你是专业商业分析AI"
                },
                {
                    "role": "user",
                    "content": f"""
请分析以下网站内容：

1. 网站类型
2. 核心业务
3. 商业模式
4. 是否值得模仿
5. 风险分析
6. 总结

内容：
{text}
"""
                }
            ]
        )

        return res.choices[0].message.content

    except Exception as e:
        return f"GPT调用失败：{e}"

# =====================
# 🌐 输入
# =====================
url = st.text_input("请输入网址")

used = st.session_state.users[user_id]

st.sidebar.write(f"已使用：{used}/{FREE_LIMIT}")

# =====================
# 🚀 开始按钮
# =====================
if st.button("开始分析 🚀"):

    # 限制次数
    if used >= FREE_LIMIT:
        st.error("次数已用完")
        st.stop()

    # 空判断
    if not url:
        st.warning("请输入网址")
        st.stop()

    with st.spinner("AI分析中..."):

        try:
            text = crawl(url)
            result = ask_gpt(text)

            # 次数 +1
            st.session_state.users[user_id] += 1

            st.success("分析完成")

            st.subheader("📊 分析结果")
            st.write(result)

            st.download_button(
                "下载报告",
                result,
                file_name="report.txt"
            )

        except Exception as e:
            st.error(f"系统错误：{e}")
