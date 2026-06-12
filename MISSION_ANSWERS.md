# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. API key bị hardcode trong code.
2. Port chạy app bị fix cứng (vd: 8000).
3. Bật chế độ Debug mode.
4. Không có health check endpoint để giám sát trạng thái của ứng dụng.
5. Không có cơ chế xử lý tín hiệu ngắt (Graceful Shutdown) để tắt app an toàn.

### Exercise 1.3: Comparison table
| Feature      | Basic (Develop) | Advanced (Production) | Tại sao quan trọng?                                                                                                         |
| --------------| -----------------| -----------------------| -----------------------------------------------------------------------------------------------------------------------------|
| Config       | Hardcode        | Env vars              | Dễ thay đổi cấu hình giữa các môi trường (dev/prod), không bị lộ thông tin nhạy cảm khi commit code.                        |
| Health check | Không có        | Có                    | Giúp hệ thống platform/orchestrator biết khi nào app bị treo để tự động restart, phục vụ tốt cho monitoring.                |
| Logging      | `print()`       | Structured JSON       | Dễ dàng parse, tìm kiếm và phân tích log tự động trên các hệ thống quản lý log tập trung (ELK, Datadog).                    |
| Shutdown     | Đột ngột        | Graceful Shutdown     | Đảm bảo hoàn thành nốt các request đang xử lý dở dang và không làm thất thoát, mất mát dữ liệu trước khi container tắt hẳn. |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. **Base image:** `python:3.11-slim` (Chứa hệ điều hành rút gọn và Python runtime).
2. **Working directory:** `/app` (Thư mục làm việc mặc định trong container nơi chứa mã nguồn ứng dụng).
3. **Tại sao COPY requirements.txt trước?** Để tận dụng cơ chế cache layer của Docker; khi mã nguồn thay đổi nhưng file requirements không đổi, Docker sẽ không cần cài lại các dependencies từ đầu, giúp tiết kiệm thời gian build.
4. **CMD vs ENTRYPOINT:** `CMD` thiết lập lệnh mặc định cho container nhưng dễ dàng bị ghi đè bởi tham số truyền vào ở lệnh `docker run`. `ENTRYPOINT` quy định ứng dụng chính luôn phải chạy, mọi tham số truyền vào sau lệnh run sẽ được gắn thêm vào đuôi của lệnh `ENTRYPOINT`.

### Exercise 2.3: Image size comparison
- Develop: ~900 MB (do dùng base image `python:3.11` tiêu chuẩn).
- Production: ~150 MB (dùng slim và multi-stage build).
- Difference: Dung lượng giảm khoảng ~80-85%.

## Part 3: Cloud Deployment

### Exercise 3.1: Deployment (Dùng Dokploy)
- URL: `https://lab12.hadp.id.vn`
- Screenshot: Xem trong thư mục `06-lab-complete/screenshots/`

## Part 4: API Security

### Exercise 4.1-4.3: Test results
- API Key Auth: Gọi api không có key (`X-API-Key`) bị từ chối với lỗi `401 Unauthorized`. Khi có key trả về `200 OK`.
- Rate Limiting: Gửi hơn 10 requests/phút liên tục sẽ nhận về lỗi `429 Too Many Requests` với message giới hạn.

### Exercise 4.4: Cost guard implementation
Sử dụng **Redis** để đếm và quản lý số lượng ngân sách đã tiêu (budget) cho từng user mỗi tháng (Key pattern: `budget:{user_id}:{month_key}`). 
Mỗi lần user gửi request, app tính dự toán chi phí (dựa trên số token in/out), sau đó cộng dồn vào ngân sách hiện tại qua lệnh `incrbyfloat`. Nếu tổng chi phí vượt mức giới hạn quy định ($10/tháng), ứng dụng từ chối request và trả về lỗi `402/503`. Budget reset đều đặn mỗi tháng nhờ việc đặt TTL (`expire`) cho key.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
- **Health & Readiness Check**: Endpoint `/health` trả về status 200 kèm uptime/metrics để liveness probe kiểm tra. `/ready` sẽ kiểm tra phụ thuộc nội tại (ping Redis), nếu các dependencies không đáp ứng, trả về `503 Service Unavailable`.
- **Graceful shutdown**: App bắt tín hiệu `SIGTERM` và `SIGINT` (thông qua thư viện `signal` và tính năng tích hợp của `uvicorn`) nhằm hoàn thành request hiện hành thay vì tắt ngay lập tức.
- **Stateless Design**: Biến app thành stateless bằng cách loại bỏ mọi dictionary/list lưu trữ trong RAM của server (`memory`). Lịch sử cuộc trò chuyện (conversation history) hoặc số liệu thống kê user đều được đẩy hết ra Redis. Do đó, traffic được load-balancer chuyển ngẫu nhiên tới các instance (Agent 1, Agent 2) mà vẫn chia sẻ đúng một bối cảnh (context).
