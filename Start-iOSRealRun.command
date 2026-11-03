#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
if [[ "$(uname -s)" != Darwin ]]; then
  echo '此启动器仅支持 macOS。'; exit 1
fi
if [[ "${EUID}" -eq 0 ]]; then
  echo '请以普通用户启动；连接设备时会单独请求管理员密码。'; exit 1
fi
if [[ ! -x .venv/bin/python ]]; then
  PYTHON="${PYTHON:-}"
  if [[ -z "$PYTHON" ]]; then
    for candidate in python3.12 python3.13 python3.11 python3.10 python3; do
      if command -v "$candidate" >/dev/null && "$candidate" -c 'import sys; assert (3,10) <= sys.version_info[:2] < (3,14)' 2>/dev/null; then
        PYTHON="$candidate"; break
      fi
    done
  fi
  if [[ -z "$PYTHON" ]]; then
    echo '请先安装 Python 3.12，例如：brew install python@3.12'; exit 1
  fi
  "$PYTHON" -m venv .venv
fi
PYTHON="$PWD/.venv/bin/python"
# Choose before dependency installation, device mounting or password prompts.
if [[ "${1:-}" == '--check' ]]; then
  "$PYTHON" -m pip --disable-pip-version-check install -q -r requirements.txt
  "$PYTHON" main.py --check
  exit 0
fi
ROUTE_SELECTION="$(mktemp)"
trap 'rm -f "$ROUTE_SELECTION"' EXIT
"$PYTHON" "$PWD/route_picker.py" --output "$ROUTE_SELECTION"
SELECTED_ROUTE="$(cat "$ROUTE_SELECTION")"
mkdir -p logs
LOG_FILE="$PWD/logs/run-$(date +%Y%m%d-%H%M%S)-$$.log"
exec > >(tee -a "$LOG_FILE") 2>&1
finish() {
  status=$?
  rm -f "$ROUTE_SELECTION"
  if [[ "$status" -ne 0 ]]; then
    echo "启动或运行失败（退出码 $status）。日志：$LOG_FILE"
  fi
}
trap finish EXIT
echo "所选路线：$SELECTED_ROUTE"
echo "本次日志：$LOG_FILE"
"$PYTHON" -m pip --disable-pip-version-check install -q -r requirements.txt
"$PYTHON" main.py --check --route "$SELECTED_ROUTE"
if [[ "${1:-}" != '--skip-mount' ]]; then
  "$PYTHON" "$PWD/prepare_device.py"
fi
echo '请保持设备连接、解锁并信任此 Mac，开启开发者模式。'
echo '接下来输入 Mac 登录密码以建立隧道；按 Ctrl+C 停止并恢复定位。'
sudo -- "$PYTHON" "$PWD/main.py" --route "$SELECTED_ROUTE"
