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
```bash
curl -X POST https://lab12.hadp.id.vn/ask \
  -H "X-API-Key: secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{"question": "Xin chào, bạn là ai?"}'
# Expected: {"question": "Xin chào, bạn là ai?", "answer": "...", "model": "gpt-4o-mini", "timestamp": "..."}
```

## Environment Variables Set
Các biến môi trường cấu hình trên Dokploy:
- `PORT` = `8000`
- `ENVIRONMENT` = `production`
- `AGENT_API_KEY` = `secret-key-123` (Nên thay đổi)
- `REDIS_URL` = `redis://redis:6379` (Nếu deploy chung với Redis trên Dokploy, hoặc dùng URL của một service Redis riêng biệt)
- `DAILY_BUDGET_USD` = `10.0`
- `RATE_LIMIT_PER_MINUTE` = `10`
- `LOG_LEVEL` = `INFO`

## Screenshots
Các ảnh chụp màn hình chứng minh trạng thái deploy:
- [Deployment dashboard (Dokploy)](screenshots/dashboard.png)
- [Service running (Logs/Metrics)](screenshots/running.png)
- [Test results (Kết quả curl trên terminal)](screenshots/test.png)
