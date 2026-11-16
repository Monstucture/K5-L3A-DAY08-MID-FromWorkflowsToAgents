# Báo cáo cá nhân — Quách Ngọc Phúc

## 1. Thông tin thành viên

- Họ tên: Quách Ngọc Phúc
- MSSV: 2A202603665
- Email: quachphucbk@gmail.com
- GitHub: https://github.com/quachphucbk
- Nhóm: MID — Lớp L3A

## 2. Phần việc phụ trách

Triển khai shape A — workflow tại `src/lab8/shapes/workflow.py` và bổ sung test kiểm tra luồng approval. Workflow xử lý claim bằng các bước Python cố định, không gọi model để quyết định tiền hoàn.

Phạm vi gồm đọc claim, kiểm tra order theo principal, tính quote, gọi host ghi refund, ghi trace và trả đúng `RunResult`. Policy, ledger và cơ chế idempotency sử dụng thành phần có sẵn của lab.

## 3. Đóng góp cụ thể

### Triển khai workflow — CP2 và CP3

Commit `9bdf78dfea6eba71e6346b6730848103cc98b706` thay stub bằng luồng xử lý hoàn chỉnh:

1. Khởi tạo database, `Budget` và `Trace`.
2. Đọc claim bằng `get_claim_view`; xử lý claim không tồn tại và thiếu `order_id`.
3. Dùng `lookup_order` kiểm tra quyền sở hữu; trả `escalated` nếu đơn không khả dụng.
4. Tính quote bằng `compute_compensation` từ order có cấu trúc, không tin số ngày trong ticket.
5. Quote bằng 0 trả `denied`; quote dương được chuyển đầy đủ cho `issue_refund`.
6. Chuyển kết quả host thành `resolved`, `denied` hoặc `failed` khi có conflict; dùng hàm phụ `end()` và `finish()` để thống nhất kết quả và ghi trace.

Workflow truyền `crash_at` xuống host, không nuốt `InjectedCrash`, và đóng connection trong `finally`. Host chịu trách nhiệm approval, trần theo đơn và chống ghi trùng. Quote không bị trừ trước: entitlement 150.000 VND với lịch sử đã hoàn 30.000 VND vẫn được truyền là 150.000 VND để host ghi phần chênh 120.000 VND.

Trace chỉ ghi trạng thái lookup, quote, kết quả host và quyết định cuối; không dump nguyên claim/order, ticket, secret hoặc thông tin cá nhân.

### Bổ sung hai test riêng cho workflow

| File / test | Tình huống và điều kiện kiểm tra |
| --- | --- |
| `src/tests/test_workflow_approval_cap.py` — `test_workflow_capped_approval_preserves_quote_on_retry` | Claim đủ điều kiện 35.000 VND nhưng approval chỉ 20.000 VND. Proposal vẫn 35.000, effect thực là 20.000; retry với seed khác vẫn một refund và một committed audit. |
| `src/tests/test_workflow_revoked_approval.py` — `test_workflow_revoked_approval_is_not_rescued_by_spare` | Approval được claim trỏ tới bị thu hồi, dù tồn tại approval hợp lệ khác cho cùng claim. Workflow phải trả `denied`, giữ quote 35.000, không tạo refund và có audit `policy_denied` với lý do `approval_revoked`; retry không nhân đôi audit. |

Hai test dùng database tạm từ fixture `public_db`; chỉ sửa dữ liệu của database test, không sửa fixture public trong repo. Mỗi test chạy seed 11 rồi 55 trên cùng database để kiểm tra retry. Assertion đối chiếu cả `RunResult` và dữ liệu SQLite, tránh chỉ dựa vào kết quả tự khai. Trace được ghi trong thư mục tạm của pytest.

## 4. Bằng chứng

- Code: [workflow.py](../../src/lab8/shapes/workflow.py).
- Commit triển khai: [9bdf78d — do workflow](https://github.com/Monstucture/K5-L3A-DAY08-MID-FromWorkflowsToAgents/commit/9bdf78dfea6eba71e6346b6730848103cc98b706).
- Test approval cap: [test_workflow_approval_cap.py](../../src/tests/test_workflow_approval_cap.py).
- Test approval thu hồi: [test_workflow_revoked_approval.py](../../src/tests/test_workflow_revoked_approval.py).

Lệnh kiểm tra hai test, chạy trong `src/`:

```bash
python -m pytest -q -p no:cacheprovider -m student -o addopts= tests/test_workflow_approval_cap.py tests/test_workflow_revoked_approval.py
```

Kết quả lần kiểm tra khi bổ sung báo cáo: **2 passed**. Mỗi file có một test case; vòng lặp hai seed bên trong dùng để kiểm retry nên không được pytest đếm thành hai case riêng. Hai file test cần được commit và đưa vào lịch sử nhánh nộp; bổ sung hash commit test sau khi commit thực tế.

Lệnh kiểm tra toàn bộ workflow:

```bash
python -m pytest -q -m student -o addopts= -k workflow
```

Theo mục `by_shape.workflow` trong [benchmark.json](../../src/reports/benchmark.json) của nhóm, workflow đạt 70/70 trial public (14 claim × 5 seed), pass rate và pass^5 bằng 1, seed variance bằng 0, cost/success khoảng 27,857143 VND mô phỏng. Run id dẫn chứng: `R-workflow-C-001-s11`. Đây là số liệu public đã lưu trong repo, không phải kết quả hidden hoặc số đo mới từ hai test trên.

## 5. Công cụ AI đã dùng

Sử dụng Codex để phân tích flow, giải thích các hàm trong starter, gợi ý code CP2/CP3, hỗ trợ viết hai test và biên tập báo cáo. Cách kiểm chứng gồm đối chiếu chữ ký các hàm, đọc logic xử lý, chạy pytest và kiểm tra các assertion về proposal, ledger và audit.

Số liệu benchmark được lấy từ JSON của nhóm. Phần test do thành viên khác bổ sung không được tính vào hai test riêng nêu trong báo cáo này.

## 6. Tự đánh giá

Đã triển khai workflow và bổ sung hai test về approval cap và approval bị thu hồi. Các quyết định kỹ thuật tập trung vào việc giữ quote đầy đủ, để host kiểm quyền ghi tiền, bảo đảm trace cho các nhánh kết thúc và tích hợp retry/crash đúng contract.

Bài học chính là cần phân biệt số tiền đề xuất với tiền thực ghi, kiểm tra dữ liệu lưu bền thay vì chỉ xem kết quả trả về, và không sử dụng approval thay thế khi claim đang trỏ tới approval không hợp lệ. Hai test mới bổ sung bằng chứng cho phần approval, không thay thế bộ crash hoặc toàn bộ ma trận student.

Kết quả public chưa chứng minh đạt ngưỡng hidden hoặc khả năng vận hành production. MockLLM và giá token là mô phỏng, latency là `unavailable`; không kết luận workflow luôn tốt hơn các kiến trúc agent trên mọi bài toán.
