# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: VuaCanTin
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:
  - Hoàng Danh Thái — 2A202601527 — Checkpoint 3
  - Trần Quang Trọng — 2A202601461 — Checkpoint 2 và Checkpoint 0
  - Nguyễn Quang Huy — 2A202601954 — Checkpoint 1

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 (hiện tại; baseline ban đầu Checkpoint 0: 30/100)
- Tổng số traces:
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard:
- Checkpoint 0: API health đạt; load test có 10 request HTTP 200; tạo được `data/logs.jsonl` với 22 bản ghi.

## 3. Logging và tracing

- Evidence correlation ID: `data/logs.jsonl` — 10 unique correlation IDs; xem `submission/evidence/log_validator.png`
- Evidence PII redaction: `data/logs.jsonl` — email thử nghiệm được che thành `[REDACTED_EMAIL]`; xem `submission/evidence/redacted_log.png`
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`:
- Evidence dashboard:
- SLO đã chọn và lý do:
- Alert rules và runbook:

## 6. Điều tra challenge

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Hoàng Danh Thái — 2A202601527 | Checkpoint 3 | | |
| Trần Quang Trọng — 2A202601461 | Checkpoint 2 và Checkpoint 0 | | |
| Nguyễn Quang Huy — 2A202601954 | Checkpoint 1 | | |
