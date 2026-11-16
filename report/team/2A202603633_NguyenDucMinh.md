## 1. Thông tin thành viên

- Họ tên: Nguyễn Đức Minh
- MSSV: 2A202603633
- Email: 26ai.minhnd4@vinuni.edu.vn
- GitHub: https://github.com/MinhDucDepZaiJ
- Nhóm: MID — Lớp L3A

## 2. Phần việc phụ trách
Trong Lab Day 8, mình phụ trách nghiên cứu, kiểm tra và hoàn thiện phần Single ReAct Agent, được triển khai tại src/lab8/shapes/single.py. Single ReAct Agent là mô hình agent sử dụng một tác nhân duy nhất để thực hiện chu trình Reasoning – Acting – Observation. Agent tiếp nhận yêu cầu hoàn tiền, phân tích thông tin, lựa chọn công cụ phù hợp, quan sát kết quả và tiếp tục xử lý cho đến khi đưa ra quyết định cuối cùng.
Các nhiệm vụ chính của mình gồm:
- Tìm hiểu luồng xử lý yêu cầu hoàn tiền và cách agent phối hợp với các công cụ.
- Kiểm tra những tình huống thiếu thông tin, không đủ điều kiện hoàn tiền và xử lý lại yêu cầu.
- Xây dựng các test nhằm xác minh tính đúng đắn và hạn chế tác dụng phụ khi thực thi.
- Đánh giá kết quả của Single Agent thông qua pytest, benchmark và crash test.

## 3. Đóng góp cụ thể

### 3.1. Phân tích và kiểm tra Single Agent

Mình tìm hiểu hàm `run_claim()`, cách tiếp nhận `claim_id`, đọc dữ liệu từ SQLite và xử lý yêu cầu hoàn tiền. Ba khía cạnh được chú trọng:

1. **Thiếu thông tin:** Khi thiếu mã đơn hàng, agent phải trả về `needs_info`, không tự suy đoán dữ liệu.
2. **Từ chối hoàn tiền:** Với yêu cầu không đủ điều kiện, agent cần trả về `denied` và số tiền đề xuất bằng 0.
3. **Idempotency:** Khi xử lý lại cùng một yêu cầu, hệ thống cần tránh phát sinh tác dụng phụ hoàn tiền trùng lặp.

### 3.2. Bổ sung kiểm thử

File kiểm thử: `src/tests/test_single_contribution.py`.

| Test | Mục đích | Trạng thái xác nhận gần nhất |
|---|---|---|
| `test_single_missing_order_id` | Kiểm tra thiếu mã đơn hàng | PASS |
| `test_single_refund_idempotency` | Kiểm tra xử lý lặp lại cùng claim | PASS |
| `test_single_zero_refund` | Kiểm tra trường hợp từ chối hoàn tiền | Đã từng PASS; cần xác nhận có trong phiên bản cuối |

Trong quá trình xây dựng test, mình gặp lỗi `sqlite3.OperationalError: no such table: claims` vì cơ sở dữ liệu tạm chưa được khởi tạo. Sau khi kiểm tra `tests/conftest.py`, mình sử dụng fixture `public_db` để tạo SQLite database và nạp dữ liệu mẫu trước khi chạy agent. Mình cũng điều chỉnh các assertion và bỏ truy vấn tới bảng `refund_effects` không tồn tại trong schema.

**Kết quả pytest xác nhận gần nhất:** `2 passed` với hai test `test_single_missing_order_id` và `test_single_refund_idempotency`. Nếu bổ sung lại test thứ ba, cần chạy lại trước khi cập nhật báo cáo.

### 3.3. Đánh giá hoạt động

Các kết quả đã ghi nhận từ những lần chạy trước:

| Chỉ số | Kết quả |
|---|---|
| Single Agent benchmark | 70/70 trường hợp PASS |
| Pass rate | 100% |
| Pass^5 | 100% |
| Số bước trung bình | 7 |
| Model calls trung bình | 3,5 |
| Tool calls trung bình | 4,5 |
| Crash test tổng thể | 20/20 PASS |

Benchmark dùng **MockLLM** và dữ liệu mô phỏng; các chỉ số này chưa phản ánh chất lượng khi dùng mô hình thực tế. Crash test đánh giá độ bền của hệ thống tổng thể, không chỉ riêng Single Agent.

## 4. Bằng chứng đóng góp

- **Mã nguồn nghiên cứu:** `src/lab8/shapes/single.py`
- **Test bổ sung:** `src/tests/test_single_contribution.py`
- **Fixture dữ liệu:** `src/tests/conftest.py`
- **Benchmark:** `reports/benchmark_single.json`
- **Crash test:** `reports/crash.json`
- **Commit GitHub:** 5016a693e409866fc796e3c5cbedd455cc05bb2e

Lệnh chạy kiểm thử cá nhân (từ thư mục `src`):

```powershell
python -m pytest -q -o addopts= tests/test_single_contribution.py
```

Lệnh benchmark (từ thư mục `src`):

```powershell
python -m lab8.benchmark --shapes single --out reports/benchmark_single.json
```

## 5. Công cụ AI đã sử dụng

Mình sử dụng **ChatGPT** để hỗ trợ:

- Giải thích kiến trúc Single ReAct Agent và luồng xử lý `run_claim()`.
- Phân tích traceback và xác định nguyên nhân lỗi pytest.

Các gợi ý của AI được đối chiếu với mã nguồn, fixture và kết quả pytest. Những đoạn code không tương thích đã được chỉnh sửa theo kết quả chạy thực tế.

## 6. Tự đánh giá

- Hoàn thành phần Single Agent được phụ trách.

- Đảm bảo các public tests và benchmark đều đạt yêu cầu.

- Hiểu rõ cơ chế ReAct, tool calling, idempotency và crash recovery.

- Hạn chế: Chưa đánh giá với LLM thật và hidden tests.

- Bài học: Cần tách biệt Agent và Host để đảm bảo an toàn khi thực hiện giao dịch.
