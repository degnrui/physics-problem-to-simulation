#!/usr/bin/env bash

set -eu

# Fill these placeholders before running if you prefer editing the script directly.
MODEL_PROVIDER="${MODEL_PROVIDER:-nvidia}"
OPENAI_API_KEY="${OPENAI_API_KEY:-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}"
OPENAI_BASE_URL="${OPENAI_BASE_URL:-https://integrate.api.nvidia.com/v1}"
OPENAI_MODEL="${OPENAI_MODEL:-minimaxai/minimax-m2.5}"

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET_FILE="$ROOT_DIR/backend/.env.local"

if [ "$OPENAI_API_KEY" = "PASTE_YOUR_API_KEY_HERE" ] || [ -z "$OPENAI_API_KEY" ]; then
  echo "OPENAI_API_KEY 还没有填写。"
  echo "请先编辑 scripts/setup_model_api.sh 顶部变量，或这样执行："
  echo "OPENAI_API_KEY=你的key OPENAI_MODEL=gpt-5-mini ./scripts/setup_model_api.sh"
  exit 1
fi

cat > "$TARGET_FILE" <<EOF
MODEL_PROVIDER=$MODEL_PROVIDER
OPENAI_API_KEY=$OPENAI_API_KEY
OPENAI_BASE_URL=$OPENAI_BASE_URL
OPENAI_MODEL=$OPENAI_MODEL
EOF

chmod 600 "$TARGET_FILE"

echo "已写入本地私密配置：$TARGET_FILE"
echo "该文件已被 .gitignore 忽略，不会被提交到 GitHub。"

if docker compose ps backend >/dev/null 2>&1; then
  docker compose restart backend >/dev/null 2>&1 || true
  echo "已尝试重启 backend 容器。"
fi

echo "下一步："
echo "1. 重新启动服务：docker compose up -d"
echo "2. 检查后端健康：curl -sS http://127.0.0.1:8000/api/health"
