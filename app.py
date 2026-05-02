from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    entrypoint = Path(__file__).with_name("streamlit_app.py")
    try:
        from streamlit.web import cli as stcli
    except ImportError as exc:  # pragma: no cover - import guard
        raise SystemExit("未安装 streamlit，请先执行 python -m pip install -r requirements.txt。") from exc

    sys.argv = ["streamlit", "run", str(entrypoint)]
    return stcli.main()


if __name__ == "__main__":
    raise SystemExit(main())
