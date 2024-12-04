import os
from client import ChatClient

def analyze_transcript(transcript_path: str, prompt: str, api_key: str):
    """
    分析转录文件内容
    
    Args:
        transcript_path: 转录文件路径
        prompt: 分析提示词
        api_key: Dify API key
        
    Returns:
        str: 分析结果，如果失败返回 None
    """
    try:
        # 读取转录文件
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript = f.read()
            
        # 创建 Dify 客户端
        client = ChatClient(api_key)
        
        # 发送分析请求
        response = client.create_chat_message(
            inputs={},
            query=f"基于以下提示词分析新闻内容：\n\n{prompt}\n\n新闻内容：\n{transcript}",
            user="news_analyzer",
            response_mode="blocking"
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', '')
            
            # 保存分析结果
            output_dir = "analysis_results"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            filename = os.path.basename(transcript_path)
            base_name = os.path.splitext(filename)[0]
            output_path = os.path.join(output_dir, f"{base_name}_analysis.txt")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(answer)
                
            print(f"分析结果已保存到: {output_path}")
            return answer
            
        else:
            print(f"API 请求失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"分析过程中出错: {str(e)}")
        return None 