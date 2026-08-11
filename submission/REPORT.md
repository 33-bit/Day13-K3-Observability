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

- Điểm `validate_logs.py`: **100/100** trên lượt kiểm tra cuối gồm 10 request mới — 0 bản ghi thiếu schema, 0 bản ghi thiếu enrichment, 10 correlation ID duy nhất và 0 PII leak. Evidence: `evidence/log_validator.png` và đầu ra text `evidence/log_validator_final.txt`. Trước đó, validator từng báo 50/100 khi đọc file runtime tích lũy có 20 bản ghi cũ sinh trước khi CP1 hoàn thiện; 54 dòng lịch sử đã được bảo toàn cục bộ trước khi tạo lượt kiểm tra sạch, không bị xóa hoặc dùng làm evidence giả.
- Tổng số traces: ít nhất 15 trace mới — 10 trace baseline từ CP2 và 5 trace challenge chính thức từ CP3.
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

- Challenge ID: `day13-k3-observability-v1` — incident `rag_slow`, affected feature `refund`, latency threshold `2000 ms`.
- Triệu chứng từ metrics: 5/5 request challenge trả HTTP 200 nhưng latency P95/P99 tăng từ `1196 ms` lên `2651 ms`, vượt ngưỡng challenge; error rate vẫn `0%`. Client quan sát request mất khoảng `5.3–13.3 s` khi chạy concurrency 5.
- Trace ID liên quan: trace đại diện `2801a8b30db245b2d705a5549edf1e4e` (session `k3-challenge-s04`) có observation `run` dài `2.653 s`. Bốn trace còn lại: `d78fe61adb261ea873b9b38cef4e6d40`, `d50f21bce2eef34d4fce812fd3cc916c`, `f7d3fe4bb96a6c40adfd7eca0700e1f5`, `ed1cbd92dd5f1355e8f428f4b1b54213`.
- Log line/correlation ID liên quan: trace đại diện có correlation ID `req-62ce9bad`; log `response_sent` cùng ID ghi `latency_ms=2651`, `feature=refund`. Log `incident_enabled` lúc `2026-08-11T07:54:33.889806Z` xác nhận `rag_slow` được bật trước request; excerpt được giữ tại `evidence/cp3_log_excerpt.jsonl`.
- Root cause: `rag_slow` khiến retrieval trong `app/mock_rag.py` chạy blocking `time.sleep(2.5)`, khớp với latency ổn định `2.650–2.653 s` của cả năm trace. Việc gọi synchronous `agent.run` trực tiếp trong async endpoint còn chặn event loop, làm request concurrent xếp hàng và đẩy thời gian phía client lên tới `13.3 s`.
- Fix action: đã disable incident sau khi thu evidence. Với hệ thống thật, chuyển retrieval sang async/offload blocking work, thêm timeout và fallback.
- Preventive measure: tạo span riêng cho retrieval, log `retrieval_latency_ms`, alert khi P95 vượt `2000 ms`, và thêm concurrency test để phát hiện event-loop blocking.
- Hồ sơ điều tra chi tiết: `evidence/cp3_investigation.md`. Ảnh Langfuse/dashboard CP3 đã lưu tại `evidence/cp3_metric_latency.png`, `evidence/cp3_trace_list.png`, `evidence/cp3_trace_waterfall.png` và `evidence/cp3_log_correlation.png`.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Hoàng Danh Thái — 2A202601527 | Checkpoint 3: chạy challenge chính thức, điều tra Metrics → Traces → Logs, xác định root cause và đề xuất fix/phòng ngừa | Commit/PR của CP3 | Phân biệt latency trong trace với thời gian client và nhận diện blocking work trong async endpoint |
| Trần Quang Trọng — 2A202601461 | Checkpoint 2 và Checkpoint 0; Langfuse MCP, 6 dashboard panels, SLO/alerts, evidence và report | [Commit/PR của CP2](https://github.com/33-bit/Day13-K3-Observability/commit/22c07e6b69e336918d44a17b7cd4d89e0a379f8d) | Đối chiếu logs, traces, metrics và prompt versioning để vận hành có thể kiểm chứng |
| Nguyễn Quang Huy — 2A202601954 | Checkpoint 1: enrichment, correlation ID và PII scrubbing | [Commit/PR của CP1](https://github.com/33-bit/Day13-K3-Observability/commit/458506f) | Chuẩn hoá log có context và bảo vệ dữ liệu nhạy cảm |
