from fourier_lab.analysis import (
    fourier_series_demo,
    image_demo,
    quiz_questions,
    series_to_integral_demo,
    transform_demo,
)


def test_series_demo_shapes() -> None:
    data = fourier_series_demo(4)
    assert len(data["x"]) == len(data["target"]) == len(data["approximation"])
    assert data["harmonics"] == [1, 3, 5, 7]
    assert len(data["amplitudes"]) == 4


def test_transition_demo_returns_dense_spectrum() -> None:
    data = series_to_integral_demo(18.0)
    assert data["sample_count"] > 0
    assert len(data["omega"]) == len(data["envelope"])
    assert len(data["sampled_omega"]) == len(data["sampled_amplitude"])


def test_transform_demo_returns_time_and_frequency_outputs() -> None:
    data = transform_demo("sensor", 0.3, 2.0, "lowpass")
    assert len(data["time_x"]) == len(data["clean"]) == len(data["filtered"])
    assert len(data["freq_x"]) == len(data["spectrum"]) == len(data["filtered_spectrum"])
    assert isinstance(data["improvement"], float)


def test_image_demo_outputs_data_uris() -> None:
    data = image_demo("lowpass", 40, 0.16)
    assert data["clean"].startswith("data:image/png;base64,")
    assert data["filtered"].startswith("data:image/png;base64,")
    assert data["retained_ratio"] > 0
    assert len(data["surface_x"]) == len(data["spectrum_surface"][0])
    assert len(data["surface_y"]) == len(data["spectrum_surface"])
    assert data["surface_peak"] >= 0


def test_quiz_questions_have_expected_shape() -> None:
    questions = quiz_questions()
    assert len(questions) == 3
    assert all("prompt" in question and "options" in question for question in questions)
