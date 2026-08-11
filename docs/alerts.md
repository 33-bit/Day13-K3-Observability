# Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1 — High latency P95

- Tên: `high_latency_p95`
- Severity: `warning`
- SLI/SLO liên quan: `latency_p95_ms`, mục tiêu P95 không vượt quá 3000 ms trong 99.5% request của cửa sổ 28 ngày.
- Điều kiện và thời gian duy trì: `latency_p95_ms > 3000ms for 5 minutes`.
- Ảnh hưởng tới người dùng: Câu trả lời chậm, request có thể timeout và trải nghiệm chat suy giảm.
- Ba bước kiểm tra đầu tiên:
  1. Mở panel latency và traffic để xác định P95 tăng trong khoảng thời gian nào và có đi cùng traffic tăng hay không.
  2. Mở một trace chậm trong cùng khoảng thời gian, so sánh thời gian các span và xác định span bất thường.
  3. Dùng correlation ID của trace để tìm `request_received`/`response_sent` tương ứng trong log và kiểm tra feature, model, token và cost.
- Mitigation tạm thời: Giảm tải hoặc concurrency, tạm chuyển traffic sang cấu hình/prompt ổn định gần nhất và rollback thay đổi gần đây nếu trace xác nhận thay đổi đó liên quan.
- Owner: `on-call-engineer`

## Alert 2 — Elevated error rate

- Tên: `elevated_error_rate`
- Severity: `critical`
- SLI/SLO liên quan: `error_rate_pct`, mục tiêu error rate dưới 2% với target 99.0%.
- Điều kiện và thời gian duy trì: `error_rate_pct > 5 for 3 minutes`.
- Ảnh hưởng tới người dùng: Nhiều request thất bại hoặc trả lỗi, người dùng không nhận được câu trả lời.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra error rate và breakdown theo `error_type` để biết lỗi tăng đột biến thuộc nhóm nào.
  2. Mở trace của request lỗi để xác định span thất bại và xem lỗi xảy ra trước hay sau bước sinh câu trả lời.
  3. Dùng correlation ID để đối chiếu log `request_failed`, kiểm tra thời điểm, feature, model và thông tin lỗi đã được redact.
- Mitigation tạm thời: Rollback release/cấu hình gần nhất, tắt luồng có tỷ lệ lỗi cao nếu có thể và chuyển traffic sang fallback ổn định; cập nhật người dùng nếu lỗi kéo dài.
- Owner: `on-call-engineer`

## Alert 3 — Cost budget exceeded

- Tên: `cost_budget_exceeded`
- Severity: `warning`
- SLI/SLO liên quan: `daily_cost_usd`, ngân sách ngày không vượt quá 2.5 USD.
- Điều kiện và thời gian duy trì: `daily_cost_usd > 2.5`.
- Ảnh hưởng tới người dùng: Có nguy cơ chạm giới hạn ngân sách, bị throttling hoặc phải giảm chất lượng/phạm vi phục vụ.
- Ba bước kiểm tra đầu tiên:
  1. So sánh total cost với traffic và tổng input/output tokens để phân biệt traffic tăng với cost/request tăng.
  2. Mở các trace có cost cao, kiểm tra model, prompt version, token usage và feature.
  3. Kiểm tra thay đổi gần đây ở prompt/model và xác nhận cost được ghi đúng trong `response_sent`.
- Mitigation tạm thời: Giới hạn traffic hoặc concurrency, chuyển sang model/prompt tiết kiệm hơn và tạm giảm các request có mức tiêu thụ bất thường.
- Owner: `team-lead`
