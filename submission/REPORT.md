# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: VuaCanTin
- Repository URL: https://github.com/33-bit/Day13-K3-Observability
- Commit SHA tham chiếu cho bộ dashboard/evidence: `22c07e6b69e336918d44a17b7cd4d89e0a379f8d`
- Thành viên và vai trò:
  - Hoàng Danh Thái — 2A202601527 — Checkpoint 3
  - Trần Quang Trọng — 2A202601461 — Checkpoint 2 và Checkpoint 0
  - Nguyễn Quang Huy — 2A202601954 — Checkpoint 1

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 50/100 trên toàn bộ file lịch sử (các bản ghi cũ trước CP1 còn thiếu enrichment); baseline ban đầu Checkpoint 0: 30/100. Các request mới sau khi chạy code CP1 có correlation ID và PII scrub đúng.
- Tổng số traces: 10 trace mới từ load test; Langfuse project đã có các trace cũ từ CP1/CP2.
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard: https://cloud.langfuse.com/project/cmso2hs6w03toad0c5juxiru0/dashboards/cmso6n58s04vjad0jmd1bysf6
- Checkpoint 0: API health đạt; load test có 10 request HTTP 200; tạo được `data/logs.jsonl` với 22 bản ghi.

## 3. Logging và tracing

- Evidence correlation ID: `data/logs.jsonl` — 10 unique correlation IDs; xem `submission/evidence/log_validator.png`
- Evidence PII redaction: `data/logs.jsonl` — email thử nghiệm được che thành `[REDACTED_EMAIL]`; xem `submission/evidence/redacted_log.png`
- Evidence trace list/waterfall: `evidence/langfuse_trace_list.png`, `evidence/langfuse_trace_waterfall.png`.
- Giải thích một span đáng chú ý: trace waterfall cho thấy root span `run` chứa generation con; generation có latency và model `claude-sonnet-4-5`, giúp phân biệt tổng request với bước LLM.

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: v1 — `baseline`, `production` (đã rollback production về v1)
- Version/label candidate: v2 — `candidate`
- Trace ID của mỗi version: v1 — `fba7fbed523f2f488d26c8de70187dce7`; v2 — `e1c81af053fe8161bd7a06ea5c73a9e7`.
- Bằng chứng prompt/label: `evidence/prompt_versions_labels.png`, `evidence/prompt_v1_trace.png`, `evidence/prompt_v2_trace.png`.
- Bằng chứng rollback: `evidence/prompt_rollback_to_v2.png` (v2 production lúc 11:44) và `evidence/prompt_rollback_to_v1.png` (v1 production lúc 11:45).

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel có trong dashboard contract.`
- Evidence dashboard: Dashboard Langfuse đã dựng đủ 6 panel theo contract; ảnh runtime tại `evidence/langfuse_dashboard_6_panels.png`; dashboard URL nằm ở mục 2. Ảnh dùng khoảng `Past 1 day` để hiển thị dữ liệu đã ingest, còn contract quy định khoảng mặc định 60 phút.
- Sáu panel: Request traffic, Latency percentiles (P50/P95/P99), Error rate and breakdown, Cost over time, Input and output tokens, Quality proxy.
- SLO đã chọn và lý do: P95 ≤ 3000 ms (99.5%), error rate ≤ 2% (99.0%), daily cost ≤ 2.5 USD (100%), quality average ≥ 0.75 (95%) — các ngưỡng cân bằng latency, độ tin cậy, ngân sách và chất lượng proxy cho lab.
- Alert rules và runbook: Đã hoàn thiện tại `config/alert_rules.yaml` và `docs/alerts.md` với `high_latency_p95`, `elevated_error_rate`, `cost_budget_exceeded`.

## 6. Điều tra challenge

- Challenge ID: `OBS-CP2-INGESTION`
- Triệu chứng từ metrics: sau khi chạy load test, trace mới chưa xuất hiện ngay trong khoảng `Past 1 hour`, một số widget hiển thị `No data`.
- Trace ID liên quan: các trace mới từ load test; trace mẫu đã lưu trong `evidence/langfuse_trace_list.png` và `evidence/langfuse_trace_waterfall.png`.
- Log line/correlation ID liên quan: các request `req-2804354e`, `req-e86b1b60`, `req-7791454d` và các request còn lại trong lần load test cuối.
- Root cause: dữ liệu Langfuse được ingest bất đồng bộ và bộ lọc thời gian 1 giờ không bao phủ dữ liệu cũ; không phải lỗi HTTP của API (load test vẫn trả 10/10 mã 200).
- Fix action: chờ dữ liệu ingest, refresh dashboard và dùng `Past 1 day` cho ảnh evidence; vẫn giữ contract mặc định 60 phút cho vận hành.
- Preventive measure: khi kiểm tra dashboard phải đối chiếu timestamp, environment và ingestion delay; kiểm tra cả Tracing trước khi kết luận widget không có dữ liệu.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Hoàng Danh Thái — 2A202601527 | Checkpoint 3 | Commit/PR của CP3 | Thiết kế và kiểm tra phần đánh giá cuối lab |
| Trần Quang Trọng — 2A202601461 | Checkpoint 2 và Checkpoint 0; Langfuse MCP, 6 dashboard panels, SLO/alerts, evidence và report | [Commit/PR của CP2](https://github.com/33-bit/Day13-K3-Observability/commit/22c07e6b69e336918d44a17b7cd4d89e0a379f8d) | Đối chiếu logs, traces, metrics và prompt versioning để vận hành có thể kiểm chứng |
| Nguyễn Quang Huy — 2A202601954 | Checkpoint 1: enrichment, correlation ID và PII scrubbing | [Commit/PR của CP1](https://github.com/33-bit/Day13-K3-Observability/commit/458506f) | Chuẩn hoá log có context và bảo vệ dữ liệu nhạy cảm |
