## 1. Thông tin thành viên

- Họ tên: Nguyễn Đức Minh
- MSSV: 2A202603633
- Email: 26ai.minhnd4@vinuni.edu.vn
- GitHub: https://github.com/MinhDucDepZaiJ

## 2. Phần việc phụ trách
- Triển khai Single ReAct Agent tại src/lab8/shapes/single.py.
- Xây dựng luồng tra cứu thông tin, tính bồi hoàn và xử lý kết quả.
- Kiểm thử tính đúng đắn, crash safety và benchmark Single Agent.

## 3. Đóng góp cụ thể
- Tích hợp ReAct runtime và các công cụ tra cứu nghiệp vụ.
- Tách quyền quyết định của Agent khỏi thao tác hoàn tiền do Host thực hiện.
- Xử lý các trạng thái resolved, denied, needs_info, escalated.
- Kiểm tra cơ chế idempotency và phục hồi sau crash.
- Commit: 5016a693e409866fc796e3c5cbedd455cc05bb2e

## 4. Bằng chứng
- Student tests: 62/62 PASS.
- Host crash safety: 20/20 PASS.
- Single Agent benchmark: 70/70 PASS.
- Pass rate: 100%; Pass^5: 1.0.
- Seed variance: 0.0.
- Cost/success: 46,40 VND (mô phỏng).
- Run ID: R-single-C-001-s11, R-single-C-012-s11.

## 5. Công cụ AI đã dùng
MockLLM: Mô phỏng quá trình lựa chọn công cụ của Agent.

## 6. Tự đánh giá

- Hoàn thành phần Single Agent được phụ trách.

- Đảm bảo các public tests và benchmark đều đạt yêu cầu.

- Hiểu rõ cơ chế ReAct, tool calling, idempotency và crash recovery.

- Hạn chế: Chưa đánh giá với LLM thật và hidden tests.

- Bài học: Cần tách biệt Agent và Host để đảm bảo an toàn khi thực hiện giao dịch.
