# Lab 12 — Complete Production Agent

Kết hợp TẤT CẢ những gì đã học trong 1 project hoàn chỉnh.

## Checklist Deliverable

- [x] Dockerfile (multi-stage, < 500 MB)
- [x] docker-compose.yml (agent + redis)
- [x] .dockerignore
- [x] Health check endpoint (`GET /health`)
- [x] Readiness endpoint (`GET /ready`)
- [x] API Key authentication
- [x] Rate limiting
- [x] Cost guard
- [x] Config từ environment variables
- [x] Structured logging
- [x] Graceful shutdown
- [x] Public URL ready (Railway / Render config)

---

## Cấu Trúc

```
06-lab-complete/
├── app/
│   ├── main.py         # Entry point — API Gateway 
│   ├── config.py       # 12-factor config
│   ├── auth.py         # API Key + JWT
│   ├── rate_limiter.py # Rate limiting
│   └── cost_guard.py   # Budget protection
├── agents/             # Day 9 Multi-Agent System
│   ├── common/         # LLM, registry/a2a clients
│   ├── registry/       # Registry service
│   ├── customer_agent/ # Entry point cho agents
│   ├── law_agent/      # Legal Orchestrator
│   ├── tax_agent/      # Tax Specialist
│   └── compliance_agent/# Compliance Specialist
├── start_agents.py     # Process manager cho agents
├── Dockerfile          # Multi-stage, production-ready
├── docker-compose.yml  # Full stack
├── railway.toml        # Deploy Railway
├── render.yaml         # Deploy Render
├── .env.example        # Template
├── .dockerignore
└── requirements.txt
```

---

## Chạy Local & Hướng Dẫn Sử Dụng

### 1. Cấu hình ban đầu
```bash
cp .env.example .env
```
Trong file `.env`:
- Bắt buộc đổi `AGENT_API_KEY` thành chuỗi bảo mật của bạn.
- Bạn có thể để trống `OPENROUTER_API_KEY` lúc test ban đầu. Khi đó, hệ thống tự động sử dụng **Mock LLM** (trả về văn bản mẫu) để bạn test pipeline A2A mà không tốn tiền. Khi sẵn sàng chạy thực tế, hãy điền key OpenRouter vào.

### 2. Khởi động hệ thống
Dự án sử dụng kiến trúc Multi-Agent. Docker sẽ khởi động API Gateway cùng với 1 Registry và 4 sub-agents.
```bash
docker compose up --build
```

### 3. Kiểm tra Health
```bash
curl http://localhost/health
```

### 4. Gửi câu hỏi cho Multi-Agent (API `/ask`)

Lưu ý: API yêu cầu header `X-API-Key` (lấy từ `.env`) và body JSON phải chứa cả `user_id` lẫn `question`.

**Trường hợp dùng Linux / Mac / Git Bash:**
```bash
API_KEY="dev-key-change-me-in-production" # Thay bằng key trong .env
curl -X POST http://localhost/ask \
     -H "X-API-Key: $API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "user123", "question": "Hợp đồng lao động có bắt buộc đóng BHXH không?"}'
```

**Trường hợp dùng Windows (CMD / PowerShell):**
Do PowerShell/CMD gặp vấn đề về encoding UTF-8 và dấu nháy đơn, hãy dùng tiếng Anh hoặc `Invoke-RestMethod`:

*Dùng PowerShell:*
```powershell
Invoke-RestMethod -Uri "http://localhost/ask" `
  -Method Post `
  -Headers @{"X-API-Key"="dev-key-change-me-in-production"; "Content-Type"="application/json"} `
  -Body '{"user_id": "test-user", "question": "Hello, who are you?"}'
```

*Dùng CMD:*
```cmd
curl -X POST http://localhost/ask ^
  -H "X-API-Key: dev-key-change-me-in-production" ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\": \"test-user\", \"question\": \"Hello, who are you?\"}"
```

---

## Deploy Railway (< 5 phút)

```bash
# Cài Railway CLI
npm i -g @railway/cli

# Login và deploy
railway login
railway init
railway variables set OPENAI_API_KEY=sk-...
railway variables set AGENT_API_KEY=your-secret-key
railway up

# Nhận public URL!
railway domain
```

---

## Deploy Render

1. Push repo lên GitHub
2. Render Dashboard → New → Blueprint
3. Connect repo → Render đọc `render.yaml`
4. Set secrets: `OPENAI_API_KEY`, `AGENT_API_KEY`
5. Deploy → Nhận URL!

---

## Kiểm Tra Production Readiness

```bash
python check_production_ready.py
```

Script này kiểm tra tất cả items trong checklist và báo cáo những gì còn thiếu.
