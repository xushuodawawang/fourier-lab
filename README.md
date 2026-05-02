# Fourier Blue Lab

一个基于 `Python + FastAPI + 原生前端` 的傅里叶教学实验网页，用来把教案里的主线

- 傅里叶级数
- 傅里叶积分
- 傅里叶变换
- AI 图像/传感器案例

做成可直接演示、可交互调参的 Web 原型。

## 亮点

- 蓝色渐变、玻璃拟态、卡片化布局，适合课堂展示
- 周期方波谐波叠加与离散频谱联动
- 周期增大时离散谱逼近连续频谱的过渡演示
- 非周期信号 FFT、滤波与逆变换
- 图像频域处理示例，适合讲 AI 图像降噪与频域增强
- 内置随堂检测，形成课堂闭环

## 运行方式

```bash
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

## 项目结构

```text
.
├─ app.py
├─ fourier_lab/
│  └─ analysis.py
├─ static/
│  ├─ css/styles.css
│  └─ js/app.js
├─ templates/
│  └─ index.html
└─ tests/
   └─ test_app.py
```

## GitHub 上传建议

如果本地还没有 Git 仓库，可按下面顺序：

```bash
git init
git add .
git commit -m "Build Fourier Blue Lab teaching prototype"
git branch -M main
git remote add origin https://github.com/<your-name>/<repo>.git
git push -u origin main
```

本项目的 `.gitignore` 已排除 `.env` 和临时目录，避免把本地敏感信息一起提交。
