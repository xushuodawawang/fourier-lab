from __future__ import annotations

import base64
import io
from typing import Iterable

import numpy as np
from PIL import Image


TAU = 2.0 * np.pi


def _pack(values: Iterable[float], digits: int = 6) -> list[float]:
    array = np.asarray(values, dtype=float)
    return [round(float(item), digits) for item in array.tolist()]


def _normalize(values: np.ndarray) -> np.ndarray:
    minimum = float(np.min(values))
    maximum = float(np.max(values))
    if maximum - minimum < 1e-12:
        return np.zeros_like(values, dtype=float)
    return (values - minimum) / (maximum - minimum)


def _image_data_uri(values: np.ndarray) -> str:
    clipped = np.clip(values, 0.0, 1.0)
    image = Image.fromarray(np.uint8(clipped * 255.0), mode="L").convert("RGB")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    payload = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{payload}"


def fourier_series_demo(terms: int = 6) -> dict[str, object]:
    odd_harmonics = 2 * np.arange(terms) + 1
    x = np.linspace(-2.0 * np.pi, 2.0 * np.pi, 960)
    target = np.where(np.sin(x) >= 0.0, 1.0, -1.0)
    approximation = np.zeros_like(x)
    amplitudes = 4.0 / (np.pi * odd_harmonics)

    for harmonic, amplitude in zip(odd_harmonics, amplitudes):
        approximation += amplitude * np.sin(harmonic * x)

    mse = float(np.mean((approximation - target) ** 2))
    gibbs = float(np.max(approximation) - 1.0)

    return {
        "x": _pack(x),
        "target": _pack(target),
        "approximation": _pack(approximation),
        "harmonics": odd_harmonics.tolist(),
        "amplitudes": _pack(amplitudes),
        "mse": round(mse, 5),
        "gibbs_peak": round(gibbs, 5),
        "summary": f"当前使用 {terms} 个奇次谐波，离散频谱只出现在 n=1,3,5... 这些谱线上。",
    }


def series_to_integral_demo(period: float = 16.0) -> dict[str, object]:
    a = 0.34
    omega_span = 11.0
    omega_0 = TAU / period

    def envelope(omega: np.ndarray) -> np.ndarray:
        return np.sqrt(np.pi / a) * np.exp(-(omega**2) / (4.0 * a))

    omega = np.linspace(-omega_span, omega_span, 840)
    envelope_values = envelope(omega)
    envelope_values /= np.max(envelope_values)

    n_max = max(4, int(omega_span / omega_0))
    n = np.arange(-n_max, n_max + 1)
    sampled_omega = n * omega_0
    sampled_amplitude = envelope(sampled_omega)
    sampled_amplitude /= np.max(sampled_amplitude)

    t = np.linspace(-2.1 * period, 2.1 * period, 920)
    wrapped_t = ((t + period / 2.0) % period) - period / 2.0
    periodic_signal = np.exp(-a * wrapped_t**2)

    return {
        "time_x": _pack(t),
        "time_y": _pack(periodic_signal),
        "omega": _pack(omega),
        "envelope": _pack(envelope_values),
        "sampled_omega": _pack(sampled_omega),
        "sampled_amplitude": _pack(sampled_amplitude),
        "spacing": round(float(omega_0), 4),
        "sample_count": int(sampled_omega.size),
        "summary": "周期越大，基波间隔越小，离散谱线就越密，最终逼近连续频谱包络。",
    }


