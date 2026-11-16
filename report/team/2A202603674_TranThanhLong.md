# Báo cáo cá nhân — 2A202603674_TranThanhLong

## 1. Thông tin thành viên

- Họ tên: Trần Thanh Long
- MSSV: 2A202603674
- Email: 26ai.longtt2@vinuni.edu.vn
- GitHub: https://github.com/Monstucture/K5-L3A-DAY08-MID-FromWorkflowsToAgents

## 2. Phần việc phụ trách

- Shape C — orchestrator + handoff (`src/lab8/shapes/orchestrator.py`), gồm CP2 (cài shape) và CP3 (truyền `crash_at`).
- Chạy crash test và benchmark public (`src/reports/crash.json`, `src/reports/benchmark.json`).
- Rà soát code shape workflow và single của bạn cùng nhóm trước khi chốt.

## 3. Đóng góp cụ thể

- `f7e31af` — viết shape orchestrator:
  - Orchestrator đọc claim bằng `get_claim_view`; claim không tồn tại → `failed`, thiếu `order_id` → `needs_info`.
  - Dựng handoff bằng `make_handoff` với `facts={}` và chỉ 3 tool đọc: `lookup_order`, `lookup_refund_history`, `compute_compensation`. Không đưa `parent_secret`, `raw_headers` hay claim row vào handoff.
  - Investigator chạy qua `run_readonly_investigators`, không có tool ghi. Đơn không thuộc principal → `escalated`.
  - Quote lấy từ order row qua `compute_compensation` (bỏ qua số ngày trễ trong ticket). Quote 0 → `denied`.
  - Chỉ orchestrator gọi `durability.issue_refund` với **quote đầy đủ**; host tự trừ phần đã hoàn trước đó (T13, T14).
  - Trace chỉ ghi handoff đã sanitize, tóm tắt investigator (visible/reason/refund history), quote và decision; trace được ghi ở mọi nhánh return.
- `06fa360` — CP3: truyền `crash_at` vào `issue_refund`, không bắt `InjectedCrash`.
- `faa3e99`, `7721b6f` — chạy `lab8.crash_test` (20/20) và `lab8.benchmark` 4 shape × 5 seed trên bộ public.
- `a36161d` — sửa nhỏ sau khi rà code nhóm: xóa code chết còn sót từ stub trong `workflow.py`; `single.py` trả `failed` cho claim không tồn tại (thống nhất với 3 shape còn lại) và ghi `reason` khi quote = 0.
- `b604bbc` — chạy lại benchmark 4 shape sau khi `reports/benchmark.json` bị ghi đè chỉ còn swarm (check_submission yêu cầu đủ 4 shape).
- `6abdf8b` — điền dòng `Run id dẫn chứng` (`R-workflow-C-001-s11`) và `Secret leak / approval bypass` (0 / 0, đã grep 70 trace workflow không có secret/PII) trong `decision_adr.md`; `check_submission` ra 0 FAIL, 0 WARN.
- Quyết định kỹ thuật: để `facts` rỗng trong handoff vì investigator tự đọc order row — không có gì từ parent context cần chuyển qua ranh giới, nên không có gì để lộ.
- Test: thêm `src/tests/test_orchestrator_handoff.py` (2 test) — với C-010, handoff trong trace chỉ có tool đọc và facts trong allowlist, trace không chứa `parent_secret`, `raw_headers`, nội dung ticket hay PII; C-002 (ticket ghi trễ 5 ngày, order ghi 2) bị `denied` ở seed 55, nơi swarm sai.

## 4. Bằng chứng

- Commit: `f7e31af`, `06fa360`, `faa3e99`, `7721b6f`, `a36161d`, `b604bbc`, `6abdf8b`.
- `python -m lab8.check_submission` trên `main` (sau `6abdf8b`): 0 FAIL, 0 WARN.
- Test: `python -m pytest -q -m student -o addopts= -k orchestrator` → 62 passed (gồm `test_t11_retry_keeps_one_refund[orchestrator]`, `test_t12_crash_before_checkpoint_does_not_double_pay[orchestrator]`). Toàn bộ ma trận student: 248 passed; `python -m pytest -q`: 56 passed (gồm 2 test mới).
- `python -m lab8.check_submission`: `shape orchestrator: format đúng, 12/12 claim public pass ở seed 11`.
- Run id: `R-orchestrator-C-001-s11` (trace trong `src/traces/`).
- Benchmark public (orchestrator, 70 trial): pass 1.000, pass^5 1.000, variance 0, cost/success 47.23 VND (mô phỏng).
- Crash: `src/reports/crash.json` → `crash_safety 20/20`.

## 5. Công cụ AI đã dùng

- Claude Code (Claude): viết bản nháp shape orchestrator theo docstring, giải thích lỗi khi làm CP3, rà code workflow/single, đọc slide hướng dẫn và tóm tắt các claim public.
- Tự kiểm tra: chạy ma trận student cho từng shape, `pytest -q`, `check_submission`, crash test và benchmark; grep trace để chắc không có `CANARY_SECRET_`, `parent_secret`, `raw_headers`. Dùng AI filled trace commit

## 6. Tự đánh giá

- Hoàn thành shape orchestrator đạt đủ 62 test, qua 3 must-pass (không bypass approval, không lộ secret, crash 20/20).
- Bài học: lần đầu làm CP3 tôi giữ lại dòng `del crash_at`, gây `UnboundLocalError` ở mọi claim có refund (37 test fail). Test bắt được liền, chạy lại ma trận sau mỗi thay đổi nhỏ là cần thiết.
- Hiểu ra vì sao nhóm chọn workflow dù orchestrator cũng pass 100%: cùng độ đúng thì shape ít tự chủ, rẻ hơn (27.86 so với 47.23 /success) là lựa chọn hợp lý hơn.
