# Team

## Thông tin nhóm

- Tên nhóm: MID
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-MID-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/Monstucture/K5-L3A-DAY08-MID-FromWorkflowsToAgents

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 |       Quách Ngọc Phúc |      2A202603665|       quachphucbk@gmail.com|        https://github.com/quachphucbk|         |
|   2 | Ngô Văn Tuân | 2A202603630 | 26ai.tuannv3@vinuni.edu.vn | https://github.com/Monstucture/K5-L3A-DAY08-MID-FromWorkflowsToAgents |  |
|   3 |    Trần Thanh Long    |   2A202603674   |    26ai.longtt2@vinuni.edu.vn   |    https://github.com/Monstucture/K5-L3A-DAY08-MID-FromWorkflowsToAgents    |         |
|   4 |    Nguyễn Đức Minh    |   2A202603633   |    26ai.minhnd4@vinuni.edu.vn   |    https://github.com/MinhDucDepZaiJ    |         |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
<<<<<<< Updated upstream
| Quách Ngọc Phúc | | | Chưa có test riêng trong lịch sử đã kiểm tra; thành viên cần bổ sung |
| Ngô Văn Tuân | Ledger/crash, evaluation và tổng hợp báo cáo | `de10b6a`, `b3f45ba` | `src/tests/test_refund_crash_recovery.py` (9 trường hợp); `src/tests/test_swarm_peer_ablation.py` (5 trường hợp) |
=======
| Quách Ngọc Phúc | | | `src/tests/test_workflow_approval_cap.py`; `src/tests/test_workflow_revoked_approval.py` (2 test case: approval cap/retry và approval thu hồi/audit) |
| Ngô Văn Tuân | | | `src/tests/test_refund_crash_recovery.py` (9 trường hợp); `src/tests/test_swarm_peer_ablation.py` (5 trường hợp) |
>>>>>>> Stashed changes
| Trần Thanh Long | Orchestrator + handoff; crash test, benchmark | `f7e31af`, `06fa360`, `a36161d` | `src/tests/test_orchestrator_handoff.py` (2 test: handoff chỉ tool đọc + trace không lộ secret/ticket/PII; C-002 denied ở seed 55) |
| Nguyễn Đức Minh | | | Chưa có test riêng trong lịch sử đã kiểm tra; thành viên cần bổ sung |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-
