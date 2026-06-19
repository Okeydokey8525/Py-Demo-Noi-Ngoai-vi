# 🧠 Hướng Dẫn Sử Dụng — Mô Phỏng Phân Mảnh Bộ Nhớ - Cơ Chế Dồn Dịch

> **Python ≥ 3.9 · Tkinter (built-in)**

---

## 1. Cấu Trúc Project

```
project/
├── main.py                  ← Điểm khởi động (tạo cửa sổ Tk + nhúng MainMenu)
├
├── ui/
│   ├── internal_tab.py      ← Tab Phân mảnh nội vi
│   ├── external_tab.py      ← Tab Phân mảnh ngoại vi
│   ├── compaction_tab.py    ← Tab Dồn dịch bộ nhớ
│    └── mainmenu.py              ← Khung chính + Notebook 3 tab
└── core/
    ├── internal_fragmentation.py   ← Thuật toán phân mảnh nội
    ├── external_fragmentation.py   ← Thuật toán First / Best / Worst Fit
    └── compaction.py               ← Thuật toán dồn dịch
```

## 2. Khởi Động Ứng Dụng

```bash
# Di chuyển vào thư mục dự án
cd /đường/dẫn/project

# Chạy app
python main.py
```

Cửa sổ hiện ra gồm **3 tab** nằm trên Notebook:

| Tab | Tên đầy đủ                                  |
|-----|---------------------------------------------|
| 1   | Phân mảnh nội vi (Internal Fragmentation)   |
| 2   | Phân mảnh ngoại vi (External Fragmentation) |
| 3   | Dồn dịch bộ nhớ (Compaction)                |

---

## 3. Tab 1 — Phân Mảnh Nội Vi

### Khái niệm
Bộ nhớ chia thành **8 ô cố định** cùng kích thước. Tiến trình được cấp **nguyên 1 ô** dù không dùng hết → phần dư bị lãng phí bên trong ô gọi là **phân mảnh nội**.

### Cách dùng

**Bước 1 – Chọn kích thước ô nhớ**  
Dropdown *"Kích thước ô (KB)"* — chọn một trong các giá trị: 16 / 32 / 64 / 128 / 256 / 512 KB.  
Thay đổi kích thước ô sẽ **reset toàn bộ** trạng thái mô phỏng.

**Bước 2 – Thêm tiến trình**  
- *Tên tiến trình*: nhập tên tùy ý (mặc định `P1`, `P2`, ...).  
- *Cần (KB)*: nhập số nguyên dương, **không vượt quá kích thước ô** đã chọn.  
- Nhấn **Nạp tiến trình** để cấp phát.

**Bước 3 – Đọc kết quả**

| Thành phần        | Mô tả                                                         |
|-------------------|---------------------------------------------------------------|
| Banner màu indigo | Nhắc kích thước ô hiện tại                                    |
| Bản đồ RAM        | 8 ô; ô màu = đã cấp, phần hồng = phân mảnh nội, ô xám = trống |
| Thẻ thống kê      | Đã dùng (KB) · Phân mảnh nội (KB) · Còn trống (KB)            |
| Bảng log          | Chi tiết từng tiến trình: ô cấp, kích thước yêu cầu, phần mảnh|
| Biểu đồ cột       | Cột màu = kích thước tiến trình · Cột hồng = phân mảnh nội    |

**Bước 4 – Reset**  
Nhấn **Reset** để xóa toàn bộ tiến trình và bắt đầu lại.

### Ví dụ nhanh
```
Kích thước ô : 64 KB
Tiến trình   : P1 = 40 KB → ô #1, phân mảnh nội = 24 KB
               P2 = 60 KB → ô #2, phân mảnh nội =  4 KB
               P3 = 64 KB → ô #3, phân mảnh nội =  0 KB
```

---

## 4. Tab 2 — Phân Mảnh Ngoại Vi

### Khái niệm
Bộ nhớ gồm nhiều khối **kích thước khác nhau**. Tiến trình được cấp vào khối phù hợp theo thuật toán chọn. Phần còn dư trong khối nằm **ngoài** tiến trình → phân mảnh ngoại.

### Cách dùng

**Bước 1 – Nhập danh sách khối nhớ**  
Ô *"Kích thước khối nhớ (KB)"* — nhập các số cách nhau bằng dấu phẩy.  
```
Ví dụ: 100, 500, 200, 300, 600
```

**Bước 2 – Nhập danh sách tiến trình**  
Ô *"Kích thước tiến trình (KB)"* — nhập tương tự.  
```
Ví dụ: 212, 417, 112, 426
```

