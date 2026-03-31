#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/chengang/桌面/codex-workbench"
TOOLBOX="$PROJECT_DIR/scripts/toolbox.py"
VENV_ACTIVATE="$PROJECT_DIR/.venv/bin/activate"

MODE="${1:-digest}"

if [[ "$MODE" != "digest" && "$MODE" != "calendar" ]]; then
  echo "Usage: $0 [digest|calendar]" >&2
  exit 1
fi

if [[ ! -f "$TOOLBOX" ]]; then
  echo "toolbox.py not found: $TOOLBOX" >&2
  exit 1
fi

if [[ ! -f "$VENV_ACTIVATE" ]]; then
  echo "Virtualenv not found: $VENV_ACTIVATE" >&2
  exit 1
fi

source "$VENV_ACTIVATE"
cd "$PROJECT_DIR"

send_feishu() {
  local user_id="$1"
  if [[ "$MODE" == "digest" ]]; then
    python3 scripts/toolbox.py digest push today --channel feishu --user-id "$user_id"
  else
    python3 scripts/toolbox.py calendar push today --channel feishu --user-id "$user_id"
  fi
}

send_telegram() {
  local chat_id="$1"
  if [[ -z "${TELEGRAM_BOT_TOKEN:-}" ]]; then
    echo "Skipping Telegram: TELEGRAM_BOT_TOKEN is not set" >&2
    return 1
  fi

  if [[ "$MODE" == "digest" ]]; then
    python3 scripts/toolbox.py digest push today --channel telegram --chat-id "$chat_id"
  else
    python3 scripts/toolbox.py calendar push today --channel telegram --chat-id "$chat_id"
  fi
}

sent_any=0

if [[ -n "${FEISHU_USER_IDS:-}" ]]; then
  IFS=',' read -r -a feishu_ids <<< "$FEISHU_USER_IDS"
  for user_id in "${feishu_ids[@]}"; do
    user_id="${user_id//[[:space:]]/}"
    [[ -z "$user_id" ]] && continue
    send_feishu "$user_id"
    sent_any=1
  done
fi

if [[ -n "${TELEGRAM_CHAT_IDS:-}" ]]; then
  IFS=',' read -r -a telegram_ids <<< "$TELEGRAM_CHAT_IDS"
  for chat_id in "${telegram_ids[@]}"; do
    chat_id="${chat_id//[[:space:]]/}"
    [[ -z "$chat_id" ]] && continue
    send_telegram "$chat_id"
    sent_any=1
  done
fi

if [[ "$sent_any" -eq 0 ]]; then
  cat >&2 <<'EOF'
No recipients configured.

Set one or both:
  FEISHU_USER_IDS="ou_xxx,ou_yyy"
  TELEGRAM_CHAT_IDS="8241532640,8681386205"

Optional:
  TELEGRAM_BOT_TOKEN="<bot_token>"

Usage:
  ./scripts/send-digest.sh
  ./scripts/send-digest.sh calendar
EOF
  exit 1
fi
