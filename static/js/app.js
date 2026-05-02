const state = {
    series: null,
    transition: null,
    transform: null,
};

function setupCanvas(canvas) {
    const ratio = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = Math.round(rect.width * ratio);
    canvas.height = Math.round(rect.height * ratio);
    const ctx = canvas.getContext("2d");
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    return { ctx, width: rect.width, height: rect.height };
}

function drawGrid(ctx, width, height, padding) {
    ctx.save();
    ctx.strokeStyle = "rgba(166, 210, 255, 0.08)";
    ctx.lineWidth = 1;
    const innerWidth = width - padding.left - padding.right;
    const innerHeight = height - padding.top - padding.bottom;

    for (let i = 0; i <= 4; i += 1) {
        const y = padding.top + (innerHeight * i) / 4;
        ctx.beginPath();
        ctx.moveTo(padding.left, y);
        ctx.lineTo(width - padding.right, y);
        ctx.stroke();
    }

    for (let i = 0; i <= 6; i += 1) {
        const x = padding.left + (innerWidth * i) / 6;
        ctx.beginPath();
        ctx.moveTo(x, padding.top);
        ctx.lineTo(x, height - padding.bottom);
        ctx.stroke();
    }
    ctx.restore();
}

function drawLineChart(canvas, config) {
    const { ctx, width, height } = setupCanvas(canvas);
    const padding = { left: 48, right: 18, top: 18, bottom: 32 };
    const allX = config.series.flatMap((item) => item.x);
    const allY = config.series.flatMap((item) => item.y);
    const minX = config.minX ?? Math.min(...allX);
    const maxX = config.maxX ?? Math.max(...allX);
    const minY = config.minY ?? Math.min(...allY);
    const maxY = config.maxY ?? Math.max(...allY);

    ctx.clearRect(0, 0, width, height);
    drawGrid(ctx, width, height, padding);

    const mapX = (value) => padding.left + ((value - minX) / (maxX - minX || 1)) * (width - padding.left - padding.right);
    const mapY = (value) => height - padding.bottom - ((value - minY) / (maxY - minY || 1)) * (height - padding.top - padding.bottom);

    ctx.save();
    ctx.strokeStyle = "rgba(234, 246, 255, 0.28)";
    ctx.lineWidth = 1;
    const zeroY = mapY(0);
    ctx.beginPath();
    ctx.moveTo(padding.left, zeroY);
    ctx.lineTo(width - padding.right, zeroY);
    ctx.stroke();
    ctx.restore();

    for (const line of config.series) {
        ctx.save();
        ctx.strokeStyle = line.color;
        ctx.lineWidth = line.width || 2.4;
        ctx.beginPath();
        line.x.forEach((value, index) => {
            const x = mapX(value);
            const y = mapY(line.y[index]);
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        ctx.stroke();
        ctx.restore();
    }

    drawLabels(ctx, width, height, padding, config.xLabel, config.yLabel);
}

function drawSpectrumChart(canvas, config) {
    const { ctx, width, height } = setupCanvas(canvas);
    const padding = { left: 48, right: 18, top: 18, bottom: 32 };
    const minX = config.minX ?? Math.min(...config.bars.x, ...(config.line ? config.line.x : []));
    const maxX = config.maxX ?? Math.max(...config.bars.x, ...(config.line ? config.line.x : []));
    const minY = 0;
    const maxY = config.maxY ?? Math.max(...config.bars.y, ...(config.line ? config.line.y : [0]));
    ctx.clearRect(0, 0, width, height);
    drawGrid(ctx, width, height, padding);

    const mapX = (value) => padding.left + ((value - minX) / (maxX - minX || 1)) * (width - padding.left - padding.right);
    const mapY = (value) => height - padding.bottom - ((value - minY) / (maxY - minY || 1)) * (height - padding.top - padding.bottom);

    if (config.line) {
        ctx.save();
        ctx.strokeStyle = config.line.color;
        ctx.lineWidth = 2;
        ctx.beginPath();
        config.line.x.forEach((value, index) => {
            const x = mapX(value);
            const y = mapY(config.line.y[index]);
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        ctx.stroke();
        ctx.restore();
    }

    ctx.save();
    ctx.strokeStyle = config.bars.color;
    ctx.lineWidth = 2;
    config.bars.x.forEach((value, index) => {
        ctx.beginPath();
        ctx.moveTo(mapX(value), mapY(0));
        ctx.lineTo(mapX(value), mapY(config.bars.y[index]));
        ctx.stroke();
    });
    ctx.restore();

    drawLabels(ctx, width, height, padding, config.xLabel, config.yLabel);
}

function drawLabels(ctx, width, height, padding, xLabel, yLabel) {
    ctx.save();
    ctx.fillStyle = "rgba(188, 218, 245, 0.8)";
    ctx.font = '12px "Aptos", "Microsoft YaHei UI", sans-serif';
    if (xLabel) {
        ctx.fillText(xLabel, width - padding.right - 48, height - 10);
    }
    if (yLabel) {
        ctx.save();
        ctx.translate(16, padding.top + 10);
        ctx.rotate(-Math.PI / 2);
        ctx.fillText(yLabel, 0, 0);
        ctx.restore();
    }
    ctx.restore();
}

async function fetchJSON(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }
    return response.json();
}

function bindRangeDisplay(input, target, formatter) {
    const update = () => {
        target.textContent = formatter(input.value);
    };
    input.addEventListener("input", update);
    update();
}

function updateSeriesMetrics(data) {
    document.getElementById("series-mse").textContent = data.mse.toFixed(5);
    document.getElementById("series-gibbs").textContent = data.gibbs_peak.toFixed(5);
    document.getElementById("series-summary").textContent = data.summary;
}

async function loadSeries() {
    const terms = document.getElementById("series-terms").value;
    const data = await fetchJSON(`/api/series?terms=${terms}`);
    state.series = data;
    updateSeriesMetrics(data);
    drawLineChart(document.getElementById("series-wave-chart"), {
        series: [
            { x: data.x, y: data.target, color: "rgba(121, 200, 255, 0.72)", width: 1.8 },
            { x: data.x, y: data.approximation, color: "#30d7ff", width: 2.8 },
        ],
        xLabel: "t",
        yLabel: "f(t)",
    });
    drawSpectrumChart(document.getElementById("series-spectrum-chart"), {
        bars: {
            x: data.harmonics,
            y: data.amplitudes,
            color: "#6fb5ff",
        },
        xLabel: "谐波序号",
        yLabel: "幅值",
    });
}

function updateTransitionMetrics(data) {
    document.getElementById("transition-spacing").textContent = data.spacing.toFixed(4);
    document.getElementById("transition-count").textContent = `${data.sample_count} 条`;
    document.getElementById("transition-summary").textContent = data.summary;
}

async function loadTransition() {
    const period = document.getElementById("transition-period").value;
    const data = await fetchJSON(`/api/transition?period=${period}`);
    state.transition = data;
    updateTransitionMetrics(data);
    drawLineChart(document.getElementById("transition-time-chart"), {
        series: [{ x: data.time_x, y: data.time_y, color: "#74c8ff", width: 2.5 }],
        xLabel: "t",
        yLabel: "fT(t)",
    });
    drawSpectrumChart(document.getElementById("transition-spectrum-chart"), {
        line: {
            x: data.omega,
            y: data.envelope,
            color: "rgba(49, 218, 255, 0.9)",
        },
        bars: {
            x: data.sampled_omega,
            y: data.sampled_amplitude,
            color: "rgba(111, 181, 255, 0.95)",
        },
        xLabel: "ω",
        yLabel: "谱强度",
    });
}

function updateTransformMetrics(data) {
    document.getElementById("transform-snr-before").textContent = `${data.snr_before.toFixed(2)} dB`;
    document.getElementById("transform-snr-after").textContent = `${data.snr_after.toFixed(2)} dB`;
    document.getElementById("transform-improvement").textContent = `${data.improvement.toFixed(2)} dB`;
    document.getElementById("transform-summary").textContent = data.summary;
}

async function loadTransform() {
    const signal = document.getElementById("transform-signal").value;
    const noise = document.getElementById("transform-noise").value;
    const cutoff = document.getElementById("transform-cutoff").value;
    const mode = document.getElementById("transform-mode").value;
    const data = await fetchJSON(`/api/transform?signal=${signal}&noise=${noise}&cutoff=${cutoff}&mode=${mode}`);
    state.transform = data;
    updateTransformMetrics(data);
    drawLineChart(document.getElementById("transform-time-chart"), {
        series: [
            { x: data.time_x, y: data.clean, color: "rgba(104, 185, 255, 0.7)", width: 1.9 },
            { x: data.time_x, y: data.noisy, color: "rgba(33, 214, 255, 0.42)", width: 1.4 },
            { x: data.time_x, y: data.filtered, color: "#7b7dff", width: 2.5 },
        ],
        xLabel: "t",
        yLabel: "幅值",
    });
    drawLineChart(document.getElementById("transform-spectrum-chart"), {
        series: [
            { x: data.freq_x, y: data.spectrum, color: "rgba(44, 214, 255, 0.72)", width: 1.7 },
            { x: data.freq_x, y: data.filtered_spectrum, color: "#7aa8ff", width: 2.3 },
        ],
        xLabel: "f (Hz)",
        yLabel: "|F(f)|",
    });
}

async function loadImageDemo() {
    const mode = document.getElementById("image-mode").value;
    const cutoff = document.getElementById("image-cutoff").value;
    const data = await fetchJSON(`/api/image-demo?mode=${mode}&cutoff=${cutoff}`);
    document.getElementById("image-clean").src = data.clean;
    document.getElementById("image-noisy").src = data.noisy;
    document.getElementById("image-spectrum").src = data.spectrum;
    document.getElementById("image-filtered").src = data.filtered;
    document.getElementById("image-retained-ratio").textContent = `${data.retained_ratio.toFixed(2)} %`;
    document.getElementById("image-summary").textContent = data.summary;
}

function renderQuiz() {
    const container = document.getElementById("quiz-list");
    container.innerHTML = "";
    window.quizQuestions.forEach((question, index) => {
        const card = document.createElement("article");
        card.className = "quiz-card";
        card.innerHTML = `
            <h3>Q${index + 1}. ${question.prompt}</h3>
            <div class="quiz-options">
                ${question.options.map((option, optionIndex) => `
                    <label class="quiz-option">
                        <input type="radio" name="question-${index}" value="${optionIndex}">
                        <span>${option}</span>
                    </label>
                `).join("")}
            </div>
        `;
        container.appendChild(card);
    });
}

function submitQuiz() {
    let score = 0;
    const details = [];
    window.quizQuestions.forEach((question, index) => {
        const checked = document.querySelector(`input[name="question-${index}"]:checked`);
        if (checked && Number(checked.value) === question.answer) {
            score += 1;
        } else {
            details.push(`第 ${index + 1} 题：${question.explanation}`);
        }
    });

    const result = document.getElementById("quiz-result");
    if (details.length === 0) {
        result.textContent = `得分 ${score}/${window.quizQuestions.length}。三层目标都打通了，可以直接进入课堂总结。`;
        return;
    }
    result.textContent = `得分 ${score}/${window.quizQuestions.length}。` + details.join(" ");
}

function debounce(fn, delay = 140) {
    let timer;
    return (...args) => {
        window.clearTimeout(timer);
        timer = window.setTimeout(() => fn(...args), delay);
    };
}

function bindEvents() {
    bindRangeDisplay(
        document.getElementById("series-terms"),
        document.getElementById("series-terms-value"),
        (value) => `${value} 项`,
    );
    bindRangeDisplay(
        document.getElementById("transition-period"),
        document.getElementById("transition-period-value"),
        (value) => Number(value).toFixed(1),
    );
    bindRangeDisplay(
        document.getElementById("transform-noise"),
        document.getElementById("transform-noise-value"),
        (value) => Number(value).toFixed(2),
    );
    bindRangeDisplay(
        document.getElementById("transform-cutoff"),
        document.getElementById("transform-cutoff-value"),
        (value) => `${Number(value).toFixed(2)} Hz`,
    );
    bindRangeDisplay(
        document.getElementById("image-cutoff"),
        document.getElementById("image-cutoff-value"),
        (value) => value,
    );

    document.getElementById("series-terms").addEventListener("input", debounce(loadSeries, 80));
    document.getElementById("transition-period").addEventListener("input", debounce(loadTransition, 80));
    document.getElementById("transform-noise").addEventListener("input", debounce(loadTransform, 120));
    document.getElementById("transform-cutoff").addEventListener("input", debounce(loadTransform, 120));
    document.getElementById("transform-signal").addEventListener("change", loadTransform);
    document.getElementById("transform-mode").addEventListener("change", loadTransform);
    document.getElementById("image-mode").addEventListener("change", loadImageDemo);
    document.getElementById("image-cutoff").addEventListener("input", debounce(loadImageDemo, 120));
    document.getElementById("quiz-submit").addEventListener("click", submitQuiz);
    window.addEventListener("resize", debounce(() => {
        if (state.series) {
            loadSeries();
        }
        if (state.transition) {
            loadTransition();
        }
        if (state.transform) {
            loadTransform();
        }
    }, 150));
}

async function init() {
    renderQuiz();
    bindEvents();
    await Promise.all([
        loadSeries(),
        loadTransition(),
        loadTransform(),
        loadImageDemo(),
    ]);
}

init().catch((error) => {
    console.error(error);
    document.getElementById("quiz-result").textContent = "页面初始化失败，请检查 Python 服务是否正常运行。";
});

