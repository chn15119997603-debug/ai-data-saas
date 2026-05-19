import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# =====================
# 🤖 GPT客户端
# =====================
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

# =====================
# 🚀 页面
# =====================
st.set_page_config(
    page_title="AI SaaS双模型分析",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 AI商业分析SaaS（GPT + 千问）")

FREE_LIMIT = 3

if "count" not in st.session_state:
    st.session_state.count = 0

# =====================
# 🌐 侧边栏
# =====================
with st.sidebar:
    st.header("📊 用户中心")
    st.write(f"已使用：{st.session_state.count}/{FREE_LIMIT}")
    st.markdown("---")
    st.subheader("🤖 AI状态")
    st.write("GPT：🟢")
    st.write("千问：🟡（备用）")

# =====================
# 🌐 爬虫
# =====================
def crawl(url):
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        texts = []
        for a in soup.find_all("a"):
            t = a.get_text(strip=True)
            if t:
                texts.append(t)

        return " ".join(texts)[:1200]

    except Exception as e:
        return f"抓取失败：{e}"

# =====================
# 🤖 GPT
# =====================
def ask_gpt(text):

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "你是商业分析AI"},
            {"role": "user", "content": f"分析网站：{text}"}
        ]
    )

    return res.choices[0].message.content

# =====================
# 🤖 千问（安全版）
# =====================
def ask_qwen(text):

    try:
        import dashscope
        dashscope.api_key = st.secrets["QWEN_API_KEY"]

        response = dashscope.Generation.call(
            model="qwen-turbo",
            prompt=f"""
请分析以下网站内容：

1. 网站类型
2. 核心业务
3. 商业模式
4. 盈利方式
5. 风险
6. 总结

内容：
{text}
"""
        )

        return response.output.text

    except Exception as e:
        return f"千问不可用（已跳过）：{e}"

# =====================
# 🤖 AI选择逻辑
# =====================
def ask_ai(text, mode):

    # GPT优先
    if mode == "GPT":

        return "🟢 GPT结果：\n\n" + ask_gpt(text)

    # 千问备用
    elif mode == "千问":

        return "🟡 千问结果：\n\n" + ask_qwen(text)

    # 自动模式
    else:

        try:
            return "🟢 GPT自动：\n\n" + ask_gpt(text)
        except:
            return ask_qwen(text)

# =====================
# 🌐 输入
# =====================
url = st.text_input("请输入网址")

mode = st.selectbox(
    "选择AI模式",
    ["自动", "GPT", "千问"]
)

# =====================
# 🚀 开始
# =====================
if st.button("开始分析 🚀"):

    if st.session_state.count >= FREE_LIMIT:
        st.error("免费次数已用完")
        st.stop()

    if not url:
        st.warning("请输入网址")
        st.stop()

    with st.spinner("AI分析中..."):

        text = crawl(url)

        result = ask_ai(text, mode)

        st.session_state.count += 1

        st.success("分析完成")

        st.subheader("📊 分析结果")
        st.write(result)

        st.download_button(
            "📥 下载报告",
            result,
            file_name="report.txt"
        )

# =====================
# 📌 footer
# =====================
st.markdown("---")
st.caption("AI SaaS v1.1 - GPT + 千问双模型版")