def transform_demo(
    signal_kind: str = "sensor",
    noise_level: float = 0.4,
    cutoff: float = 1.8,
    filter_mode: str = "lowpass",
) -> dict[str, object]:
    t = np.linspace(-6.0, 6.0, 1024, endpoint=False)
    dt = float(t[1] - t[0])
    rng = np.random.default_rng(7)

    if signal_kind == "pulse":
        clean = np.exp(-0.55 * t**2) * np.cos(2.0 * np.pi * 1.1 * t)
    elif signal_kind == "chirp":
        clean = np.cos(2.0 * np.pi * (0.28 * t**2 + 0.7 * t)) * np.exp(-0.035 * t**2)
    else:
        clean = (
            0.92 * np.sin(2.0 * np.pi * 0.62 * t)
            + 0.38 * np.sin(2.0 * np.pi * 1.48 * t + 0.45)
            + 0.22 * np.cos(2.0 * np.pi * 0.18 * t)
        )

    structured_noise = 0.62 * np.sin(2.0 * np.pi * 4.9 * t)
    random_noise = 0.35 * rng.normal(size=t.size)
    noisy = clean + noise_level * (structured_noise + random_noise)

    freqs = np.fft.fftshift(np.fft.fftfreq(t.size, d=dt))
    spectrum = np.fft.fftshift(np.fft.fft(noisy))

    abs_freqs = np.abs(freqs)
    if filter_mode == "highpass":
        mask = abs_freqs >= cutoff
    elif filter_mode == "bandpass":
        bandwidth = 0.55
        mask = (abs_freqs >= max(cutoff - bandwidth, 0.0)) & (abs_freqs <= cutoff + bandwidth)
    else:
        mask = abs_freqs <= cutoff

    filtered_spectrum = spectrum * mask
    filtered = np.fft.ifft(np.fft.ifftshift(filtered_spectrum)).real

    spectrum_mag = np.abs(spectrum)
    filtered_mag = np.abs(filtered_spectrum)

    noise_power_before = float(np.mean((noisy - clean) ** 2))
    noise_power_after = float(np.mean((filtered - clean) ** 2))
    signal_power = float(np.mean(clean**2))
    snr_before = 10.0 * np.log10(signal_power / max(noise_power_before, 1e-9))
    snr_after = 10.0 * np.log10(signal_power / max(noise_power_after, 1e-9))

    return {
        "time_x": _pack(t),
        "clean": _pack(clean),
        "noisy": _pack(noisy),
        "filtered": _pack(filtered),
        "freq_x": _pack(freqs),
        "spectrum": _pack(spectrum_mag),
        "filtered_spectrum": _pack(filtered_mag),
        "mask": _pack(mask.astype(float)),
        "snr_before": round(float(snr_before), 3),
        "snr_after": round(float(snr_after), 3),
        "improvement": round(float(snr_after - snr_before), 3),
        "summary": "先做傅里叶变换找到噪声主要聚集的频带，再用滤波器处理，最后逆变换回时域。",
    }


def image_demo(filter_mode: str = "lowpass", cutoff: int = 26) -> dict[str, object]:
    size = 256
    rng = np.random.default_rng(11)

    y, x = np.mgrid[-1.0:1.0:complex(0, size), -1.0:1.0:complex(0, size)]
    radius = np.sqrt((x + 0.16) ** 2 + (y - 0.08) ** 2)
    gradient = 0.16 * (x + y + 2.0)
    center_blob = 0.58 * np.exp(-4.1 * (x**2 + y**2))
    ring = 0.35 * np.exp(-95.0 * (radius - 0.42) ** 2)
    ridges = 0.14 * np.sin(17.0 * x) + 0.12 * np.cos(19.0 * y)
    checker = 0.1 * (np.sign(np.sin(11.0 * x) * np.cos(11.0 * y)) + 1.0)

    clean = _normalize(gradient + center_blob + ring + ridges + checker)
    noisy = np.clip(clean + 0.18 * rng.normal(size=(size, size)), 0.0, 1.0)

    shifted = np.fft.fftshift(np.fft.fft2(noisy))
    yy, xx = np.indices((size, size))
    spectral_radius = np.sqrt((xx - size / 2.0) ** 2 + (yy - size / 2.0) ** 2)

    if filter_mode == "highpass":
        mask = spectral_radius >= cutoff
    else:
        mask = spectral_radius <= cutoff

    filtered = np.fft.ifft2(np.fft.ifftshift(shifted * mask)).real
    filtered = _normalize(filtered)
    spectrum_view = _normalize(np.log1p(np.abs(shifted)))

    return {
        "clean": _image_data_uri(clean),
        "noisy": _image_data_uri(noisy),
        "spectrum": _image_data_uri(spectrum_view),
        "filtered": _image_data_uri(filtered),
        "retained_ratio": round(float(np.mean(mask) * 100.0), 2),
        "summary": "低频保留轮廓与大结构，高频更偏向边缘、纹理和噪声，因此频域操作很适合做图像增强与降噪。",
    }


def quiz_questions() -> list[dict[str, object]]:
    return [
        {
            "prompt": "傅里叶级数最直接适用于哪一类信号？",
            "options": ["周期信号", "任意有限长信号", "所有随机噪声信号", "仅图像信号"],
            "answer": 0,
            "explanation": "傅里叶级数强调周期展开，频域对应离散谱线。",
        },
        {
            "prompt": "当周期 T 趋向无穷大时，基波间隔 ω₀ 会怎样变化？",
            "options": ["保持不变", "逐渐增大", "逐渐趋近于 0", "先减小后增大"],
            "answer": 2,
            "explanation": "ω₀ = 2π/T，周期越大，频率采样间隔越小。",
        },
        {
            "prompt": "在图像降噪场景中，常见操作更接近哪一种频域处理？",
            "options": ["增强全部高频", "保留主要低频并抑制部分高频", "删除全部低频", "只保留单个频率点"],
            "answer": 1,
            "explanation": "低频更多承载整体轮廓，高频常包含细节与噪声，所以降噪常通过低通或带通实现。",
        },
    ]
