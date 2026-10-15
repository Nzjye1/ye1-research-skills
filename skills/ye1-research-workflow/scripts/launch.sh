#!/bin/sh
# Optional shell bootstrap. Text-only hosts read environment.md without executing this.
if [ -n "${DOCTOR_PAPER_PYTHON:-}" ]; then
  if [ ! -x "$DOCTOR_PAPER_PYTHON" ]; then
    printf '%s\n' '执行器不可用；先交可读文本与续接记录。未安装任何软件。' >&2
    exit 3
  fi
  chosen=$DOCTOR_PAPER_PYTHON
elif command -v python3 >/dev/null 2>&1; then chosen=$(command -v python3)
elif command -v python >/dev/null 2>&1; then chosen=$(command -v python)
else
  if command -v Rscript >/dev/null 2>&1; then
    printf '%s\n' 'NO_PYTHON_WRAPPER / R_DISCOVERED_NOT_VERIFIED：当前无Python包装器，已有Rscript可发现；宿主可核已有R/jsonlite或其他执行器完成适用步骤，文本继续。未执行或安装任何工具。'
  else
    printf '%s\n' 'TEXT_ONLY：当前shell找不到Python或R命令；这不证明整个宿主没有执行器。先交已读文本/可信已有结果，计算与导出待核已有能力。'
  fi
  exit 3
fi
base=${0%/*}
exec "$chosen" -B "$base/safe_run.py" "$@"
