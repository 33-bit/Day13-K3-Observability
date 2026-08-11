# Checkpoint 3 — Official Challenge Investigation

## Challenge

- Challenge ID: `day13-k3-observability-v1`
- Cohort: `K3`
- Incident: `rag_slow`
- Affected feature: `refund`
- Challenge latency threshold: `2000 ms`
- Execution time: 2026-08-11 07:54 UTC (14:54 Asia/Bangkok)
- Result: 5/5 challenge requests returned HTTP 200.

## Metrics evidence

| Metric | Before challenge | After challenge | Interpretation |
|---|---:|---:|---|
| Traffic | 10 | 15 | Five official requests were processed |
| Latency P50 | 150 ms | 151 ms | Historical baseline still dominates the median |
| Latency P95 | 1196 ms | 2651 ms | Exceeded the challenge threshold of 2000 ms |
| Latency P99 | 1196 ms | 2651 ms | Tail latency increased sharply |
| Error rate | 0% | 0% | Incident affects latency, not availability |
| Total cost | $0.0221 | $0.0326 | Normal increase from five additional requests |
| Quality average | 0.88 | 0.8733 | No material quality degradation |

Client-observed challenge durations were approximately 5.3–13.3 seconds under concurrency 5. The application metric records about 2.65 seconds inside each agent run; the larger client duration is queueing caused by blocking synchronous work inside the async `/chat` handler.

## Trace-to-log correlation

| Session ID | Trace ID | Correlation ID | Trace/run latency |
|---|---|---|---:|
| `k3-challenge-s01` | `d78fe61adb261ea873b9b38cef4e6d40` | `req-6592dc03` | 2.652 s |
| `k3-challenge-s02` | `d50f21bce2eef34d4fce812fd3cc916c` | `req-589679c6` | 2.653 s |
| `k3-challenge-s03` | `f7d3fe4bb96a6c40adfd7eca0700e1f5` | `req-524d1e4d` | 2.652 s |
| `k3-challenge-s04` | `2801a8b30db245b2d705a5549edf1e4e` | `req-62ce9bad` | 2.653 s |
| `k3-challenge-s05` | `ed1cbd92dd5f1355e8f428f4b1b54213` | `req-39a76993` | 2.652 s |

Representative evidence chain:

1. At `2026-08-11T07:54:33.889806Z`, log event `incident_enabled` records incident `rag_slow`.
2. Trace `2801a8b30db245b2d705a5549edf1e4e` starts at `2026-08-11T07:54:34.272Z` for session `k3-challenge-s04`.
3. The trace metadata contains correlation ID `req-62ce9bad`; its `run` generation lasts `2.653 s`.
4. `data/logs.jsonl` contains `request_received` and `response_sent` with the same correlation ID. The response log records `latency_ms=2651`, `feature=refund`, HTTP success and no error.
5. At `2026-08-11T07:54:47.874392Z`, log event `incident_disabled` confirms cleanup.

The preserved structured-log excerpt is `cp3_log_excerpt.jsonl`.

## Root cause

The official challenge enabled `rag_slow`. When this flag is active, `app/mock_rag.py` executes a blocking `time.sleep(2.5)` before returning retrieval documents. This explains the stable 2.650–2.653 second latency across all five challenge traces and the P95 increase above 2000 ms.

An amplifying factor is that the async `/chat` endpoint directly invokes the synchronous `agent.run`. With concurrency 5, the blocking retrieval stalls the event loop and serializes requests, which explains why client-observed durations reached 13.3 seconds even though each trace records about 2.65 seconds of processing.

## Fix action

- Disable the `rag_slow` incident after evidence collection (completed).
- For a real retrieval backend, remove the blocking delay, use an async client or offload blocking retrieval to a worker thread, and configure a retrieval timeout/fallback.

## Preventive measures

- Instrument retrieval as a dedicated span and record `retrieval_latency_ms` in structured logs.
- Alert when latency P95 exceeds 2000 ms for the challenge/SLO window.
- Add concurrency tests that compare client-observed duration with per-trace duration.
- Use timeout, caching and fallback behavior for the retrieval dependency.

## Evidence screenshots

The following files are saved in this directory and referenced from `submission/REPORT.md`:

- `cp3_metric_latency.png`: dashboard showing the latency spike, time range, unit and threshold.
- `cp3_trace_list.png`: challenge traces filtered by `k3-challenge-*` or one of the trace IDs above.
- `cp3_trace_waterfall.png`: representative trace `2801a8b30db245b2d705a5549edf1e4e`, showing the `run` duration and metadata/correlation ID.
- `cp3_log_correlation.png`: terminal/editor view containing `incident_enabled`, `req-62ce9bad` request/response logs, and `incident_disabled`.

Direct links for the manual UI step:

- Dashboard: <https://cloud.langfuse.com/project/cmso2hs6w03toad0c5juxiru0/dashboards/cmso6n58s04vjad0jmd1bysf6>
- Representative trace: <https://cloud.langfuse.com/project/cmso2hs6w03toad0c5juxiru0/traces/2801a8b30db245b2d705a5549edf1e4e>
