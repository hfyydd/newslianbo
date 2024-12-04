import yt_dlp
import os
from datetime import datetime
import re
import json
import glob
import whisper
import torch
from tqdm import tqdm
import time
from news_analyzer import analyze_transcript

CHINESE_NEWS_ANALYSIS_PROMPT = """
分析新闻和经济信号的关键规则:

1. 外交用语解读:
- "亲切友好的交谈" = 合作可能性大
- "坦率的交谈" = 存在重大分歧
- "交换意见" = 各说各的，未达成共识
- "深度交换意见" = 分歧严重
- "增进双方了解" = 存在显著分歧
- "会谈来之不易" = 双方立场差距大

2. 领导人活动信号:
- 企业参观 = 该公司可能获得政策支持
- 展会出席 = 相关行业将受重视
- 地方考察 = 该地区可能有重要变革
- 随行企业家 = 这些企业短期内相对稳定

3. 人事调动含义:
- 发达地区领导→落后地区 = 后者将获发展机会
- 落后地区领导→发达地区 = 可能趋于保守稳定

4. 政策文件解读:
- 1号文件方向 = 重点扶持领域
- 提到"大力发展" = 该领域将获政策支持
- "鼓励创新" = 相关行业将获资金倾斜

5. 经济预警信号:
- 强调防范风险 = 相关领域可能存在隐患
- 反腐相关报道 = 该行业将被重点整治
- 批评某类行为 = 相关监管政策可能出台

6. 宏观经济指标关注:
- 外汇储备变化 = 关注资金流向
- 房地产政策 = 注意区域发展机会
- 产业结构调整 = 把握转型方向

7. 舆论导向解读:
- 正面表扬 = 该领域将获支持
- 批评报道 = 可能涉及监管收紧
- "典型案例" = 该领域将被重点关注

8. 投资机会识别:
- 政策支持行业 = 提前布局机会
- 区域发展规划 = 关注区域龙头企业
- 产业升级方向 = 寻找细分领域机会

注意事项:
1. 需要多维度交叉验证信息
2. 关注政策落地的时间周期
3. 警惕过度解读带来的风险
4. 结合具体行业特点分析
5. 考虑宏观经济环境影响
"""

def transcribe_video(video_path, date_str, st_status=None):
    """
    使用 Whisper 模型提取视频中的文字
    
    Args:
        video_path: 视频文件路径
        date_str: 日期字符串，用于生成输出文件名
        st_status: Streamlit status 对象，用于显示进度
    
    Returns:
        转录文本文件的路径，如果失败则返回 None
    """
    # 检查视频文件是否存在
    if not os.path.exists(video_path):
        if st_status:
            st_status.error(f"错误：视频文件不存在: {video_path}")
        print(f"错误：视频文件不存在: {video_path}")
        return None
        
    transcripts_dir = "transcripts"
    if not os.path.exists(transcripts_dir):
        os.makedirs(transcripts_dir)
        
    output_file = os.path.join(transcripts_dir, f"{date_str}_transcript.txt")
    
    # 检查是否已存在转录文件
    if os.path.exists(output_file):
        if st_status:
            st_status.success(f"已找到转录文件: {output_file}")
        print(f"已找到转录文件: {output_file}")
        return output_file
    
    try:
        # 命令行进度显示
        print("正在加载 Whisper 模型...")
        
        # Streamlit进度显示
        if st_status:
            st_status.write("正在加载 Whisper 模型...")
            progress = st_status.progress(0)
            
        # 使用tqdm显示模型加载进度
        with tqdm(total=100, desc="加载模型") as pbar:
            model = whisper.load_model("medium")
            pbar.update(100)
            
        if st_status:
            progress.progress(100)
            st_status.write("模型加载完成！")
            st_status.write("\n开始转录视频...")
            progress.progress(0)
            
        print("\n开始转录视频...")
        print("转录过程可能需要几分钟，请耐心等待...")
        
        start_time = time.time()
        video_path = os.path.abspath(video_path)
        
        if st_status:
            # 添加一个容器来显示实时转录进度
            transcript_container = st_status.empty()
            
        # 创建转录进度显示
        with tqdm(total=100, desc="转录进度") as pbar:
            def progress_callback(prog, text=None, start_time=None, end_time=None):
                pbar.update(int(prog * 100) - pbar.n)
                if st_status:
                    progress.progress(int(prog * 100))
                    # 显示当前转录的时间段和内容
                    if text and start_time is not None and end_time is not None:
                        time_info = f"[{start_time:.2f} --> {end_time:.2f}] "
                        transcript_container.markdown(f"```\n{time_info}{text}\n```")
            
            # 开始转录，使用简体中文配置
            result = model.transcribe(
                str(video_path),
                language="zh",
                task="transcribe",
                initial_prompt="以下是简体中文新闻内容：",
                verbose=True,
                word_timestamps=True  # 启用词级时间戳
            )
            
            # 显示转录进度
            if st_status and 'segments' in result:
                for segment in result['segments']:
                    progress_callback(
                        segment['end'] / result['segments'][-1]['end'],
                        segment['text'],
                        segment['start'],
                        segment['end']
                    )
            
            pbar.update(100)  # 确保进度条完成
            
        if st_status:
            progress.progress(100)
        
        # 计算耗时
        duration = time.time() - start_time
        
        # 保存转录结果
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result["text"])
        
        # 显示完成信息
        success_msg = f"✓ 转录完成! 总耗时: {duration:.2f} 秒"
        print(f"\n{success_msg}")
        if st_status:
            st_status.success(success_msg)
        
        return output_file
        
    except Exception as e:
        error_msg = f"转录过程中出现错误: {str(e)}"
        print(f"\n❌ {error_msg}")
        if st_status:
            st_status.error(error_msg)
        import traceback
        traceback_info = traceback.format_exc()
        print(traceback_info)
        if st_status:
            st_status.error(traceback_info)
        return None

