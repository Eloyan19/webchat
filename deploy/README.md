# Деплой webchat на VPS (jorchik.com)

Публичный URL: **https://jorchik.com** (TLS — Certbot, уже настроен).

## Компоненты
- **backend** — `webchat.service` (systemd), uvicorn на `127.0.0.1:8000`.
  Ключ `DEEPSEEK_API_KEY` подтягивается через `EnvironmentFile=backend/.env`
  (в git НЕ попадает). `RAG_URL` задан в юните.
- **frontend** — прод-сборка Vite (`npm run build`, base = same-origin через
  `frontend/.env.production`), выложена в `/var/www/webchat`, раздаётся nginx.
- **nginx** — блок из `nginx-jorchik.conf` внутри server-блока jorchik.com:
  `/` → статика, `/chat` и `/health` → проксируются на backend.

## Первичная установка
```sh
# backend service
sudo cp deploy/webchat.service /etc/systemd/system/webchat.service
sudo systemctl daemon-reload
sudo systemctl enable --now webchat.service

# frontend static
cd frontend && npm run build && cd ..
sudo mkdir -p /var/www/webchat
sudo rsync -a --delete frontend/dist/ /var/www/webchat/

# nginx: вставить содержимое deploy/nginx-jorchik.conf в server-блок
# /etc/nginx/sites-available/jorchik.com, затем:
sudo nginx -t && sudo systemctl reload nginx
```

## Обновление (redeploy)
```sh
# backend
sudo systemctl restart webchat.service

# frontend
cd frontend && npm run build && cd ..
sudo rsync -a --delete frontend/dist/ /var/www/webchat/
```

## Проверка
```sh
curl https://jorchik.com/health
curl -X POST https://jorchik.com/chat -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"ping"}]}'
```
