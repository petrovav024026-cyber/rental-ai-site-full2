# Rental AI Assistant — Website

Минималистичный сайт проекта с приёмом заявок и обратной связью. Готов к деплою на Render.

## Локальный запуск
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```
Откройте http://127.0.0.1:8000

## Render
- Подключите репозиторий, Render прочитает `render.yaml`.
- Переменные окружения задайте в Dashboard (ADMIN_*, ALBATO_WEBHOOK_URL, и т.д.).

## Автодеплой (GitHub Actions)
Добавьте секрет `RENDER_DEPLOY_HOOK` с Deploy Hook URL из Render.