**Bước 3 – Chọn thuật toán**  
Ba nút radio bên dưới:

| Thuật toán    | Chiến lược               | Màu chủ đạo|
|---------------|--------------------------|------------|
| **First Fit** | Khối **đầu tiên** đủ lớn | Indigo     |
| **Best Fit**  | Khối **nhỏ nhất** vừa đủ | Xanh lá    |
| **Worst Fit** | Khối **lớn nhất** có thể | Cam        |

**Bước 4 – Nhấn ▶ Chạy**  
Banner đổi màu theo thuật toán đang chọn.

**Bước 5 – Đọc kết quả**

| Thành phần   | Mô tả                                                                     |
|--------------|---------------------------------------------------------------------------|
| Bản đồ RAM   | Khối tỉ lệ với kích thước; màu = phần cấp cho tiến trình; xám = còn trống |
| Thẻ thống kê | Tổng bộ nhớ · Đã cấp phát · Còn dư                                        |
| Bảng log     | Tiến trình → khối được cấp → còn dư trong khối                            |
| Biểu đồ cột  | Cột màu = kích thước yêu cầu · Cột vàng = còn dư trong khối               |

**Bước 6 – So sánh thuật toán**  
Thay đổi nút thuật toán → nhấn **▶ Chạy** lại để so sánh kết quả với cùng bộ dữ liệu.

**Reset** — Nhấn **↺ Reset** để xóa và nhập lại.

### Ví dụ nhanh
```
Khối nhớ   : 100, 500, 200, 300, 600
Tiến trình : 212, 417, 112, 426

First Fit  → P1→B2(500), P2→B5(600), P3→B3(200), P4→B4(300)
Best Fit   → P1→B4(300), P2→B5(600), P3→B3(200), P4→B2(500)
Worst Fit  → P1→B5(600), P2→B2(500), P3→B3(200), P4→B4(300)
```

---

## 5. Tab 3 — Dồn Dịch Bộ Nhớ (Compaction)

### Khái niệm
Sau khi cấp phát (First Fit), bộ nhớ tồn tại nhiều **vùng trống rải rác**. Compaction **gom tất cả vùng trống** thành một **khối liên tục** ở cuối, giải quyết phân mảnh ngoại.

### Cách dùng

**Bước 1 – Nhập khối nhớ & tiến trình**  
Tương tự Tab 2, nhập hai danh sách số cách nhau bằng dấu phẩy.

**Bước 2 – Nhấn ▶ Chạy Compaction**  
App tự động:
1. Cấp phát bằng **First Fit**
2. Dồn tất cả vùng trống rải rác thành **1 khối liên tục**

**Bước 3 – Đọc kết quả**

| Thành phần                  | Mô tả                                                                                          |
|-----------------------------|------------------------------------------------------------------------------------------------|
| Bản đồ **TRƯỚC** Compaction | Các khối xen kẽ: màu = đã dùng, xám = còn trống rải rác                                        |
| Bản đồ **SAU** Compaction   | Toàn bộ tiến trình dồn sang trái, vùng trống xanh lớn bên phải                                 |
| Thẻ thống kê                | Tổng bộ nhớ · Đã cấp · Vùng trống trước/sau dồn                                                |
| Bảng log                    | Chi tiết cấp phát trước khi dồn                                                                |
| Biểu đồ cột                 | Cột màu = kích thước P_i · Cột vàng = trống trước dồn · Cột xanh = vùng trống liên tục sau dồn |

**Reset** — Nhấn **↺ Reset toàn bộ** để làm mới.

### Ví dụ nhanh
```
Khối nhớ   : 100, 500, 200, 300, 600
Tiến trình : 212, 417, 112, 426

Trước dồn  : [P1 | 288 free] [P2 | 83 free] [P3 | 88 free] [P4 | 174 free] [600 free]
Sau dồn    : [P4][P3][P1][P2][ ←── 1.233 KB trống liên tục ──→ ]
```

---

## 6. Tính Năng Chung

- **Cuộn chuột** — mỗi tab có thanh cuộn dọc và hỗ trợ `MouseWheel`.
- **Bản đồ RAM** tự vẽ lại khi cửa sổ thay đổi kích thước (bind `<Configure>`).
- **Màu sắc tiến trình** tuần hoàn trong bảng 8 màu pastel, nhất quán giữa bản đồ RAM và biểu đồ.
- **Trạng thái cấp phát thất bại** (tiến trình lớn hơn mọi khối trống) hiển thị `—` trong bảng log và được tính vào số "Chưa cấp phát" trong thẻ thống kê.

---


