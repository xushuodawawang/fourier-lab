# fourier-lab

一个基于 `Python + FastAPI + 原生前端` 的傅里叶实验网页，包含：

- 傅里叶级数演示
- 级数到积分的过渡演示
- 频域滤波实验
- 真实图片加噪与滤波
- 基于千问的 AI 助教

## 启动

```bash
python -m pip install -r requirements.txt
python -m uvicorn app:app --reload
```

浏览器打开：

```text
http://127.0.0.1:8000
```

## 测试

```bash
python -m pytest
```

## 说明

- 千问 API Key 从 `.env` 中读取：`DASHSCOPE_API_KEY`
- 默认演示图片为项目根目录下的 `image.png`
