# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. API key bị hardcode trong code.
2. Port chạy app bị fix cứng (vd: 8000).
3. Bật chế độ Debug mode.
4. Không có health check endpoint để giám sát trạng thái của ứng dụng.
5. Không có cơ chế xử lý tín hiệu ngắt (Graceful Shutdown) để tắt app an toàn.

### Exercise 1.3: Comparison table
| Feature | Basic (Develop) | Advanced (Production) | Tại sao quan trọng? |
|---------|-----------------|-----------------------|---------------------|
| Config | Hardcode | Env vars | Dễ thay đổi cấu hình giữa các môi trường (dev/prod), không bị lộ thông tin nhạy cảm khi commit code. |
| Health check | Không có | Có | Giúp hệ thống platform/orchestrator biết khi nào app bị treo để tự động restart, phục vụ tốt cho monitoring. |
| Logging | `print()` | Structured JSON | Dễ dàng parse, tìm kiếm và phân tích log tự động trên các hệ thống quản lý log tập trung (ELK, Datadog). |
| Shutdown | Đột ngột | Graceful Shutdown | Đảm bảo hoàn thành nốt các request đang xử lý dở dang và không làm thất thoát, mất mát dữ liệu trước khi container tắt hẳn. |

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

---
## Discussion Questions Answers
Dưới đây là phần trả lời các câu hỏi thảo luận (phần này được thêm vào nhằm đầy đủ nội dung bài tập):

### Section 01: Localhost vs Production
1. **Điều gì xảy ra nếu bạn push code với API key hardcode lên GitHub public?**
   - Các hệ thống bot/scanner tự động của hacker hoặc Github Secret Scanning sẽ phát hiện ra ngay lập tức (trong vòng vài giây). Kẻ gian có thể lạm dụng key của bạn để gọi API liên tục gây thiệt hại chi phí lớn, hoặc key đó sẽ tự động bị nhà cung cấp revoke nếu họ phát hiện bị lộ.
2. **Tại sao stateless quan trọng khi scale?**
   - Khi scale ngang (chạy nhiều container một lúc qua load-balancer), các request của user có thể được đẩy tới bất kỳ container nào. Nếu app stateful (lưu context, token, rate-limit trong RAM), container thứ 2 sẽ không thể nhận dạng user đã làm việc trên container thứ 1. Stateless buộc chúng ta lưu vào Redis/DB giúp mọi container hoạt động độc lập và liền mạch.
3. **12-factor nói "dev/prod parity" — nghĩa là gì trong thực tế?**
   - Giữ môi trường Development và Production càng giống nhau càng tốt. Đảm bảo dùng cùng hệ điều hành, version thư viện, cấu hình backing services (đều xài chung 1 DB thay vì Dev xài SQLite còn Prod xài Postgres).

### Section 02: Docker
1. **Tại sao `COPY requirements.txt .` rồi `RUN pip install` TRƯỚC khi `COPY . .`?**
   - Để tận dụng cơ chế Docker layer caching. Docker cache từng bước thực thi. Vì `requirements.txt` hiếm khi thay đổi, còn mã nguồn `COPY . .` thay đổi liên tục, làm thế này giúp khi build lại Docker không phải chạy lại lệnh pip install gây lãng phí thời gian.
2. **`.dockerignore` nên chứa những gì? Tại sao `venv/` và `.env` quan trọng?**
   - Chứa các file/folder không cần thiết cho ứng dụng khi chạy như `venv/`, `.env`, `.git/`, `__pycache__`. Bỏ qua `venv/` giúp tránh làm tăng kích thước image lên mức khổng lồ và tránh lỗi môi trường Python cục bộ. Bỏ qua `.env` để bảo mật, ngăn không cho API key và secret bị đóng gói thành file cứng trong container image.
3. **Nếu agent cần đọc file từ disk, làm sao mount volume vào container?**
   - Sử dụng tham số volume khi khởi chạy: `docker run -v $(pwd)/local_folder:/container_folder image_name`, hoặc cấu hình phần `volumes:` trong `docker-compose.yml`.

### Section 03: Cloud Deployment
1. **Tại sao serverless (Lambda) không phải lúc nào cũng tốt cho AI agent?**
   - Hàm Serverless (Lambda) có giới hạn thời gian thực thi (timeout) thường là khá ngắn (vd: API Gateway của AWS là 29s). Các AI Agent đôi khi mất rất nhiều thời gian gọi API/LLM nên dễ gây quá hạn. Hơn nữa, việc tính tiền theo memory và mili-giây có thể đắt đỏ nếu thời gian chờ phản hồi dài.
2. **"Cold start" là gì? Ảnh hưởng thế nào đến UX?**
   - Là độ trễ xảy ra ở request đầu tiên khi hệ thống serverless khởi động một container mới từ trạng thái nghỉ (idle). Nó làm request tốn thêm vài giây, gây cảm giác ứng dụng bị đơ chậm với người dùng.
3. **Khi nào nên upgrade từ Railway lên Cloud Run?**
   - Khi dự án bước sang giai đoạn Production chuẩn doanh nghiệp (Enterprise), có lượng người dùng lớn cần tự động scale mạnh mẽ, yêu cầu tính an toàn bảo mật cao (chạy trong VPC), và cần tích hợp sâu với các dịch vụ khác của nền tảng GCP.

### Section 04: API Gateway & Security
1. **Khi nào nên dùng API Key vs JWT vs OAuth2?**
   - **API Key:** Sử dụng đơn giản, tốt cho giao tiếp Server-to-Server hoặc cấp quyền cho một tool bên thứ 3 truy cập API (như OpenAI cấp key cho developer).
   - **JWT:** Tốt cho Client-to-Server authentication, quản lý state (phiên đăng nhập) của user một cách phi tập trung thay vì lưu ở database nội bộ.
   - **OAuth2:** Khi cần ủy quyền và chia sẻ thông tin truy cập giữa các hệ thống (Đăng nhập bằng Google/Facebook) mà không lộ mật khẩu.
2. **Rate limit nên đặt bao nhiêu request/phút cho một AI agent?**
   - Thường dao động từ 5 đến 20 request/phút tùy chi phí API LLM và lượng câu hỏi xử lý mỗi phút, tránh tình trạng tool auto gửi request làm cạn kiệt ngân sách (exhaustion).
3. **Nếu API key bị lộ, bạn phát hiện và xử lý như thế nào?**
   - Rà soát sự bất thường trong logs hoặc hệ thống giám sát Cost/Rate-limiting để phát hiện. Xử lý bằng cách vô hiệu hóa (revoke) key bị rò rỉ lập tức trên dashboard cấu hình, tạo một key mới, cập nhật key vào file `env` an toàn và restart app.
