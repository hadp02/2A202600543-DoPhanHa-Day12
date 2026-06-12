# Deployment Information

## Public URL
`https://<ten-domain-cua-ban.com>` (Thay tên domain Dokploy của bạn vào đây)

## Platform
**Dokploy** (Self-hosted VPS)

## Test Commands

### Health Check
```bash
curl https://<ten-domain-cua-ban.com>/health
# Expected: {"status": "ok", "uptime_seconds": ..., "checks": ...}
```

### API Test (with authentication)
```bash
curl -X POST https://<ten-domain-cua-ban.com>/ask \
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
Vui lòng thay thế các placeholder này bằng screenshot từ dự án của bạn (lưu ảnh vào thư mục `screenshots/` rồi push lên repo):
- [Deployment dashboard (Dokploy)](screenshots/dashboard.png)
- [Service running (Logs/Metrics)](screenshots/running.png)
- [Test results (Kết quả curl trên terminal)](screenshots/test.png)
