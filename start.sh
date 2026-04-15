#!/usr/bin/env zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_LOG="$ROOT_DIR/.run-backend.log"
FRONTEND_LOG="$ROOT_DIR/.run-frontend.log"
BACKEND_PID_FILE="$ROOT_DIR/.run-backend.pid"
FRONTEND_PID_FILE="$ROOT_DIR/.run-frontend.pid"

cd "$ROOT_DIR"

if [ -f ".env" ]; then
  set -a
  source .env
  set +a
elif [ -f ".env.example" ]; then
  set -a
  source .env.example
  set +a
fi

BACKEND_HOST="${BACKEND_HOST:-127.0.0.1}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
EXECUTOR_MODE="${EXECUTOR_MODE:-dev_proxy}"

if [ ! -x ".venv/bin/python" ]; then
  echo "缺少 .venv/bin/python，请先创建并安装后端依赖。"
  echo "建议执行: python3 -m venv .venv && .venv/bin/pip install -r backend/requirements.txt"
  exit 1
fi

if [ ! -d "node_modules" ]; then
  echo "缺少 node_modules，请先执行 npm install"
  exit 1
fi

if [ -f "$BACKEND_PID_FILE" ] && kill -0 "$(cat "$BACKEND_PID_FILE")" 2>/dev/null; then
  echo "后端已在运行 (PID $(cat "$BACKEND_PID_FILE"))"
else
  rm -f "$BACKEND_PID_FILE"
  nohup env EXECUTOR_MODE="$EXECUTOR_MODE" MODEL_API_BASE_URL="${MODEL_API_BASE_URL:-}" MODEL_API_KEY="${MODEL_API_KEY:-}" MODEL_NAME="${MODEL_NAME:-}" EXECUTOR_TIMEOUT_MS="${EXECUTOR_TIMEOUT_MS:-45000}" EXECUTOR_MAX_RETRIES="${EXECUTOR_MAX_RETRIES:-2}" .venv/bin/python -m uvicorn backend.app.main:app --reload --host "$BACKEND_HOST" --port "$BACKEND_PORT" >"$BACKEND_LOG" 2>&1 &
  echo $! >"$BACKEND_PID_FILE"
  echo "后端启动中... PID $(cat "$BACKEND_PID_FILE")"
fi

if [ -f "$FRONTEND_PID_FILE" ] && kill -0 "$(cat "$FRONTEND_PID_FILE")" 2>/dev/null; then
  echo "前端已在运行 (PID $(cat "$FRONTEND_PID_FILE"))"
else
  rm -f "$FRONTEND_PID_FILE"
  nohup env VITE_BACKEND_ORIGIN="http://$BACKEND_HOST:$BACKEND_PORT" /opt/homebrew/bin/npm run dev -- --host "$BACKEND_HOST" --port "$FRONTEND_PORT" >"$FRONTEND_LOG" 2>&1 &
  echo $! >"$FRONTEND_PID_FILE"
  echo "前端启动中... PID $(cat "$FRONTEND_PID_FILE")"
fi

echo "等待服务启动..."
sleep 2

echo "后端健康检查:"
if curl -fsS "http://$BACKEND_HOST:$BACKEND_PORT/api/health"; then
  echo ""
else
  echo "后端未通过健康检查，请查看: $BACKEND_LOG"
fi

echo "前端首页检查:"
if curl -fsS "http://$BACKEND_HOST:$FRONTEND_PORT" >/dev/null; then
  echo "ok"
else
  echo "前端未通过检查，请查看: $FRONTEND_LOG"
fi

echo ""
echo "访问地址: http://$BACKEND_HOST:$FRONTEND_PORT"
echo "执行模式: $EXECUTOR_MODE"
echo "后端日志: $BACKEND_LOG"
echo "前端日志: $FRONTEND_LOG"
echo ""
echo "停止服务可执行: ./stop.sh"
