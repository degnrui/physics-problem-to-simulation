#!/usr/bin/env zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_PID_FILE="$ROOT_DIR/.run-backend.pid"
FRONTEND_PID_FILE="$ROOT_DIR/.run-frontend.pid"

stop_by_pid_file() {
  local pid_file="$1"
  local name="$2"
  if [ -f "$pid_file" ]; then
    local pid
    pid="$(cat "$pid_file")"
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      echo "已停止 $name (PID $pid)"
    else
      echo "$name 进程已不存在 (PID $pid)"
    fi
    rm -f "$pid_file"
  else
    echo "未找到 $name PID 文件"
  fi
}

stop_by_pid_file "$BACKEND_PID_FILE" "后端"
stop_by_pid_file "$FRONTEND_PID_FILE" "前端"
