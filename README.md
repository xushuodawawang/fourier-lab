# fourier-lab

一个真正面向 `Streamlit` 部署的傅里叶实验室，包含：

- 傅里叶级数逼近
- 级数到积分的频谱过渡
- 傅里叶变换与频域滤波
- 基于 `image.png` 的图像加噪与降噪
- 基于千问 API 的 AI 助教
- 课堂小测

## 本地启动

```bash
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

也可以直接运行：

```bash
python app.py
```

## Streamlit Cloud 部署

1. 将仓库连接到 Streamlit Community Cloud。
2. Main file path 填 `streamlit_app.py`。
3. 在应用的 Secrets 中配置：

```toml
DASHSCOPE_API_KEY = "你的千问 API Key"
DASHSCOPE_MODEL = "qwen-plus"
```

可选：

```toml
DASHSCOPE_CHAT_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
```

## 测试

```bash
python -m pytest
```

## 说明

- 本地图像演示默认读取仓库根目录下的 `image.png`
- AI 助教优先读取环境变量，其次读取 `.env`，在 Streamlit Cloud 中也支持 `st.secrets`
