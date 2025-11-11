from tkinter import Tk, Button, Label, Scrollbar, StringVar, Entry, W, E, N, S, END
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
from sqlserver_config import dbConfig
import pypyodbc as pyo
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker


class EmployeeManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Management System")
        self.root.state('zoomed')
        self.root.configure(bg="#f0f2f5")

        try:
            self.con = pyo.connect(**dbConfig)
            self.con.autocommit = False  # Tắt autocommit
            self.cursor = self.con.cursor()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {str(e)}")
            self.root.destroy()
            return

        self.employee_id_var = StringVar()
        self.full_name_var = StringVar()
        self.date_of_birth_var = StringVar()
        self.gender_var = StringVar(value="Male")
        self.address_var = StringVar()
        self.phone_number_var = StringVar()
        self.position_var = StringVar(value="Nhân viên")
        self.working_days_var = StringVar()
        self.daily_salary_var = StringVar()
        self.search_var = StringVar()  # Biến cho tìm kiếm

        self.create_gui()

    def format_currency(self, amount):
        """Định dạng số tiền thành chuỗi với dấu chấm phân cách và VND"""
        try:
            formatted = "{:,.0f}".format(int(amount)).replace(",", ".")
            return f"{formatted} VND"
        except (ValueError, TypeError):
            return "0 VND"

    def parse_currency(self, formatted_amount):
        """Chuyển chuỗi tiền tệ (3.000.000 VND) thành số nguyên"""
        try:
            cleaned = formatted_amount.replace("VND", "").replace(".", "").strip()
            return int(cleaned)
        except (ValueError, TypeError):
            return 0

    def create_gui(self):
        # Style
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12), background="#e0f7fa")
        style.configure("TEntry", font=("Helvetica", 12), padding=5)
        style.configure("TButton", font=("Helvetica", 12, "bold"), padding=10)
        style.configure("Treeview", font=("Helvetica", 11), background="#e0f7fa", fieldbackground="#e0f7fa")
        style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"), background="#b2ebf2")
        style.configure("Rounded.TFrame", background="#e0f7fa", bordercolor="#dcdcdc", relief="solid")
        style.configure("Custom.Treeview", font=("Helvetica", 11), rowheight=30)
        style.map("Treeview", background=[("selected", "#80deea")])

        # Khung chính
        main_frame = ttk.Frame(self.root, padding=10, style="TFrame")
        main_frame.grid(row=0, column=0, sticky=(N, S, E, W))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=3)  # Cột 2 rộng hơn
        main_frame.columnconfigure(0, weight=1)  # Cột 1 hẹp hơn

        # Hàng 1: Cột 1 (Form nhập liệu)
        input_frame = ttk.Frame(main_frame, padding=10, relief="flat", style="Rounded.TFrame")
        input_frame.grid(row=0, column=0, sticky=(N, S), padx=10, pady=10)
        input_frame.configure(borderwidth=2, relief="solid")
        canvas = ttk.Frame(input_frame, style="Rounded.TFrame")
        canvas.grid(row=0, column=0, sticky=(N, S, E, W))
        canvas.configure(borderwidth=10, relief="solid")

        # Tiêu đề
        ttk.Label(canvas, text="Employee Information", font=("Helvetica", 16, "bold"), background="#e0f7fa").grid(row=0,
                                                                                                                  column=0,
                                                                                                                  columnspan=2,
                                                                                                                  pady=15)

        # Các trường nhập liệu
        fields = [
            ("Full Name", self.full_name_var, False, "entry"),
            ("Date of Birth", self.date_of_birth_var, False, "calendar"),
            ("Gender", self.gender_var, False, "combobox", ["Male", "Female"]),
            ("Address", self.address_var, False, "entry"),
            ("Phone Number", self.phone_number_var, False, "entry"),
            ("Position", self.position_var, False, "combobox",
             ["Giám đốc", "Phó giám đốc", "Trưởng phòng", "Nhân viên", "Thực tập sinh"]),
            ("Working Days", self.working_days_var, False, "entry"),
            ("Daily Salary", self.daily_salary_var, False, "entry")
        ]

        for i, (label, var, readonly, field_type, *options) in enumerate(fields, 1):
            ttk.Label(canvas, text=label).grid(row=i, column=0, sticky=W, padx=10, pady=10)
            if field_type == "combobox":
                combo = ttk.Combobox(canvas, textvariable=var, values=options[0], state="readonly", width=20)
                combo.grid(row=i, column=1, sticky=(W, E), padx=10, pady=10)
            elif field_type == "calendar":
                current_year = datetime.now().year
                calendar = DateEntry(
                    canvas,
                    textvariable=var,
                    width=20,
                    date_pattern="dd-mm-yyyy",
                    font=("Helvetica", 12),
                    yearrange=(1900, current_year + 10),
                    mindate=datetime(1900, 1, 1),
                    maxdate=datetime(current_year + 10, 12, 31)
                )
                calendar.grid(row=i, column=1, sticky=(W, E), padx=10, pady=10)
            else:
                entry = ttk.Entry(canvas, textvariable=var, width=22)
                entry.grid(row=i, column=1, sticky=(W, E), padx=10, pady=10)
                if readonly:
                    entry.configure(state="readonly")

        # Hàng 1: Cột 2 (Danh sách nhân viên)
        list_frame = ttk.Frame(main_frame, padding=10, relief="solid", style="TFrame")
        list_frame.grid(row=0, column=1, sticky=(N, S, E, W), padx=10, pady=10)
        list_frame.configure(borderwidth=2, relief="solid")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Bảng hiển thị
        columns = ("ID", "Name", "DOB", "Gender", "Address", "Phone", "Position", "Days", "Salary", "Total")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20, style="Custom.Treeview")
        self.tree.grid(row=0, column=0, sticky=(N, S, E, W))
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(N, S))
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Tiêu đề cột
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Full Name")
        self.tree.heading("DOB", text="Date of Birth")
        self.tree.heading("Gender", text="Gender")
        self.tree.heading("Address", text="Address")
        self.tree.heading("Phone", text="Phone Number")
        self.tree.heading("Position", text="Position")
        self.tree.heading("Days", text="Working Days")
        self.tree.heading("Salary", text="Daily Salary")
        self.tree.heading("Total", text="Total Salary")

        # Độ rộng cột và viền
        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Name", width=150, anchor="w")
        self.tree.column("DOB", width=100, anchor="center")
        self.tree.column("Gender", width=80, anchor="center")
        self.tree.column("Address", width=100, anchor="w")
        self.tree.column("Phone", width=100, anchor="center")
        self.tree.column("Position", width=100, anchor="w")
        self.tree.column("Days", width=80, anchor="center")
        self.tree.column("Salary", width=120, anchor="center")  # Tăng độ rộng cho cột Salary
        self.tree.column("Total", width=120, anchor="center")   # Tăng độ rộng cho cột Total

        # Thêm viền phân cách
        style.configure("Treeview", highlightthickness=1, bd=1)
        style.configure("Treeview.Heading", relief="flat", borderwidth=1)
        self.tree.tag_configure("cell", background="#e0f7fa")

        # Hàng 2: Nút chức năng và tìm kiếm
        button_frame = ttk.Frame(main_frame, padding=10, style="Rounded.TFrame")
        button_frame.grid(row=1, column=0, columnspan=2, pady=15)
        button_frame.configure(borderwidth=2, relief="solid")

        # Trường tìm kiếm
        ttk.Label(button_frame, text="Search Name:", font=("Helvetica", 12, "bold"), background="#f0f2f5").grid(row=0,
                                                                                                                column=0,
                                                                                                                padx=(10, 5),
                                                                                                                pady=5,
                                                                                                                sticky=E)
        search_entry = ttk.Entry(button_frame, textvariable=self.search_var, width=20, font=("Helvetica", 12))
        search_entry.grid(row=0, column=1, padx=(0, 5), pady=5, sticky=W)

        # Nút Reset
        reset_btn = Button(
            button_frame,
            text="Reset",
            command=self.reset_search,
            bg="#6c757d",
            fg="white",
            font=("Helvetica", 12, "bold"),
            relief="flat",
            bd=0,
            padx=20,
            pady=10,
            highlightthickness=0,
            borderwidth=0
        )
        reset_btn.grid(row=0, column=2, padx=5, pady=5)
        reset_btn.configure(activebackground="#6c757d", activeforeground="white")
        reset_btn.configure(highlightbackground="#ffffff", highlightcolor="#ffffff", borderwidth=2, relief="solid")
        reset_btn.bind("<Enter>", lambda e, b=reset_btn: b.configure(bg="#e0e0e0"))
        reset_btn.bind("<Leave>", lambda e, b=reset_btn: b.configure(bg="#6c757d"))

        # Danh sách nút
        buttons = [
            ("Search", self.search_employee, "#17a2b8"),  # Nút tìm kiếm
            ("Add", self.add_employee, "#28a745"),
            ("Update", self.update_employee, "#007bff"),
            ("Delete", self.delete_employee, "#dc3545"),
            ("Clear", self.clear_fields, "#6c757d"),
            ("Chart", self.show_chart, "#ff9800"),  # Nút Chart mới
            ("Exit", self.exit_app, "#343a40")
        ]

        for i, (text, command, bg) in enumerate(buttons):
            btn = Button(
                button_frame,
                text=text,
                command=command,
                bg=bg,
                fg="white",
                font=("Helvetica", 12, "bold"),
                relief="flat",
                bd=0,
                padx=20,
                pady=10,
                highlightthickness=0,
                borderwidth=0
            )
            btn.grid(row=0, column=i + 3, padx=15, pady=5)  # Dịch cột do có reset
            btn.configure(activebackground=bg, activeforeground="white")
            btn.configure(highlightbackground="#ffffff", highlightcolor="#ffffff", borderwidth=2, relief="solid")
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#e0e0e0"))
            btn.bind("<Leave>", lambda e, b=btn, c=bg: b.configure(bg=c))

        # Load dữ liệu
        self.load_employees()

        # Sự kiện chọn dòng
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def show_chart(self):
        try:
            # Lấy dữ liệu từ cơ sở dữ liệu
            self.cursor.execute(
                "SELECT FullName, WorkingDays, DailySalary FROM Employee WHERE WorkingDays > 0 AND DailySalary > 0")
            data = self.cursor.fetchall()

            if not data:
                messagebox.showinfo("No Data", "No valid employee data found for the chart!")
                return

            # Chuẩn bị dữ liệu cho biểu đồ
            nhan_vien = [row[0] for row in data]
            ngay_lam_viec = [row[1] for row in data]
            muc_luong_moi_ngay = [row[2] for row in data]
            tong_luong = [row[1] * row[2] for row in data]  # Tính tổng lương

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
            max_salary = max(tong_luong) if tong_luong else 10000000
            ax2.set_yticks(np.arange(10000000, max_salary + 10000000, 10000000))

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
            ax1.set_xticklabels(nhan_vien, rotation=45, ha='right')

            # Hiển thị chú thích
            fig.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2)

            # Tự động điều chỉnh bố cục
            plt.tight_layout()

            # Hiển thị biểu đồ
            plt.show()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate chart: {str(e)}")

    def validate_integer(self, value):
        """Kiểm tra giá trị có phải số nguyên hợp lệ không"""
        if not value:
            return True
        try:
            int(value)
            return True
        except ValueError:
            return False

    def load_employees(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.cursor.execute(
            "SELECT EmployeeID, FullName, CONVERT(VARCHAR, DateOfBirth, 105) AS DateOfBirth, Gender, Address, PhoneNumber, Position, WorkingDays, DailySalary FROM Employee")
        for row in self.cursor.fetchall():
            total_salary = row[7] * row[8]
            formatted_daily_salary = self.format_currency(row[8])
            formatted_total_salary = self.format_currency(total_salary)
            self.tree.insert("", END, values=(
                row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                formatted_daily_salary, formatted_total_salary
            ), tags=("cell",))

    def search_employee(self):
        search_term = self.search_var.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = """
            SELECT EmployeeID, FullName, CONVERT(VARCHAR, DateOfBirth, 105) AS DateOfBirth, Gender, Address, PhoneNumber, Position, WorkingDays, DailySalary
            FROM Employee
            WHERE LOWER(FullName) LIKE LOWER(?)
        """
        search_param = f'%{search_term}%'
        self.cursor.execute(query, (search_param,))

        for row in self.cursor.fetchall():
            total_salary = row[7] * row[8]
            formatted_daily_salary = self.format_currency(row[8])
            formatted_total_salary = self.format_currency(total_salary)
            self.tree.insert("", END, values=(
                row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                formatted_daily_salary, formatted_total_salary
            ), tags=("cell",))

        if not self.tree.get_children():
            messagebox.showinfo("Search Result", "No employees found matching the search term.")

    def reset_search(self):
        self.search_var.set("")  # Xóa trường tìm kiếm
        self.load_employees()    # Tải lại toàn bộ dữ liệu

    def add_employee(self):
        try:
            if not self.full_name_var.get():
                messagebox.showwarning("Warning", "Full Name is required!")
                return
            if not self.date_of_birth_var.get():
                messagebox.showwarning("Warning", "Date of Birth is required!")
                return

            try:
                datetime.strptime(self.date_of_birth_var.get(), "%d-%m-%Y")
            except ValueError:
                messagebox.showwarning("Warning", "Invalid Date of Birth format! Use DD-MM-YYYY")
                return

            if self.working_days_var.get() and not self.validate_integer(self.working_days_var.get()):
                messagebox.showwarning("Warning", "Working Days must be an integer!")
                return
            if self.daily_salary_var.get() and not self.validate_integer(self.daily_salary_var.get()):
                messagebox.showwarning("Warning", "Daily Salary must be an integer!")
                return

            self.cursor.execute("""
                INSERT INTO Employee (FullName, DateOfBirth, Gender, Address, PhoneNumber, Position, WorkingDays, DailySalary)
                OUTPUT INSERTED.EmployeeID
                VALUES (?, CONVERT(DATE, ?, 105), ?, ?, ?, ?, ?, ?)
            """, (
                self.full_name_var.get(),
                self.date_of_birth_var.get(),
                self.gender_var.get(),
                self.address_var.get(),
                self.phone_number_var.get(),
                self.position_var.get(),
                self.working_days_var.get() or "0",
                self.daily_salary_var.get() or "0"
            ))
            employee_id = self.cursor.fetchone()[0]
            self.con.commit()
            self.load_employees()
            self.clear_fields()
            messagebox.showinfo("Success", "Employee added successfully!")
        except Exception as e:
            self.con.rollback()
            messagebox.showerror("Error", f"Failed to add employee: {str(e)}")

    def update_employee(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an employee to update!")
            return
        try:
            if not self.full_name_var.get():
                messagebox.showwarning("Warning", "Full Name is required!")
                return
            if not self.date_of_birth_var.get():
                messagebox.showwarning("Warning", "Date of Birth is required!")
                return

            try:
                datetime.strptime(self.date_of_birth_var.get(), "%d-%m-%Y")
            except ValueError:
                messagebox.showwarning("Warning", "Invalid Date of Birth format! Use DD-MM-YYYY")
                return

            if self.working_days_var.get() and not self.validate_integer(self.working_days_var.get()):
                messagebox.showwarning("Warning", "Working Days must be an integer!")
                return
            if self.daily_salary_var.get() and not self.validate_integer(self.daily_salary_var.get()):
                messagebox.showwarning("Warning", "Daily Salary must be an integer!")
                return

            employee_id = self.tree.item(selected[0])["values"][0]
            self.cursor.execute("""
                UPDATE Employee
                SET FullName = ?, DateOfBirth = CONVERT(DATE, ?, 105), Gender = ?, Address = ?, PhoneNumber = ?, Position = ?, WorkingDays = ?, DailySalary = ?
                WHERE EmployeeID = ?
            """, (
                self.full_name_var.get(),
                self.date_of_birth_var.get(),
                self.gender_var.get(),
                self.address_var.get(),
                self.phone_number_var.get(),
                self.position_var.get(),
                self.working_days_var.get() or "0",
                self.daily_salary_var.get() or "0",
                employee_id
            ))
            self.con.commit()
            self.load_employees()
            self.clear_fields()
            messagebox.showinfo("Success", "Employee updated successfully!")
        except Exception as e:
            self.con.rollback()
            messagebox.showerror("Error", f"Failed to update employee: {str(e)}")

    def delete_employee(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an employee to delete!")
            return
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this employee?"):
            try:
                employee_id = self.tree.item(selected[0])["values"][0]
                self.cursor.execute("DELETE FROM Employee WHERE EmployeeID = ?", (employee_id,))
                self.con.commit()
                self.load_employees()
                self.clear_fields()
                messagebox.showinfo("Success", "Employee deleted successfully!")
            except Exception as e:
                self.con.rollback()
                messagebox.showerror("Error", f"Failed to delete employee: {str(e)}")

    def clear_fields(self):
        self.employee_id_var.set("")
        self.full_name_var.set("")
        self.date_of_birth_var.set("")
        self.gender_var.set("Male")
        self.address_var.set("")
        self.phone_number_var.set("")
        self.position_var.set("Nhân viên")
        self.working_days_var.set("")
        self.daily_salary_var.set("")
        self.search_var.set("")  # Xóa trường tìm kiếm

    def exit_app(self):
        self.con.close()
        self.root.destroy()

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])["values"]
            self.employee_id_var.set(values[0])
            self.full_name_var.set(values[1])
            self.date_of_birth_var.set(values[2])
            self.gender_var.set(values[3])
            self.address_var.set(values[4])
            self.phone_number_var.set(values[5])
            self.position_var.set(values[6])
            self.working_days_var.set(str(values[7]))
            self.daily_salary_var.set(str(self.parse_currency(values[8])))


if __name__ == "__main__":
    root = Tk()
    app = EmployeeManagementApp(root)
    root.mainloop()