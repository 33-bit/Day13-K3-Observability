# Yêu cầu dashboard

Contract có thể kiểm tra bằng máy nằm tại `config/dashboard.yaml`. Hướng dẫn dựng và kiểm tra runtime nằm tại [DASHBOARD_SETUP.md](DASHBOARD_SETUP.md).

## Phạm vi và công cụ

- Công cụ trong bài nộp: mô tả dashboard bằng spec; có thể triển khai lại trên Langfuse, Grafana hoặc Streamlit.
- Nguồn dữ liệu chuẩn: `data/logs.jsonl` theo contract trong `config/dashboard.yaml`.
- Nguồn runtime tương đương: endpoint `GET /metrics`, cung cấp các field tổng hợp cho dashboard local.
- Khoảng thời gian mặc định: 60 phút.
- Refresh đề xuất: 30 giây.
- Mỗi panel phải hiển thị đơn vị và threshold/SLO line.

Dashboard chính cần đủ 6 nhóm thông tin:

1. Latency P50/P95/P99.
2. Traffic: request count hoặc QPS.
3. Error rate và breakdown theo loại lỗi.
4. Cost theo thời gian.
5. Tổng token input/output.
6. Quality proxy.

## Mapping panel và threshold

| Panel | Runtime field / event | Đơn vị | Tổng hợp | Threshold/SLO |
|---|---|---|---|---|
| Latency | `/metrics`: `latency_p50`, `latency_p95`, `latency_p99`; log `response_sent.latency_ms` | ms | P50/P95/P99 | P95 ≤ 3000 ms |
| Traffic | `/metrics`: `traffic`; log `request_received` | request, request/phút | count/rate | tối thiểu 1 request/phút khi có traffic |
| Error | `/metrics`: `error_rate_pct`, `error_breakdown`; log `request_failed.error_type` | % | error rate/breakdown | error rate ≤ 2%; cảnh báo >5% trong 3 phút |
| Cost | `/metrics`: `total_cost_usd`, `avg_cost_usd`; log `response_sent.cost_usd` | USD | total/average/theo thời gian | daily cost ≤ 2.5 USD |
| Tokens | `/metrics`: `tokens_in_total`, `tokens_out_total`; log `response_sent.tokens_in/tokens_out` | tokens | sum input/output | theo dõi ngưỡng 50,000 token trong dashboard contract |
| Quality | `/metrics`: `quality_avg`; log `response_sent.quality_score` | score 0–1 | mean | quality average ≥ 0.75 |

Tiêu chuẩn trình bày:

- Khoảng thời gian mặc định: 1 giờ.
- Tự refresh mỗi 15–30 giây nếu công cụ hỗ trợ.
- Có threshold hoặc SLO line.
- Ghi rõ đơn vị.
- Chỉ giữ 6–8 panel quan trọng ở lớp chính.
- Screenshot phải nhìn được tên panel và khoảng thời gian.

Kiểm tra contract trước khi chụp evidence:

```bash
python scripts/validate_dashboard.py
```
