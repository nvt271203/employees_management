import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

# Dữ liệu mẫu
nhan_vien = ['Nhân viên A', 'Nhân viên B', 'Nhân viên C', 'Nhân viên D']
ngay_lam_viec = [20, 18, 32, 15]  # Số ngày làm việc
tong_luong = [10000000, 15500000, 19000000, 27000000]  # Tổng lương (VND)
muc_luong_moi_ngay = [300000, 500000, 400000, 600000]  # Mức lương mỗi ngày (VND)

# Thiết lập biểu đồ
fig, ax1 = plt.subplots(figsize=(10, 6))

# Vẽ biểu đồ cột cho số ngày làm việc
ax1.bar(np.arange(len(nhan_vien)) - 0.2, ngay_lam_viec, width=0.4, label='Ngày làm việc', color='b')
ax1.set_xlabel('Nhân viên')
ax1.set_ylabel('Số ngày làm việc', color='b')
ax1.tick_params(axis='y', labelcolor='b')

# Thêm giá trị số ngày làm việc lên cột với định dạng "22d"
for i, ngay in enumerate(ngay_lam_viec):
    ax1.text(i - 0.2, ngay + 0.5, f'{ngay}d', ha='center', va='bottom', color='black', fontsize=10, weight='bold')

# Tạo trục thứ hai cho tổng lương
ax2 = ax1.twinx()
ax2.bar(np.arange(len(nhan_vien)) + 0.2, tong_luong, width=0.4, label='Tổng lương', color='g')
ax2.set_ylabel('Tổng lương (Triệu VND)', color='g')
ax2.tick_params(axis='y', labelcolor='g')

# Định dạng trục y của tổng lương thành đơn vị triệu
ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x/1000000:.0f}'))

# Thiết lập các mốc trục y (10, 20, 30, 40 triệu)
ax2.set_yticks([10000000, 20000000, 30000000, 40000000])

# Thêm văn bản mức lương mỗi ngày và tổng lương vào cột tổng lương
for i, (luong, ngay, tong) in enumerate(zip(muc_luong_moi_ngay, ngay_lam_viec, tong_luong)):
    # Chuyển mức lương mỗi ngày thành đơn vị "k" (nghìn đồng)
    luong_k = luong / 1000
    # Tạo chuỗi văn bản (ví dụ: "300k / 1d")
    text = f'{luong_k:.0f}k / 1d'
    # Đặt văn bản mức lương mỗi ngày vào giữa cột tổng lương
    ax2.text(i + 0.2, tong / 2, text, ha='center', va='center', color='white', fontsize=10, weight='bold')
    # Thêm giá trị tổng lương (triệu VND) lên trên cột
    ax2.text(i + 0.2, tong + 500000, f'{tong/1000000:.0f}M', ha='center', va='bottom', color='black', fontsize=10, weight='bold')

# Thiết lập tiêu đề và các nhãn
plt.title('Số ngày làm việc và tổng lương của nhân viên')
ax1.set_xticks(np.arange(len(nhan_vien)))
ax1.set_xticklabels(nhan_vien)

# Hiển thị chú thích
fig.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2)

# Tự động điều chỉnh bố cục
plt.tight_layout()

# Hiển thị biểu đồ
plt.show()