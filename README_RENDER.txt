Инструкция по деплою на Render.com (Telegram-бот на aiogram)

1) Зарегистрируйся на https://render.com и создай новый Web Service -> 'Private Service' or 'Worker'.
2) Выбери 'Deploy a Dockerfile' или 'Deploy from a repo'. Для простоты выбери 'Deploy' -> 'Manual' и загрузи ZIP через GitHub или используй 'Deploy from ZIP' (Render поддерживает деплой из GitHub).
3) В настройках сервиса укажи команду запуска: `worker: python PythonProject3/tattoo_studio_bot_main.py` (Render использует Procfile при деплое из репозитория).
4) В разделе Environment -> Environment Variables добавь переменную `BOT_TOKEN` и вставь **новый** токен от @BotFather (никогда не выкладывай токен публично).
5) Установи `requirements.txt` — Render автоматически выполнит pip install -r requirements.txt.
6) Запусти сервис и проверь логи (Logs) — если всё ок, бот заработает и будет онлайн 24/7.

Если тебе нужно — могу подготовить шаги для Railway.app или Render из ZIP непосредственно (инструкция по связке с GitHub тоже возможна).
