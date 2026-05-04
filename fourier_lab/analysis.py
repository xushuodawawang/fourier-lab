from __future__ import annotations

import base64
import io
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image, ImageOps


TAU = 2.0 * np.pi
ROOT_DIR = Path(__file__).resolve().parent.parent
DEMO_IMAGE_PATH = ROOT_DIR / "image.png"
IMAGE_SIZE = 256
SURFACE_SAMPLE_SIZE = 72
RESAMPLE = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS


def _pack(values: Iterable[float], digits: int = 6) -> list[float]:
    array = np.asarray(values, dtype=float)
    return [round(float(item), digits) for item in array.tolist()]


def _normalize(values: np.ndarray) -> np.ndarray:
    minimum = float(np.min(values))
    maximum = float(np.max(values))
    if maximum - minimum < 1e-12:
        return np.zeros_like(values, dtype=float)
    return (values - minimum) / (maximum - minimum)


def _pack_matrix(values: np.ndarray, digits: int = 6) -> list[list[float]]:
    array = np.asarray(values, dtype=float)
    rounded = np.round(array, digits)
    return [[float(item) for item in row] for row in rounded.tolist()]


def _downsample_grid(values: np.ndarray, sample_size: int = SURFACE_SAMPLE_SIZE) -> np.ndarray:
    height, width = values.shape
    y_index = np.linspace(0, height - 1, min(sample_size, height), dtype=int)
    x_index = np.linspace(0, width - 1, min(sample_size, width), dtype=int)
    return values[np.ix_(y_index, x_index)]


def _image_data_uri(values: np.ndarray) -> str:
    clipped = np.clip(values, 0.0, 1.0)
    if clipped.ndim == 2:
        image = Image.fromarray(np.uint8(clipped * 255.0), mode="L").convert("RGB")
    else:
        image = Image.fromarray(np.uint8(clipped * 255.0), mode="RGB")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    payload = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{payload}"


def _fallback_demo_image(size: int) -> np.ndarray:
    y, x = np.mgrid[-1.0:1.0:complex(0, size), -1.0:1.0:complex(0, size)]
    crest = np.exp(-4.5 * (x**2 + y**2))
    ridges = 0.25 * np.sin(12.0 * x) + 0.18 * np.cos(15.0 * y)
    halo = 0.15 * np.exp(-70.0 * (np.sqrt(x**2 + y**2) - 0.58) ** 2)
    base = _normalize(0.6 * crest + ridges + halo)
    rgb = np.stack(
        (
            0.85 * base + 0.15,
            0.92 * base + 0.08,
            np.ones_like(base),
        ),
        axis=-1,
    )
    return np.clip(rgb, 0.0, 1.0)


def _prepare_image(image: Image.Image, size: int = IMAGE_SIZE) -> np.ndarray:
    image = image.convert("RGB")
    canvas = Image.new("RGB", (size, size), color=(255, 255, 255))
    contained = ImageOps.contain(image, (size - 20, size - 20), method=RESAMPLE)
    offset = ((size - contained.width) // 2, (size - contained.height) // 2)
    canvas.paste(contained, offset)
    return np.asarray(canvas, dtype=float) / 255.0


def _load_demo_image(size: int = IMAGE_SIZE, image_bytes: bytes | None = None) -> np.ndarray:
    if image_bytes:
        with Image.open(io.BytesIO(image_bytes)) as source:
            return _prepare_image(source, size)

    if not DEMO_IMAGE_PATH.exists():
        return _fallback_demo_image(size)

    with Image.open(DEMO_IMAGE_PATH) as source:
        return _prepare_image(source, size)


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
        "summary": f"使用 {terms} 项奇次谐波逼近方波，边缘附近仍能看到典型的 Gibbs 现象。",
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
        "summary": "周期 T 增大时，离散频率点会变得更密，逐渐贴近连续频谱包络。",
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
        "summary": "先在频域定位噪声，再进行滤波，最后逆变换回到时域。",
    }


def image_demo(
    filter_mode: str = "lowpass",
    cutoff: int = 40,
    noise_level: float = 0.16,
    image_bytes: bytes | None = None,
) -> dict[str, object]:
    clean = _load_demo_image(image_bytes=image_bytes)
    size = clean.shape[0]
    rng = np.random.default_rng(11)

    gaussian_noise = rng.normal(loc=0.0, scale=noise_level, size=clean.shape)
    noisy = np.clip(clean + gaussian_noise, 0.0, 1.0)

    impulse_ratio = min(0.04, noise_level * 0.1)
    impulse_map = rng.random((size, size))
    salt_mask = impulse_map < impulse_ratio
    pepper_mask = (impulse_map >= impulse_ratio) & (impulse_map < impulse_ratio * 1.8)
    noisy[salt_mask] = 1.0
    noisy[pepper_mask] = 0.0

    shifted = np.fft.fftshift(np.fft.fft2(noisy, axes=(0, 1)), axes=(0, 1))
    yy, xx = np.indices((size, size))
    spectral_radius = np.sqrt((xx - size / 2.0) ** 2 + (yy - size / 2.0) ** 2)

    if filter_mode == "highpass":
        mask = spectral_radius >= cutoff
        summary = f"高通模式，噪声强度 {noise_level:.2f}，更适合观察边缘和高频细节。"
    else:
        mask = spectral_radius <= cutoff
        summary = f"低通模式，噪声强度 {noise_level:.2f}，更适合演示降噪与轮廓保留。"

    filtered_shifted = shifted * mask[..., None]
    filtered = np.fft.ifft2(np.fft.ifftshift(filtered_shifted, axes=(0, 1)), axes=(0, 1)).real
    filtered = np.clip(filtered, 0.0, 1.0)

    spectrum_log = np.log1p(np.mean(np.abs(shifted), axis=2))
    spectrum_view = _normalize(spectrum_log)
    spectrum_surface = _downsample_grid(spectrum_view)
    mse_before = float(np.mean((noisy - clean) ** 2))
    mse_after = float(np.mean((filtered - clean) ** 2))

    return {
        "clean": _image_data_uri(clean),
        "noisy": _image_data_uri(noisy),
        "spectrum": _image_data_uri(spectrum_view),
        "filtered": _image_data_uri(filtered),
        "source_label": "上传图像" if image_bytes else "默认示例",
        "spectrum_surface": _pack_matrix(spectrum_surface),
        "surface_x": list(range(int(spectrum_surface.shape[1]))),
        "surface_y": list(range(int(spectrum_surface.shape[0]))),
        "surface_peak": round(float(np.max(spectrum_surface)), 5),
        "retained_ratio": round(float(np.mean(mask) * 100.0), 2),
        "mse_before": round(mse_before, 5),
        "mse_after": round(mse_after, 5),
        "summary": summary,
    }


def quiz_questions() -> list[dict[str, object]]:
    return [
        {
            "prompt": "傅里叶级数最直接适用于哪类信号？",
            "options": ["周期信号", "随机噪声", "任意图像", "非周期脉冲"],
            "answer": 0,
            "explanation": "傅里叶级数用于周期展开，频域上表现为离散谱线。",
        },
        {
            "prompt": "当 T 变大时，ω₀ 会怎样？",
            "options": ["不变", "变大", "趋近 0", "先小后大"],
            "answer": 2,
            "explanation": "ω₀ = 2π/T，周期越大，频率间隔越小。",
        },
        {
            "prompt": "图像降噪通常更接近哪种处理？",
            "options": ["全部增强高频", "保低频抑高频", "删除全部低频", "只保留单频点"],
            "answer": 1,
            "explanation": "低频负责整体结构，高频更容易包含细节和噪声。",
        },
    ]
