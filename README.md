# chatgpt-telegram-bot

## 使用

- 将仓库克隆到本地

- 在 `docker-compose.yml` 中填写 OpenAI API key 和 Telegram bot token

- 在 `config.py` 中填写管理员的 Telegram user id, 模型名和 prompt

- `docker compose build`

- `docker compose up -d`

## 说明

本仓库相对于源仓库的改动：

- 重组了代码结构

- 将 PTB 升级至 20.1 版本以使用异步 handler

- 支持多 prompt