def get_news_video(date_str):
    """
    从 YouTube 获取指定日期的新闻联播视频
    
    Args:
        date_str: 日期字符串，格式为 'YYYYMMDD'，例如 '20231201'
    
    Returns:
        下载视频的本地路径，如果下载失败则返回None
    """
    playlist_url = "https://www.youtube.com/playlist?list=PL0eGJygpmOH5xQuy8fpaOvKrenoCsWrKh"
    download_dir = "downloads"
    
    # 创建下载目录
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    # 检查是否已经存在包含指定日期的视频文件
    existing_files = glob.glob(os.path.join(download_dir, f"*{date_str}*.mp4"))
    if existing_files:
        print(f"找到已下载的视频: {existing_files[0]}")
        return existing_files[0]
    
    try:
        # 配置yt-dlp选项
        ydl_opts = {
            'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b',  # 优先选择mp4格式
            'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': True,
            'extract_flat': True,  # 不下载，只获取信息
        }
        
        # 首先获取播放列表信息
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(playlist_url, download=False)
            
            # 遍历播放列表中的视频
            for entry in playlist_info['entries']:
                if not entry:
                    continue
                    
                video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                title = entry.get('title', '')
                
                # 检查日期是否匹配
                if date_str in title:
                    print(f"找到匹配的视频: {title}")
                    
                    # 更新下载选项，使用更灵活的格式选择
                    download_opts = {
                        'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b',
                        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
                        'quiet': False,
                        'no_warnings': True,
                        'merge_output_format': 'mp4',  # 合并为mp4格式
                        'postprocessors': [{
                            'key': 'FFmpegVideoConvertor',
                            'preferedformat': 'mp4',  # 转换为mp4格式
                        }],
                    }
                    
                    # 下载视频
                    print("开始下载视频...")
                    with yt_dlp.YoutubeDL(download_opts) as ydl:
                        try:
                            # 先获取可用格式
                            info = ydl.extract_info(video_url, download=False)
                            # 下载视频
                            ydl.download([video_url])
                            # 获取输出文件路径
                            video_path = os.path.join(download_dir, f"{info['title']}.mp4")
                            print(f"视频已下载到: {video_path}")
                            return video_path
                        except Exception as e:
                            print(f"下载视频时出错: {str(e)}")
                            # 如果出错，尝试使用最基本的格式
                            download_opts['format'] = 'best'
                            ydl.download([video_url])
                            video_path = os.path.join(download_dir, f"{info['title']}.mp4")
                            return video_path
        
        print(f"找到日期为 {date_str} 的视频")
        return None
        
    except Exception as e:
        print(f"下载过程中出现错误: {str(e)}")
        return None

def check_transcript_exists(date_str):
    """
    检查指定日期的转录文件是否存在
    
    Args:
        date_str: 日期字符串，格式为 'YYYYMMDD'
    
    Returns:
        bool: 如果转录文件存在返回 True，否则返回 False
        str: 如果存在则返回文件路径，否则返回 None
    """
    transcripts_dir = "transcripts"
    transcript_path = os.path.join(transcripts_dir, f"{date_str}_transcript.txt")
    
    if os.path.exists(transcript_path):
        # 检查文件是否为空
        if os.path.getsize(transcript_path) > 0:
            return True, transcript_path
    return False, None

if __name__ == "__main__":
    date_str = '20241130'  # 这里改为你想下载的日期
    api_key = "app-7mN6qPRFPHT5DjJlTqZCBqSz"  # 替换为您的 Dify API key
    
    # 首先检查转录文件是否存在
    exists, transcript_path = check_transcript_exists(date_str)
    
    if exists:
        print(f"已找到{date_str}的转录文件: {transcript_path}")
    else:
        print(f"未找到{date_str}的转录文件，开始处理...")
        video_path = get_news_video(date_str)
        if video_path:
            transcript_path = transcribe_video(video_path, date_str)
            if not transcript_path:
                print("转录失败")
                exit(1)
        else:
            print("获取视频失败")
            exit(1)
    
    # 调用 Dify 进行分析
    print("\n开始分析转录内容...")
    result = analyze_transcript(
        transcript_path=transcript_path,
        prompt=CHINESE_NEWS_ANALYSIS_PROMPT,
        api_key=api_key
    )
    
    if result:
        print("\n分析完成!")
    else:
        print("\n分析失败!")
