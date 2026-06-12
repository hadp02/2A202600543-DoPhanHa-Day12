# Deployment Information

## Public URL
`https://lab12.hadp.id.vn`

## Platform
**Dokploy** (Self-hosted VPS)

## Test Commands

### Health Check
```bash
curl https://lab12.hadp.id.vn/health
# Expected: {"status": "ok", "uptime_seconds": ..., "checks": ...}
```

### API Test (with authentication)

**Trên Linux / Mac (hoặc Git Bash):**
```bash
curl -X POST https://lab12.hadp.id.vn/ask \
  -H "X-API-Key: secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user", "question": "Hello, who are you?"}'
```

**Trên Windows (CMD / PowerShell):**
(Vì Windows curl không hỗ trợ bọc JSON bằng dấu nháy đơn `''` nên phải dùng dấu nháy kép `""` và escape bên trong)
```cmd
curl -X POST https://lab12.hadp.id.vn/ask ^
  -H "X-API-Key: secret-key-123" ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\": \"test-user\", \"question\": \"Hello, who are you?\"}"
```

# Expected output: 
# {"user_id": "test-user", "question": "Hello, who are you?", "answer": "...", "history_length": 1, "model": "...", "timestamp": "..."}

## Environment Variables Set
Các biến môi trường cấu hình trên Dokploy:
- `PORT` = `8000`
- `ENVIRONMENT` = `production`
- `AGENT_API_KEY` = `secret-key-123` (Nên thay đổi)
- `REDIS_URL` = `redis://redis:6379` (Nếu deploy chung với Redis trên Dokploy, hoặc dùng URL của một service Redis riêng biệt)
- `DAILY_BUDGET_USD` = `10.0`
- `RATE_LIMIT_PER_MINUTE` = `10`
- `LOG_LEVEL` = `INFO`
- `OPENROUTER_API_KEY` = `your-api-key`
- `OPENROUTER_MODEL` = `deepseek/deepseek-v4-flash`
- `CUSTOMER_AGENT_URL` = `http://localhost:10100`
- `REGISTRY_URL` = `http://localhost:10000`

## System Architecture & APIs

Trong kiến trúc Multi-Agent hiện tại, hệ thống bao gồm các APIs sau:

### 1. External APIs (Third-party)
- **OpenRouter API**: `https://openrouter.ai/api/v1/chat/completions` (Giao tiếp với các LLM như DeepSeek, Claude, v.v.)

### 2. Public API (Exposed via Nginx / Dokploy)
- **API Gateway (FastAPI)**: `https://lab12.hadp.id.vn`
  - `GET /health` : Kiểm tra trạng thái gateway và fallback LLM.
  - `GET /ready` : Kiểm tra kết nối Redis.
  - `POST /ask` : Gửi câu hỏi pháp lý. Yêu cầu `X-API-Key`.
  - `GET /metrics` : Lấy số liệu giám sát (rate limit, cost). Yêu cầu `X-API-Key`.

### 3. Internal APIs (A2A Multi-Agent Protocol)
Các Agents bên dưới chạy nội bộ trong container và giao tiếp qua A2A protocol (HTTP POST, không expose ra ngoài):
- **Registry Service**: `http://localhost:10000` (Service discovery & Tracing)
- **Customer Agent**: `http://localhost:10100` (Entry-point nhận request từ API Gateway)
- **Law Agent**: `http://localhost:10101` (Legal Orchestrator)
- **Tax Agent**: `http://localhost:10102` (Tax Specialist)
- **Compliance Agent**: `http://localhost:10103` (Compliance Specialist)

## Screenshots
Các ảnh chụp màn hình chứng minh trạng thái deploy:
- [Deployment dashboard (Dokploy)](screenshots/dashboard.png)
- [Service running (Logs/Metrics)](screenshots/running.png)
- [Test results (Kết quả curl trên terminal)](screenshots/test.png)
