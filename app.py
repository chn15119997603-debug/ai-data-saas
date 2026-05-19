import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import dashscope

# =====================
# 🤖 GPT客户端
# =====================
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

# =====================
# 🚀 页面设置
# =====================
st.set_page_config(
    page_title="AI网页分析SaaS",
    page_icon="🚀"
)

st.title("🚀 GPT + 千问 AI网页分析")

st.write("输入网址，AI帮你分析网站商业价值")

# =====================
# 🚀 免费次数
# =====================
FREE_LIMIT = 3

if "count" not in st.session_state:
    st.session_state.count = 0

st.sidebar.write(f"剩余次数：{FREE_LIMIT - st.session_state.count}")

# =====================
# 🌐 输入网址
# =====================
url = st.text_input("请输入网址")

# =====================
# 🌐 爬虫
# =====================
def crawl(url):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(
        url,
        headers=headers,
        timeout=10
    )

    soup = BeautifulSoup(r.text, "html.parser")

    texts = []

    for a in soup.find_all("a"):

        t = a.get_text(strip=True)

        if t:
            texts.append(t)

    text = " ".join(texts)

    # 防止token太大
    return text[:1200]

# =====================
# 🤖 千问AI
# =====================
def ask_qwen(text):

    try:

        dashscope.api_key = st.secrets["QWEN_API_KEY"]

        response = dashscope.Generation.call(
            model="qwen-turbo",
            prompt=f"""
请分析以下网站内容：

1. 网站类型
2. 核心业务
3. 商业模式
4. 是否值得模仿
5. 风险分析
6. 总结建议

内容：
{text}
"""
        )

        return "🟡 千问结果：\n\n" + response.output.text

    except Exception as e:

        return f"千问失败：{e}"

# =====================
# 🤖 GPT + 千问自动切换
# =====================
def ask_ai(text):

    # 先用GPT
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
6. 总结建议

内容：
{text}
"""
                }
            ]
        )

        return "🟢 GPT结果：\n\n" + res.choices[0].message.content

    except Exception as e:

        st.warning("GPT失败，自动切换千问AI")

        return ask_qwen(text)

# =====================
# 🚀 开始按钮
# =====================
if st.button("开始分析 🚀"):

    # 次数限制
    if st.session_state.count >= FREE_LIMIT:

        st.error("免费次数已用完")
        st.stop()

    # 空判断
    if not url:

        st.warning("请输入网址")
        st.stop()

    with st.spinner("AI分析中..."):

        try:

            # 爬网页
            text = crawl(url)

            # AI分析
            result = ask_ai(text)

            # 次数+1
            st.session_state.count += 1

            # 输出
            st.success("分析完成")

            st.subheader("📊 分析结果")

            st.write(result)

            # 下载按钮
            st.download_button(
                "下载报告",
                result,
                file_name="report.txt"
            )

        except Exception as e:

            st.error(f"系统错误：{e}")
