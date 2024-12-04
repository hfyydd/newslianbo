# 新闻联播分析助手 📺

一个基于 AI 的新闻联播智能分析工具，可以自动下载、转录和分析新闻联播内容，并支持智能问答交互。

## 功能特点

- 🎥 自动下载指定日期的新闻联播视频
- 🔊 使用 Whisper 模型进行语音转录
- 📊 智能分析新闻内容和政策导向
- 💬 支持上下文对话和深入提问
- 📱 友好的 Web 界面（基于 Streamlit）

## 安装说明

1. 克隆项目并安装依赖：

```bash
git clone https://github.com/hfyydd/newslianbo
cd news-analysis
pip install -r requirements.txt
```




2. 配置 API Key：
```bash
   - 获取 [Dify](https://dify.ai) API Key
   - 在 app.py 中替换 API Key
```



## 使用方法

1. 启动应用：
```bash
streamlit run app.py
```

2. 在浏览器中访问应用（默认地址：http://localhost:8501）

3. 使用流程：
   - 选择想要分析的新闻日期
   - 点击"开始分析"按钮
   - 等待系统完成下载和转录
   - 查看分析结果
   - 在对话框中提问，进行深入交流

## 项目结构
```bash
.
├── app.py # Streamlit 主应用
├── get_news.py # 新闻下载和转录模块
├── news_analyzer.py # 新闻分析模块
├── client.py # Dify API 客户端
├── downloads/ # 视频下载目录
├── transcripts/ # 转录文本存储
└── analysis_results/ # 分析结果存储
```


## 分析规则

系统基于以下维度分析新闻内容：

1. 外交用语解读
   - "亲切友好的交谈" = 合作可能性大
   - "坦率的交谈" = 存在重大分歧
   - "交换意见" = 各说各的，未达成共识

2. 领导人活动信号
   - 企业参观 = 该公司可能获得政策支持
   - 展会出席 = 相关行业将受重视
   - 地方考察 = 该地区可能有重要变革

3. 人事调动含义
   - 发达地区领导→落后地区 = 后者将获发展机会
   - 落后地区领导→发达地区 = 可能趋于保守稳定

4. 政策文件解读
   - 1号文件方向 = 重点扶持领域
   - 提到"大力发展" = 该领域将获政策支持
   - "鼓励创新" = 相关行业将获资金倾斜

5. 经济预警信号
   - 强调防范风险 = 相关领域可能存在隐患
   - 反腐相关报道 = 该行业将被重点整治
   - 批评某类行为 = 相关监管政策可能出台

## 技术依赖
```bash
- Python 3.8+
- Streamlit
- OpenAI Whisper
- yt-dlp
- PyTorch
- Dify API
```

## 环境要求
```bash
- 操作系统：Windows/Linux/MacOS
- Python 版本：3.8 或更高
- 内存：建议 8GB 以上
- 磁盘空间：建议预留 10GB 以上（用于存储视频和模型）
- GPU：可选（有 GPU 可加速转录过程）
```
## 常见问题

1. 视频下载失败
   - 检查网络连接
   - 确认 YouTube 可访问
   - 验证日期格式是否正确

2. 转录失败
   - 确保已安装 FFmpeg
   - 检查视频文件完整性
   - 确认系统内存充足

3. 分析失败
   - 验证 API Key 是否正确
   - 检查网络连接
   - 确认转录文件存在且非空

## 更新日志

### v1.0.0 (2023-12-04)
- 初始版本发布
- 支持视频下载和转录
- 集成 Dify 分析功能
- 添加 Web 界面

## License

MIT License

## 免责声明

本工具的分析内容由 AI 大模型生成，仅供参考。请您仔细甄别信息，谨慎使用。不对因使用本工具产生的任何后果承担责任。

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。提交时请：

1. Fork 项目并创建新分支
2. 遵循现有代码风格
3. 更新相关文档
4. 提交前进行充分测试

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue

## 致谢

感谢以下开源项目的支持：

- [Streamlit](https://streamlit.io/)
- [Whisper](https://github.com/openai/whisper)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [Dify](https://dify.ai/)