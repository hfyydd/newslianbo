import streamlit as st
import datetime
from get_news import check_transcript_exists, get_news_video, transcribe_video, CHINESE_NEWS_ANALYSIS_PROMPT
from client import ChatClient
import os

# 设置页面配置
st.set_page_config(
    page_title="新闻联播分析助手",
    page_icon="📺",
    layout="wide"
)

# 初始化会话状态
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'conversation_id' not in st.session_state:
    st.session_state.conversation_id = None
if 'client' not in st.session_state:
    st.session_state.client = ChatClient("app-7mN6qPRFPHT5DjJlTqZCBqSz")

def process_news(date_str):
    """处理指定日期的新闻"""
    exists, transcript_path = check_transcript_exists(date_str)
    
    if exists:
        st.success(f"已找到{date_str}的转录文件")
    else:
        with st.status("正在处理新闻...", expanded=True) as status:
            st.write("开始下载视频...")
            video_path = get_news_video(date_str)
            if video_path:
                st.write("视频下载完成，开始转录...")
                
                # 创建一个专门的区域显示转录进度
                transcript_progress = st.empty()
                with transcript_progress.container():
                    st.markdown("### 转录进度")
                    transcript_path = transcribe_video(video_path, date_str, status)
                
                if not transcript_path:
                    st.error("转录失败")
                    return None
                st.write("转录完成！")
            else:
                st.error("获取视频失败")
                return None
            status.update(label="处理完成！", state="complete")
    
    return transcript_path

def analyze_news(transcript_path):
    """分析新闻内容"""
    with open(transcript_path, 'r', encoding='utf-8') as f:
        transcript = f.read()
    
    # 发送分析请求
    response = st.session_state.client.create_chat_message(
        inputs={},
        query=f"基于以下提示词分析新闻内容：\n\n{CHINESE_NEWS_ANALYSIS_PROMPT}\n\n新闻内容：\n{transcript}",
        user="news_analyzer",
        response_mode="blocking",
        conversation_id=st.session_state.conversation_id
    )
    
    if response.status_code == 200:
        result = response.json()
        st.session_state.conversation_id = result.get('conversation_id')
        return result.get('answer', '')
    return None

def main():
    st.title("📺 新闻联播分析助手")
    
    # 日期选择器
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_date = st.date_input(
            "选择日期",
            datetime.date.today(),
            format="YYYY/MM/DD"
        )
    with col2:
        if st.button("开始分析", type="primary"):
            date_str = selected_date.strftime("%Y%m%d")
            transcript_path = process_news(date_str)
            
            if transcript_path:
                analysis = analyze_news(transcript_path)
                if analysis:
                    st.session_state.messages.append({"role": "assistant", "content": analysis})
                else:
                    st.error("分析失败")
    
    # 显示聊天历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 聊天输入框
    if prompt := st.chat_input("输入您的问题"):
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # 获取AI响应
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                response = st.session_state.client.create_chat_message(
                    inputs={},
                    query=prompt,
                    user="news_analyzer",
                    conversation_id=st.session_state.conversation_id
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get('answer', '')
                    st.session_state.conversation_id = result.get('conversation_id')
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    st.markdown(answer)
                else:
                    st.error("获取回答失败")
    
    # 添加页面底部免责声明
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
    ⚠️ 免责声明：本工具的分析内容由 AI 大模型生成，仅供参考。请您仔细甄别信息，谨慎使用。
    </div>
    """, unsafe_allow_html=True)

# 添加侧边栏说明
def add_sidebar():
    with st.sidebar:
        st.markdown("""
        ### 使用说明
        1. 选择想要分析的新闻日期
        2. 点击"开始分析"按钮
        3. 等待系统完成下载和分析
        4. 在对话框中提问，进行深入交流
        
        ### 功能特点
        - 自动下载指定日期的新闻联播
        - 智能分析新闻内容
        - 支持上下文对话
        - 保存分析结果
        
        ### 提示规则
        """)
        st.markdown(CHINESE_NEWS_ANALYSIS_PROMPT)

if __name__ == "__main__":
    add_sidebar()
    main() 