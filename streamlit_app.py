from __future__ import annotations

import base64
import io
import json
from typing import Any

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

from fourier_lab.ai import ask_ai_tutor, has_ai_credentials, test_ai_connection
from fourier_lab.analysis import (
    fourier_series_demo,
    image_demo,
    quiz_questions,
    series_to_integral_demo,
    transform_demo,
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(96, 165, 250, 0.32), transparent 28%),
                radial-gradient(circle at bottom right, rgba(14, 165, 233, 0.22), transparent 24%),
                linear-gradient(135deg, #f6fbff 0%, #e8f2ff 42%, #f8fbff 100%);
        }
        .block-container {
            padding-top: 1.6rem;
            padding-bottom: 2rem;
            max-width: 1380px;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #123a8f 58%, #1d4ed8 100%);
        }
        [data-testid="stSidebar"] * {
            color: #eff6ff;
        }
        .hero-card {
            background: linear-gradient(135deg, rgba(29, 78, 216, 0.96), rgba(14, 165, 233, 0.88));
            color: white;
            border-radius: 28px;
            padding: 2rem 2.15rem;
            box-shadow: 0 26px 60px rgba(37, 99, 235, 0.22);
            border: 1px solid rgba(255, 255, 255, 0.18);
            margin-bottom: 0.8rem;
        }
        .hero-badge {
            display: inline-flex;
            padding: 0.34rem 0.78rem;
            border-radius: 999px;
            font-size: 0.82rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            background: rgba(255, 255, 255, 0.16);
            border: 1px solid rgba(255, 255, 255, 0.22);
            margin-bottom: 0.95rem;
        }
        .hero-title {
            font-size: 2.65rem;
            font-weight: 700;
            line-height: 1.05;
            margin: 0;
        }
        .hero-copy {
            margin: 0.8rem 0 0;
            max-width: 46rem;
            font-size: 1.03rem;
            color: rgba(239, 246, 255, 0.92);
        }
        .panel-card {
            background: rgba(255, 255, 255, 0.76);
            border: 1px solid rgba(148, 163, 184, 0.22);
            border-radius: 22px;
            box-shadow: 0 16px 40px rgba(148, 163, 184, 0.14);
            padding: 1rem 1.1rem;
            margin-bottom: 1rem;
            backdrop-filter: blur(14px);
        }
        .metric-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.88), rgba(238,246,255,0.72));
            border: 1px solid rgba(125, 171, 255, 0.22);
            border-radius: 20px;
            padding: 1rem 1.05rem;
            box-shadow: 0 16px 36px rgba(59, 130, 246, 0.12);
            min-height: 120px;
        }
        .metric-label {
            font-size: 0.82rem;
            color: #33589d;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }
        .metric-value {
            margin-top: 0.45rem;
            font-size: 1.8rem;
            line-height: 1.05;
            color: #0f172a;
            font-weight: 700;
        }
        .metric-note {
            margin-top: 0.45rem;
            font-size: 0.9rem;
            color: #475569;
        }
        .caption-line {
            font-size: 0.92rem;
            color: #52637f;
            margin-top: 0.25rem;
        }
        div[data-testid="stTabs"] button[role="tab"] {
            border-radius: 999px;
            border: 1px solid rgba(148, 163, 184, 0.25);
            background: rgba(255, 255, 255, 0.72);
            margin-right: 0.5rem;
            padding: 0.65rem 1rem;
        }
        div[data-testid="stTabs"] button[aria-selected="true"] {
            background: linear-gradient(135deg, #1d4ed8, #0ea5e9);
            color: white;
            border-color: transparent;
        }
        .stButton > button {
            border-radius: 999px;
            border: none;
            background: linear-gradient(135deg, #1d4ed8, #0ea5e9);
            color: white;
            font-weight: 600;
            box-shadow: 0 14px 28px rgba(37, 99, 235, 0.2);
        }
        .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
            border-radius: 16px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def get_series_data(terms: int) -> dict[str, object]:
    return fourier_series_demo(terms)


@st.cache_data(show_spinner=False)
def get_transition_data(period: float) -> dict[str, object]:
    return series_to_integral_demo(period)


@st.cache_data(show_spinner=False)
def get_transform_data(signal: str, noise: float, cutoff: float, mode: str) -> dict[str, object]:
    return transform_demo(signal, noise, cutoff, mode)


@st.cache_data(show_spinner=False)
def get_image_data(mode: str, cutoff: int, noise: float) -> dict[str, object]:
    return image_demo(mode, cutoff, noise)


def metric_card(title: str, value: str, note: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def panel_open() -> None:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)


def panel_close() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def decode_data_uri(data_uri: str) -> Image.Image:
    _, encoded = data_uri.split(",", 1)
    payload = base64.b64decode(encoded)
    return Image.open(io.BytesIO(payload))


def line_figure(
    title: str,
    traces: list[dict[str, Any]],
    x_title: str,
    y_title: str,
    height: int = 360,
) -> go.Figure:
    figure = go.Figure()
    for trace in traces:
        figure.add_trace(
            go.Scatter(
                x=trace["x"],
                y=trace["y"],
                mode=trace.get("mode", "lines"),
                name=trace["name"],
                line=dict(color=trace["color"], width=trace.get("width", 3)),
                marker=dict(size=trace.get("marker_size", 8), color=trace.get("color")),
                opacity=trace.get("opacity", 1.0),
            )
        )

    figure.update_layout(
        title=title,
        height=height,
        margin=dict(l=12, r=12, t=42, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.62)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1.0),
        xaxis=dict(title=x_title, gridcolor="rgba(148,163,184,0.22)", zerolinecolor="rgba(148,163,184,0.22)"),
        yaxis=dict(title=y_title, gridcolor="rgba(148,163,184,0.22)", zerolinecolor="rgba(148,163,184,0.22)"),
        font=dict(color="#0f172a"),
    )
    return figure


def bar_figure(title: str, x: list[float], y: list[float], color: str, x_title: str, y_title: str) -> go.Figure:
    figure = go.Figure(
        data=[
            go.Bar(
                x=x,
                y=y,
                marker=dict(color=color, line=dict(color="rgba(255,255,255,0.45)", width=1)),
            )
        ]
    )
    figure.update_layout(
        title=title,
        height=320,
        margin=dict(l=12, r=12, t=42, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.62)",
        xaxis=dict(title=x_title, gridcolor="rgba(148,163,184,0.22)"),
        yaxis=dict(title=y_title, gridcolor="rgba(148,163,184,0.22)"),
        font=dict(color="#0f172a"),
    )
    return figure


def surface_figure(title: str, x: list[int], y: list[int], z: list[list[float]]) -> go.Figure:
    figure = go.Figure(
        data=[
            go.Surface(
                x=x,
                y=y,
                z=z,
                colorscale=[
                    [0.0, "#dbeafe"],
                    [0.2, "#93c5fd"],
                    [0.45, "#38bdf8"],
                    [0.7, "#2563eb"],
                    [1.0, "#0f172a"],
                ],
                showscale=False,
                hovertemplate="x=%{x}<br>y=%{y}<br>强度=%{z:.3f}<extra></extra>",
            )
        ]
    )
    figure.update_layout(
        title=title,
        height=430,
        margin=dict(l=0, r=0, t=42, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            bgcolor="rgba(255,255,255,0.62)",
            xaxis=dict(title="频率 x", gridcolor="rgba(148,163,184,0.18)"),
            yaxis=dict(title="频率 y", gridcolor="rgba(148,163,184,0.18)"),
            zaxis=dict(title="幅值", gridcolor="rgba(148,163,184,0.18)"),
            camera=dict(eye=dict(x=1.45, y=1.45, z=0.9)),
        ),
        font=dict(color="#0f172a"),
    )
    return figure


def stacked_3d_lines_figure(
    title: str,
    traces: list[dict[str, Any]],
    x_title: str,
    y_title: str,
    z_title: str,
    height: int = 430,
) -> go.Figure:
    figure = go.Figure()
    tickvals: list[float] = []
    ticktext: list[str] = []

    for index, trace in enumerate(traces):
        plane = float(trace.get("plane", index))
        if plane not in tickvals:
            tickvals.append(plane)
            ticktext.append(trace["name"])

        x_values = trace["x"]
        z_values = trace["z"]
        figure.add_trace(
            go.Scatter3d(
                x=x_values,
                y=[plane] * len(x_values),
                z=z_values,
                mode=trace.get("mode", "lines"),
                name=trace["name"],
                line=dict(color=trace["color"], width=trace.get("width", 6)),
                marker=dict(size=trace.get("marker_size", 3), color=trace["color"]),
                opacity=trace.get("opacity", 1.0),
            )
        )

    figure.update_layout(
        title=title,
        height=height,
        margin=dict(l=0, r=0, t=42, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1.0),
        scene=dict(
            bgcolor="rgba(255,255,255,0.62)",
            xaxis=dict(title=x_title, gridcolor="rgba(148,163,184,0.18)"),
            yaxis=dict(
                title=y_title,
                gridcolor="rgba(148,163,184,0.18)",
                tickmode="array",
                tickvals=tickvals,
                ticktext=ticktext,
            ),
            zaxis=dict(title=z_title, gridcolor="rgba(148,163,184,0.18)"),
            camera=dict(eye=dict(x=1.4, y=1.35, z=0.95)),
        ),
        font=dict(color="#0f172a"),
    )
    return figure


def ensure_state() -> None:
    defaults: dict[str, Any] = {
        "series_terms": 6,
        "transition_period": 16.0,
        "transform_signal": "sensor",
        "transform_noise": 0.4,
        "transform_cutoff": 1.8,
        "transform_mode": "lowpass",
        "image_mode": "lowpass",
        "image_cutoff": 40,
        "image_noise": 0.16,
        "ai_module": "general",
        "ai_template": "自定义",
        "ai_prompt": "",
        "runtime_api_key": "",
        "runtime_model": "",
        "runtime_endpoint": "",
        "api_test_status": None,
        "quiz_submitted": False,
        "chat_history": [
            {
                "role": "assistant",
                "content": "我是 fourier-lab 的 AI 助教。你可以结合当前实验参数提问，例如“为什么低通滤波后图像会更平滑？”",
            }
        ],
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def current_context() -> dict[str, Any]:
    return {
        "series_terms": st.session_state.series_terms,
        "transition_period": st.session_state.transition_period,
        "transform_signal": st.session_state.transform_signal,
        "transform_noise": round(float(st.session_state.transform_noise), 3),
        "transform_cutoff": round(float(st.session_state.transform_cutoff), 3),
        "transform_mode": st.session_state.transform_mode,
        "image_mode": st.session_state.image_mode,
        "image_cutoff": int(st.session_state.image_cutoff),
        "image_noise": round(float(st.session_state.image_noise), 3),
    }


def runtime_ai_settings() -> dict[str, str | None]:
    api_key = st.session_state.runtime_api_key.strip()
    model = st.session_state.runtime_model.strip()
    endpoint = st.session_state.runtime_endpoint.strip()
    return {
        "api_key": api_key or None,
        "model": model or None,
        "endpoint": endpoint or None,
    }


def render_header() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-badge">fourier-lab</div>
            <h1 class="hero-title">Streamlit 傅里叶实验室</h1>
            <p class="hero-copy">把级数、频谱、滤波、图像降噪和 AI 助教放进同一个可部署的课堂实验界面。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview() -> None:
    series = get_series_data(st.session_state.series_terms)
    transition = get_transition_data(st.session_state.transition_period)
    transform = get_transform_data(
        st.session_state.transform_signal,
        float(st.session_state.transform_noise),
        float(st.session_state.transform_cutoff),
        st.session_state.transform_mode,
    )
    image = get_image_data(
        st.session_state.image_mode,
        int(st.session_state.image_cutoff),
        float(st.session_state.image_noise),
    )

    cols = st.columns(4)
    with cols[0]:
        metric_card("Series", f"{st.session_state.series_terms} 项", f"MSE {series['mse']}")
    with cols[1]:
        metric_card("Integral", f"{transition['spacing']}", "离散频率间隔")
    with cols[2]:
        metric_card("Transform", f"{transform['improvement']} dB", "滤波前后 SNR 提升")
    with cols[3]:
        metric_card("Image", f"{image['retained_ratio']}%", "频域保留比例")


def render_sidebar() -> None:
    st.sidebar.markdown("## fourier-lab")
    st.sidebar.caption("真正面向 Streamlit 部署的版本")
    st.sidebar.markdown("### 运行状态")

    settings = runtime_ai_settings()
    if has_ai_credentials(settings["api_key"]):
        st.sidebar.success("已检测到可用的千问密钥")
    else:
        st.sidebar.warning("尚未检测到千问密钥")

    with st.sidebar.expander("API 配置", expanded=False):
        st.caption("支持直接在页面输入 API Key。当前输入只保存在本次会话，不会写回仓库。")
        st.text_input(
            "DashScope API Key",
            key="runtime_api_key",
            type="password",
            placeholder="sk-...",
            help="留空时会回退到 Streamlit secrets 或本地 .env。",
        )
        st.text_input("模型名称", key="runtime_model", placeholder="留空则使用 qwen-plus")
        st.text_input("接口地址", key="runtime_endpoint", placeholder="留空则使用官方兼容端点")

        if st.button("测试 API 连接", key="test_api_connection_button", use_container_width=True):
            test_settings = runtime_ai_settings()
            with st.spinner("正在测试千问 API 连接..."):
                try:
                    result = test_ai_connection(**test_settings)
                except RuntimeError as exc:
                    st.session_state.api_test_status = {"level": "error", "message": str(exc)}
                except Exception as exc:  # pragma: no cover - UI defensive path
                    st.session_state.api_test_status = {"level": "error", "message": f"出现未预期错误：{exc}"}
                else:
                    st.session_state.api_test_status = {"level": "success", "message": result}

        status = st.session_state.api_test_status
        if status:
            if status["level"] == "success":
                st.success(f"连接测试成功：{status['message']}")
            else:
                st.error(status["message"])

    st.sidebar.markdown("### 部署提示")
    st.sidebar.caption("主入口文件：`streamlit_app.py`")
    st.sidebar.caption("本地也可以运行：`python app.py`")
    st.sidebar.caption("云端可直接在页面输入 Key，也可以在 Streamlit secrets 中配置 `DASHSCOPE_API_KEY`")

    with st.sidebar.expander("当前实验上下文", expanded=False):
        st.code(json.dumps(current_context(), ensure_ascii=False, indent=2), language="json")


def render_series_tab() -> None:
    left, right = st.columns([0.33, 0.67], gap="large")
    with left:
        panel_open()
        st.subheader("傅里叶级数")
        st.slider("谐波项数", 1, 12, key="series_terms")
        data = get_series_data(st.session_state.series_terms)
        st.markdown(f'<div class="caption-line">{data["summary"]}</div>', unsafe_allow_html=True)
        st.divider()
        metric_card("MSE", f"{data['mse']}", "近似误差")
        metric_card("Gibbs", f"{data['gibbs_peak']}", "峰值超调")
        panel_close()
    with right:
        data = get_series_data(st.session_state.series_terms)
        x = np.asarray(data["x"], dtype=float)
        palette = ["#38bdf8", "#0ea5e9", "#2563eb", "#1d4ed8", "#4338ca", "#0f172a"]
        harmonic_traces: list[dict[str, Any]] = []
        for index, (harmonic, amplitude) in enumerate(zip(data["harmonics"], data["amplitudes"])):
            harmonic_traces.append(
                {
                    "name": f"H{harmonic}",
                    "x": data["x"],
                    "z": (amplitude * np.sin(harmonic * x)).tolist(),
                    "plane": harmonic,
                    "color": palette[index % len(palette)],
                    "width": 4,
                }
            )

        st.plotly_chart(
            stacked_3d_lines_figure(
                "3D 方波与级数逼近",
                [
                    {"name": "目标方波", "x": data["x"], "z": data["target"], "plane": 0, "color": "#0f172a", "width": 5},
                    {"name": "级数逼近", "x": data["x"], "z": data["approximation"], "plane": 1, "color": "#2563eb", "width": 6},
                ],
                "t",
                "图层",
                "幅值",
                height=360,
            ),
            use_container_width=True,
        )
        st.caption("这里已经改成三维主图。拖拽图形可以从不同角度观察理想方波和傅里叶逼近之间的差异。")
        st.plotly_chart(
            stacked_3d_lines_figure(
                "3D 谐波瀑布图",
                harmonic_traces,
                "t",
                "谐波序号",
                "分量幅值",
                height=420,
            ),
            use_container_width=True,
        )


def render_transition_tab() -> None:
    left, right = st.columns([0.33, 0.67], gap="large")
    with left:
        panel_open()
        st.subheader("级数到积分")
        st.slider("周期 T", 6.0, 28.0, key="transition_period")
        data = get_transition_data(float(st.session_state.transition_period))
        st.markdown(f'<div class="caption-line">{data["summary"]}</div>', unsafe_allow_html=True)
        st.divider()
        metric_card("ω₀", f"{data['spacing']}", "基本频率间隔")
        metric_card("Sample", f"{data['sample_count']}", "离散频率点数量")
        panel_close()
    with right:
        data = get_transition_data(float(st.session_state.transition_period))
        st.plotly_chart(
            line_figure(
                "周期延拓后的时域波形",
                [{"name": "周期信号", "x": data["time_x"], "y": data["time_y"], "color": "#2563eb"}],
                "t",
                "幅值",
            ),
            use_container_width=True,
        )
        st.plotly_chart(
            line_figure(
                "离散谱线向连续包络过渡",
                [
                    {"name": "连续包络", "x": data["omega"], "y": data["envelope"], "color": "#0ea5e9", "width": 3},
                    {
                        "name": "离散谱线",
                        "x": data["sampled_omega"],
                        "y": data["sampled_amplitude"],
                        "color": "#1d4ed8",
                        "mode": "markers",
                        "marker_size": 9,
                        "width": 0,
                    },
                ],
                "ω",
                "归一化幅值",
            ),
            use_container_width=True,
        )


def render_transform_tab() -> None:
    left, right = st.columns([0.36, 0.64], gap="large")
    with left:
        panel_open()
        st.subheader("傅里叶变换")
        st.selectbox(
            "信号类型",
            options=["sensor", "pulse", "chirp"],
            format_func=lambda value: {"sensor": "传感器叠加波", "pulse": "高斯脉冲", "chirp": "啁啾信号"}[value],
            key="transform_signal",
        )
        st.slider("噪声强度", 0.0, 1.2, key="transform_noise")
        st.slider("截止频率", 0.2, 5.5, key="transform_cutoff")
        st.selectbox(
            "滤波方式",
            options=["lowpass", "highpass", "bandpass"],
            format_func=lambda value: {"lowpass": "低通", "highpass": "高通", "bandpass": "带通"}[value],
            key="transform_mode",
        )
        data = get_transform_data(
            st.session_state.transform_signal,
            float(st.session_state.transform_noise),
            float(st.session_state.transform_cutoff),
            st.session_state.transform_mode,
        )
        st.markdown(f'<div class="caption-line">{data["summary"]}</div>', unsafe_allow_html=True)
        st.divider()
        metric_card("SNR Before", f"{data['snr_before']} dB", "加噪后的信噪比")
        metric_card("SNR After", f"{data['snr_after']} dB", "滤波后的信噪比")
        metric_card("Improvement", f"{data['improvement']} dB", "恢复效果")
        panel_close()
    with right:
        data = get_transform_data(
            st.session_state.transform_signal,
            float(st.session_state.transform_noise),
            float(st.session_state.transform_cutoff),
            st.session_state.transform_mode,
        )
        mask_scale = max(data["spectrum"]) * 0.35 if data["spectrum"] else 0.0
        st.plotly_chart(
            stacked_3d_lines_figure(
                "3D 时域信号",
                [
                    {"name": "原始信号", "x": data["time_x"], "z": data["clean"], "plane": 0, "color": "#0f172a", "width": 5},
                    {"name": "带噪信号", "x": data["time_x"], "z": data["noisy"], "plane": 1, "color": "#38bdf8", "width": 4, "opacity": 0.86},
                    {"name": "滤波结果", "x": data["time_x"], "z": data["filtered"], "plane": 2, "color": "#1d4ed8", "width": 6},
                ],
                "t",
                "信号层",
                "幅值",
                height=340,
            ),
            use_container_width=True,
        )
        st.caption("时域主图已经切成三维叠层，拖拽后可以更直观看出原始、带噪和滤波结果之间的差别。")
        st.plotly_chart(
            stacked_3d_lines_figure(
                "3D 频域幅值",
                [
                    {"name": "原始频谱", "x": data["freq_x"], "z": data["spectrum"], "plane": 0, "color": "#0ea5e9", "width": 4},
                    {"name": "滤波后频谱", "x": data["freq_x"], "z": data["filtered_spectrum"], "plane": 1, "color": "#1d4ed8", "width": 5},
                    {"name": "滤波窗口", "x": data["freq_x"], "z": [value * mask_scale for value in data["mask"]], "plane": 2, "color": "#94a3b8", "width": 3},
                ],
                "f",
                "频谱层",
                "|F(f)|",
                height=340,
            ),
            use_container_width=True,
        )


def render_image_tab() -> None:
    left, right = st.columns([0.34, 0.66], gap="large")
    with left:
        panel_open()
        st.subheader("图像频域实验")
        st.selectbox(
            "滤波方式",
            options=["lowpass", "highpass"],
            format_func=lambda value: {"lowpass": "低通降噪", "highpass": "高通边缘"}[value],
            key="image_mode",
        )
        st.slider("截止半径", 6, 96, key="image_cutoff")
        st.slider("噪声强度", 0.0, 0.32, key="image_noise")
        data = get_image_data(
            st.session_state.image_mode,
            int(st.session_state.image_cutoff),
            float(st.session_state.image_noise),
        )
        st.markdown(f'<div class="caption-line">{data["summary"]}</div>', unsafe_allow_html=True)
        st.divider()
        metric_card("Retained", f"{data['retained_ratio']}%", "保留的频域比例")
        metric_card("MSE Before", f"{data['mse_before']}", "加噪后误差")
        metric_card("MSE After", f"{data['mse_after']}", "滤波后误差")
        metric_card("3D Peak", f"{data['surface_peak']}", "三维频谱峰值")
        panel_close()
    with right:
        data = get_image_data(
            st.session_state.image_mode,
            int(st.session_state.image_cutoff),
            float(st.session_state.image_noise),
        )
        top = st.columns(2, gap="medium")
        bottom = st.columns(2, gap="medium")
        top[0].image(decode_data_uri(data["clean"]), caption="原始图像", use_container_width=True)
        top[1].image(decode_data_uri(data["noisy"]), caption="加噪图像", use_container_width=True)
        bottom[0].image(decode_data_uri(data["spectrum"]), caption="频谱视图", use_container_width=True)
        bottom[1].image(decode_data_uri(data["filtered"]), caption="滤波结果", use_container_width=True)
        st.caption("三维频谱图可以拖拽旋转，用来观察中心低频峰和外围高频分布。")
        st.plotly_chart(
            surface_figure(
                "三维傅里叶频谱曲面",
                data["surface_x"],
                data["surface_y"],
                data["spectrum_surface"],
            ),
            use_container_width=True,
        )


def render_quiz_tab() -> None:
    panel_open()
    st.subheader("课堂小测")
    questions = quiz_questions()
    for index, question in enumerate(questions):
        st.markdown(f"**{index + 1}. {question['prompt']}**")
        st.radio(
            "请选择答案",
            question["options"],
            key=f"quiz_{index}",
            index=None,
            label_visibility="collapsed",
        )
        st.write("")

    if st.button("检查答案", key="check_quiz", use_container_width=True):
        st.session_state.quiz_submitted = True

    if st.session_state.quiz_submitted:
        score = 0
        for index, question in enumerate(questions):
            chosen = st.session_state.get(f"quiz_{index}")
            correct = question["options"][question["answer"]]
            if chosen == correct:
                score += 1
                st.success(f"第 {index + 1} 题正确：{question['explanation']}")
            else:
                st.error(f"第 {index + 1} 题正确答案是“{correct}”：{question['explanation']}")
        st.info(f"当前得分：{score} / {len(questions)}")
    panel_close()


def render_ai_tab() -> None:
    left, right = st.columns([0.34, 0.66], gap="large")
    with left:
        panel_open()
        st.subheader("AI 助教")
        st.caption("如果没有配置 `.env`，可以直接在左侧边栏的“API 配置”里输入千问 API Key。")
        st.selectbox(
            "提问模块",
            options=["general", "series", "transition", "transform", "image"],
            format_func=lambda value: {
                "general": "综合",
                "series": "傅里叶级数",
                "transition": "级数到积分",
                "transform": "傅里叶变换",
                "image": "图像频域实验",
            }[value],
            key="ai_module",
        )
        prompt_templates = {
            "系列逼近为什么会有振铃？": "系列逼近为什么会在方波边缘出现振铃？",
            "周期变大后发生什么？": "当周期 T 继续变大时，离散谱线为什么会越来越像连续频谱？",
            "怎样解释滤波结果？": "请结合我当前的滤波参数，解释为什么信号恢复成现在这样。",
            "图像为什么更模糊？": "为什么我当前的图像滤波结果会更平滑或更模糊？",
        }
        quick_prompt = st.selectbox(
            "快捷问题",
            options=["自定义"] + list(prompt_templates.keys()),
            key="ai_template",
        )
        if quick_prompt != "自定义" and st.button("填入当前问题模板", use_container_width=True):
            st.session_state.ai_prompt = prompt_templates[quick_prompt]

        st.text_area("问题", key="ai_prompt", height=140, placeholder="例如：请解释当前图像实验中低通滤波的作用。")
        settings = runtime_ai_settings()
        disabled = not has_ai_credentials(settings["api_key"])
        if st.button("发送给 AI 助教", use_container_width=True, disabled=disabled):
            question = st.session_state.ai_prompt.strip()
            if not question:
                st.warning("请先输入问题。")
            else:
                st.session_state.chat_history.append({"role": "user", "content": question})
                with st.spinner("AI 助教正在分析当前实验参数..."):
                    try:
                        answer = ask_ai_tutor(
                            question=question,
                            module=st.session_state.ai_module,
                            context=current_context(),
                            api_key=settings["api_key"],
                            model=settings["model"],
                            endpoint=settings["endpoint"],
                        )
                    except RuntimeError as exc:
                        answer = f"调用失败：{exc}"
                    except Exception as exc:  # pragma: no cover - UI defensive path
                        answer = f"出现未预期错误：{exc}"
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                st.session_state.ai_prompt = ""

        if disabled:
            st.warning("还没有可用的 DASHSCOPE_API_KEY。请在侧边栏输入 Key，或在 Streamlit secrets/.env 中配置。")
        with st.expander("发送给 AI 的实验上下文", expanded=False):
            st.code(json.dumps(current_context(), ensure_ascii=False, indent=2), language="json")
            st.code(json.dumps(runtime_ai_settings(), ensure_ascii=False, indent=2), language="json")
        panel_close()
    with right:
        panel_open()
        st.subheader("对话窗口")
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        panel_close()


def main() -> None:
    st.set_page_config(
        page_title="fourier-lab",
        page_icon="f",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_styles()
    ensure_state()
    render_sidebar()
    render_header()
    render_overview()

    tabs = st.tabs(
        [
            "傅里叶级数",
            "级数到积分",
            "傅里叶变换",
            "图像频域实验",
            "课堂小测",
            "AI 助教",
        ]
    )

    with tabs[0]:
        render_series_tab()
    with tabs[1]:
        render_transition_tab()
    with tabs[2]:
        render_transform_tab()
    with tabs[3]:
        render_image_tab()
    with tabs[4]:
        render_quiz_tab()
    with tabs[5]:
        render_ai_tab()


if __name__ == "__main__":
    main()
