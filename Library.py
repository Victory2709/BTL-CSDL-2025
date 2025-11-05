import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import webbrowser
import os

class LibraryManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ Thống Quản Lý Thư Viện - Library Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f8ff')
        
        # Initialize database
        self.init_database()
        
        # Create main interface
        self.create_main_interface()
        
    def init_database(self):
        """Initialize SQLite database with the schema from the document"""
        self.conn = sqlite3.connect('library.db')
        self.cursor = self.conn.cursor()
        
        # Create tables
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Sach (
                MaSach TEXT PRIMARY KEY,
                TenSach TEXT NOT NULL,
                TacGia TEXT NOT NULL,
                NamXB TEXT,
                NhaXB TEXT,
                TheLoai TEXT NOT NULL,
                SoLuong INTEGER NOT NULL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS SinhVien (
                MaSV TEXT PRIMARY KEY,
                TenSV TEXT NOT NULL,
                NamSinh TEXT NOT NULL,
                SDT TEXT,
                MaLop TEXT NOT NULL,
                Tuoi INTEGER
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Phieu (
                MaPhieu TEXT PRIMARY KEY,
                MaSV TEXT NOT NULL,
                MaSach TEXT NOT NULL,
                SoLuongMuon INTEGER NOT NULL,
                NgayMuon TEXT NOT NULL,
                NgayTra TEXT NOT NULL,
                FOREIGN KEY (MaSV) REFERENCES SinhVien(MaSV),
                FOREIGN KEY (MaSach) REFERENCES Sach(MaSach)
            )
        ''')
    
    def create_main_interface(self):
        """Create the main interface with navigation and content areas"""
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="HỆ THỐNG QUẢN LÝ THƯ VIỆN - LIBRARY MANAGEMENT SYSTEM", 
            font=('Arial', 16, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(pady=20)
        
        # Navigation frame
        nav_frame = tk.Frame(self.root, bg='#34495e', width=200)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        nav_frame.pack_propagate(False)
        
        # Content frame
        self.content_frame = tk.Frame(self.root, bg='#ecf0f1')
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Navigation buttons
        nav_buttons = [
            ("Quản lý sách", self.show_book_management),
            ("Quản lý sinh viên", self.show_student_management),
            ("Quản lý mượn/trả sách", self.show_borrow_return),
            ("Tìm kiếm sách", self.show_search_books),
            ("Tìm kiếm sinh viên", self.show_search_students),
            ("Thống kê báo cáo", self.show_reports),
            ("Thoát", self.exit_app)
        ]
        
        for text, command in nav_buttons:
            btn = tk.Button(
                nav_frame, 
                text=text, 
                command=command,
                font=('Arial', 12),
                bg='#3498db',
                fg='white',
                width=18,
                pady=10,
                relief=tk.FLAT
            )
            btn.pack(pady=5, padx=10)
        
        # Show default content
        self.show_book_management()
    
    def clear_content_frame(self):
        """Clear the content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_book_management(self):
        """Display book management interface"""
        self.clear_content_frame()
        
        title_label = tk.Label(
            self.content_frame, 
            text="QUẢN LÝ SÁCH", 
            font=('Arial', 16, 'bold'),
            bg='#ecf0f1'
        )
        title_label.pack(pady=10)
        
        # Book management frame
        book_frame = tk.Frame(self.content_frame, bg='#ecf0f1')
        book_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Input fields
        input_frame = tk.Frame(book_frame, bg='#ecf0f1')
        input_frame.pack(fill=tk.X, pady=10)
        
        fields = [
            ("Mã sách:", "MaSach"),
            ("Tên sách:", "TenSach"),
            ("Tác giả:", "TacGia"),
            ("Năm xuất bản:", "NamXB"),
            ("Nhà xuất bản:", "NhaXB"),
            ("Thể loại:", "TheLoai"),
            ("Số lượng:", "SoLuong")
        ]
        
        self.book_entries = {}
        for i, (label_text, field_name) in enumerate(fields):
            tk.Label(input_frame, text=label_text, bg='#ecf0f1').grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = tk.Entry(input_frame, width=30)
            entry.grid(row=i, column=1, pady=5, padx=10)
            self.book_entries[field_name] = entry
        
        # Buttons
        button_frame = tk.Frame(book_frame, bg='#ecf0f1')
        button_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            button_frame, 
            text="Thêm sách", 
            command=self.add_book,
            bg='#2ecc71',
            fg='white',
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame, 
            text="Cập nhật", 
            command=self.update_book,
            bg='#f39c12',
            fg='white',
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame, 
            text="Xóa sách", 
            command=self.delete_book,
            bg='#e74c3c',
            fg='white',
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame, 
            text="Làm mới", 
            command=self.refresh_book_list,
            bg='#3498db',
            fg='white',
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # Book list
        list_frame = tk.Frame(book_frame, bg='#ecf0f1')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        columns = ("MaSach", "TenSach", "TacGia", "NamXB", "NhaXB", "TheLoai", "SoLuong")
        self.book_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.book_tree.heading(col, text=col)
            self.book_tree.column(col, width=120)
        
        self.book_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind selection
        self.book_tree.bind('<<TreeviewSelect>>', self.on_book_select)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.book_tree.yview)
        self.book_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load book data
        self.refresh_book_list()
    
    def add_book(self):
        """Add a new book to the database"""
        try:
            # Get values from entries
            values = []
            for field in ["MaSach", "TenSach", "TacGia", "NamXB", "NhaXB", "TheLoai", "SoLuong"]:
                value = self.book_entries[field].get()
                if field == "SoLuong":
                    value = int(value) if value else 0
                values.append(value)
            
            # Check required fields
            if not values[0] or not values[1] or not values[2] or not values[5]:
                messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin bắt buộc!")
                return
            
            # Insert into database
            self.cursor.execute(
                "INSERT INTO Sach VALUES (?, ?, ?, ?, ?, ?, ?)",
                values
            )
            self.conn.commit()
            
            messagebox.showinfo("Thành công", "Thêm sách thành công!")
            self.refresh_book_list()
            self.clear_book_entries()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Mã sách đã tồn tại!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
    
    def update_book(self):
        """Update book information"""
        selected = self.book_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sách để cập nhật!")
            return
        
        try:
            # Get values from entries
            values = []
            for field in ["TenSach", "TacGia", "NamXB", "NhaXB", "TheLoai", "SoLuong"]:
                value = self.book_entries[field].get()
                if field == "SoLuong":
                    value = int(value) if value else 0
                values.append(value)
            
            book_id = self.book_entries["MaSach"].get()
            
            # Update database
            self.cursor.execute(
                "UPDATE Sach SET TenSach=?, TacGia=?, NamXB=?, NhaXB=?, TheLoai=?, SoLuong=? WHERE MaSach=?",
                values + [book_id]
            )
            self.conn.commit()
            
            messagebox.showinfo("Thành công", "Cập nhật sách thành công!")
            self.refresh_book_list()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
    
    def delete_book(self):
        """Delete a book from the database"""
        selected = self.book_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sách để xóa!")
            return
        
        book_id = self.book_tree.item(selected[0])['values'][0]
        
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa sách {book_id}?"):
            try:
                self.cursor.execute("DELETE FROM Sach WHERE MaSach=?", (book_id,))
                self.conn.commit()
                
                messagebox.showinfo("Thành công", "Xóa sách thành công!")
                self.refresh_book_list()
                self.clear_book_entries()
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
    
    def on_book_select(self, event):
        """Handle book selection in the treeview"""
        selected = self.book_tree.selection()
        if selected:
            values = self.book_tree.item(selected[0])['values']
            fields = ["MaSach", "TenSach", "TacGia", "NamXB", "NhaXB", "TheLoai", "SoLuong"]
            
            for i, field in enumerate(fields):
                self.book_entries[field].delete(0, tk.END)
                self.book_entries[field].insert(0, str(values[i]) if values[i] is not None else "")
    
    def refresh_book_list(self):
        """Refresh the book list in the treeview"""
        # Clear existing data
        for item in self.book_tree.get_children():
            self.book_tree.delete(item)
        
        # Fetch data from database
        self.cursor.execute("SELECT * FROM Sach")
        books = self.cursor.fetchall()
        
        # Insert data into treeview
        for book in books:
            self.book_tree.insert('', tk.END, values=book)
    
    def clear_book_entries(self):
        """Clear all book entry fields"""
        for entry in self.book_entries.values():
            entry.delete(0, tk.END)
    
    def show_student_management(self):
        """Display student management interface"""
        self.clear_content_frame()
        
        title_label = tk.Label(
            self.content_frame, 
            text="QUẢN LÝ SINH VIÊN", 
            font=('Arial', 16, 'bold'),
            bg='#ecf0f1'
        )
        title_label.pack(pady=10)
        
        # Student management frame
        student_frame = tk.Frame(self.content_frame, bg='#ecf0f1')
        student_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Input fields
        input_frame = tk.Frame(student_frame, bg='#ecf0f1')
        input_frame.pack(fill=tk.X, pady=10)
        
        fields = [
            ("Mã sinh viên:", "MaSV"),
            ("Tên sinh viên:", "TenSV"),
            ("Ngày sinh:", "NamSinh"),
            ("Số điện thoại:", "SDT"),
            ("Mã lớp:", "MaLop"),
            ("Tuổi:", "Tuoi")
        ]
        
        self.student_entries = {}
        for i, (label_text, field_name) in enumerate(fields):
            tk.Label(input_frame, text=label_text, bg='#ecf0f1').grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = tk.Entry(input_frame, width=30)
            entry.grid(row=i, column=1, pady=5, padx=10)
            self.student_entries[field_name] = entry
        
        # Buttons
        button_frame = tk.Frame(student_frame, bg='#ecf0f1')
        button_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            button_frame, 
            text="Thêm sinh viên", 
            command=self.add_student,
            bg='#2ecc71',
            fg='white',
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame, 
            text="Cập nhật", 
            command=self.update_student,
            bg='#f39c12',
            fg='white',
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame, 
            text="Xóa sinh viên", 
            command=self.delete_student,
            bg='#e74c3c',
            fg='white',
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame, 
            text="Làm mới", 
            command=self.refresh_student_list,
            bg='#3498db',
            fg='white',
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # Student list
        list_frame = tk.Frame(student_frame, bg='#ecf0f1')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        columns = ("MaSV", "TenSV", "NamSinh", "SDT", "MaLop", "Tuoi")
        self.student_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.student_tree.heading(col, text=col)
            self.student_tree.column(col, width=120)
        
        self.student_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind selection
        self.student_tree.bind('<<TreeviewSelect>>', self.on_student_select)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.student_tree.yview)
        self.student_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load student data
        self.refresh_student_list()
    
    def add_student(self):
        """Add a new student to the database"""
        try:
            # Get values from entries
            values = []
            for field in ["MaSV", "TenSV", "NamSinh", "SDT", "MaLop", "Tuoi"]:
                value = self.student_entries[field].get()
                if field == "Tuoi":
                    value = int(value) if value else 0
                values.append(value)
            
            # Check required fields
            if not values[0] or not values[1] or not values[2] or not values[4]:
                messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin bắt buộc!")
                return
            
            # Insert into database
            self.cursor.execute(
                "INSERT INTO SinhVien VALUES (?, ?, ?, ?, ?, ?)",
                values
            )
            self.conn.commit()
            
            messagebox.showinfo("Thành công", "Thêm sinh viên thành công!")
            self.refresh_student_list()
            self.clear_student_entries()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Mã sinh viên đã tồn tại!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
    
    def update_student(self):
        """Update student information"""
        selected = self.student_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sinh viên để cập nhật!")
            return
        
        try:
            # Get values from entries
            values = []
            for field in ["TenSV", "NamSinh", "SDT", "MaLop", "Tuoi"]:
                value = self.student_entries[field].get()
                if field == "Tuoi":
                    value = int(value) if value else 0
                values.append(value)
            
            student_id = self.student_entries["MaSV"].get()
            
            # Update database
            self.cursor.execute(
                "UPDATE SinhVien SET TenSV=?, NamSinh=?, SDT=?, MaLop=?, Tuoi=? WHERE MaSV=?",
                values + [student_id]
            )
            self.conn.commit()
            
            messagebox.showinfo("Thành công", "Cập nhật sinh viên thành công!")
            self.refresh_student_list()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
    
    def delete_student(self):
        """Delete a student from the database"""
        selected = self.student_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sinh viên để xóa!")
            return
        
        student_id = self.student_tree.item(selected[0])['values'][0]
        
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa sinh viên {student_id}?"):
            try:
                self.cursor.execute("DELETE FROM SinhVien WHERE MaSV=?", (student_id,))
                self.conn.commit()
                
                messagebox.showinfo("Thành công", "Xóa sinh viên thành công!")
                self.refresh_student_list()
                self.clear_student_entries()
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
    
    def on_student_select(self, event):
        """Handle student selection in the treeview"""
        selected = self.student_tree.selection()
        if selected:
            values = self.student_tree.item(selected[0])['values']
            fields = ["MaSV", "TenSV", "NamSinh", "SDT", "MaLop", "Tuoi"]
            
            for i, field in enumerate(fields):
                self.student_entries[field].delete(0, tk.END)
                self.student_entries[field].insert(0, str(values[i]) if values[i] is not None else "")
    
    def refresh_student_list(self):
        """Refresh the student list in the treeview"""
        # Clear existing data
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        
        # Fetch data from database and sort by class
        self.cursor.execute("SELECT * FROM SinhVien ORDER BY MaLop, MaSV")
        students = self.cursor.fetchall()
        
        # Insert data into treeview
        for student in students:
            self.student_tree.insert('', tk.END, values=student)
    
    def clear_student_entries(self):
        """Clear all student entry fields"""
        for entry in self.student_entries.values():
            entry.delete(0, tk.END)
    
    def show_borrow_return(self):
        """Display borrow/return management interface"""
        self.clear_content_frame()
        
        title_label = tk.Label(
            self.content_frame, 
            text="QUẢN LÝ MƯỢN/TRẢ SÁCH", 
            font=('Arial', 16, 'bold'),
            bg='#ecf0f1'
        )
        title_label.pack(pady=10)
        
        # Borrow/Return management frame
        borrow_frame = tk.Frame(self.content_frame, bg='#ecf0f1')
        borrow_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Input fields
        input_frame = tk.Frame(borrow_frame, bg='#ecf0f1')
        input_frame.pack(fill=tk.X, pady=10)
        
        fields = [
            ("Mã phiếu:", "MaPhieu"),
            ("Mã sinh viên:", "MaSV"),
            ("Mã sách:", "MaSach"),
            ("Số lượng mượn:", "SoLuongMuon"),
            ("Ngày mượn:", "NgayMuon"),
            ("Ngày trả:", "NgayTra")
        ]
        
        self.borrow_entries = {}
        for i, (label_text, field_name) in enumerate(fields):
            tk.Label(input_frame, text=label_text, bg='#ecf0f1').grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = tk.Entry(input_frame, width=30)
            entry.grid(row=i, column=1, pady=5, padx=10)
            self.borrow_entries[field_name] = entry
        
        # Buttons
        button_frame = tk.Frame(borrow_frame, bg='#ecf0f1')
        button_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            button_frame, 
            text="Tạo phiếu mượn", 
            command=self.create_borrow_record,
            bg='#2ecc71',
            fg='white',
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame, 
            text="Cập nhật", 
            command=self.update_borrow_record,
            bg='#f39c12',
            fg='white',
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame, 
            text="Xóa phiếu", 
            command=self.delete_borrow_record,
            bg='#e74c3c',
            fg='white',
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame, 
            text="Làm mới", 
            command=self.refresh_borrow_list,
            bg='#3498db',
            fg='white',
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # Borrow records list
        list_frame = tk.Frame(borrow_frame, bg='#ecf0f1')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        columns = ("MaPhieu", "MaSV", "MaSach", "SoLuongMuon", "NgayMuon", "NgayTra")
        self.borrow_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.borrow_tree.heading(col, text=col)
            self.borrow_tree.column(col, width=120)
        
        self.borrow_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind selection
        self.borrow_tree.bind('<<TreeviewSelect>>', self.on_borrow_select)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.borrow_tree.yview)
        self.borrow_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load borrow records data
        self.refresh_borrow_list()
    
    def create_borrow_record(self):
        """Create a new borrow record"""
        try:
            # Get values from entries
            values = []
            for field in ["MaPhieu", "MaSV", "MaSach", "SoLuongMuon", "NgayMuon", "NgayTra"]:
                value = self.borrow_entries[field].get()
                if field == "SoLuongMuon":
                    value = int(value) if value else 0
                values.append(value)
            
            # Check required fields
            if not values[0] or not values[1] or not values[2] or not values[3] or not values[4] or not values[5]:
                messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")
                return
            
            # Check if student exists
            self.cursor.execute("SELECT * FROM SinhVien WHERE MaSV=?", (values[1],))
            if not self.cursor.fetchone():
                messagebox.showerror("Lỗi", "Mã sinh viên không tồn tại!")
                return
            
            # Check if book exists and has enough quantity
            self.cursor.execute("SELECT SoLuong FROM Sach WHERE MaSach=?", (values[2],))
            book = self.cursor.fetchone()
            if not book:
                messagebox.showerror("Lỗi", "Mã sách không tồn tại!")
                return
            
            if book[0] < values[3]:
                messagebox.showerror("Lỗi", "Số lượng sách không đủ!")
                return
            
            # Insert into database
            self.cursor.execute(
                "INSERT INTO Phieu VALUES (?, ?, ?, ?, ?, ?)",
                values
            )
            
            # Update book quantity
            self.cursor.execute(
                "UPDATE Sach SET SoLuong = SoLuong - ? WHERE MaSach = ?",
                (values[3], values[2])
            )
            
            self.conn.commit()
            
            messagebox.showinfo("Thành công", "Tạo phiếu mượn thành công!")
            self.refresh_borrow_list()
            self.clear_borrow_entries()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Mã phiếu đã tồn tại!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
    
    def update_borrow_record(self):
        """Update borrow record information"""
        selected = self.borrow_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn phiếu để cập nhật!")
            return
        
        try:
            # Get values from entries
            values = []
            for field in ["MaSV", "MaSach", "SoLuongMuon", "NgayMuon", "NgayTra"]:
                value = self.borrow_entries[field].get()
                if field == "SoLuongMuon":
                    value = int(value) if value else 0
                values.append(value)
            
            record_id = self.borrow_entries["MaPhieu"].get()
            
            # Update database
            self.cursor.execute(
                "UPDATE Phieu SET MaSV=?, MaSach=?, SoLuongMuon=?, NgayMuon=?, NgayTra=? WHERE MaPhieu=?",
                values + [record_id]
            )
            self.conn.commit()
            
            messagebox.showinfo("Thành công", "Cập nhật phiếu thành công!")
            self.refresh_borrow_list()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
    
    def delete_borrow_record(self):
        """Delete a borrow record from the database"""
        selected = self.borrow_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn phiếu để xóa!")
            return
        
        record_id = self.borrow_tree.item(selected[0])['values'][0]
        book_id = self.borrow_tree.item(selected[0])['values'][2]
        quantity = self.borrow_tree.item(selected[0])['values'][3]
        
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa phiếu {record_id}?"):
            try:
                # Restore book quantity
                self.cursor.execute(
                    "UPDATE Sach SET SoLuong = SoLuong + ? WHERE MaSach = ?",
                    (quantity, book_id)
                )
                
                # Delete record
                self.cursor.execute("DELETE FROM Phieu WHERE MaPhieu=?", (record_id,))
                self.conn.commit()
                
                messagebox.showinfo("Thành công", "Xóa phiếu thành công!")
                self.refresh_borrow_list()
                self.clear_borrow_entries()
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
    
    def on_borrow_select(self, event):
        """Handle borrow record selection in the treeview"""
        selected = self.borrow_tree.selection()
        if selected:
            values = self.borrow_tree.item(selected[0])['values']
            fields = ["MaPhieu", "MaSV", "MaSach", "SoLuongMuon", "NgayMuon", "NgayTra"]
            
            for i, field in enumerate(fields):
                self.borrow_entries[field].delete(0, tk.END)
                self.borrow_entries[field].insert(0, str(values[i]) if values[i] is not None else "")
    
    def refresh_borrow_list(self):
        """Refresh the borrow records list in the treeview"""
        # Clear existing data
        for item in self.borrow_tree.get_children():
            self.borrow_tree.delete(item)
        
        # Fetch data from database
        self.cursor.execute("SELECT * FROM Phieu")
        records = self.cursor.fetchall()
        
        # Insert data into treeview
        for record in records:
            self.borrow_tree.insert('', tk.END, values=record)
    
    def clear_borrow_entries(self):
        """Clear all borrow record entry fields"""
        for entry in self.borrow_entries.values():
            entry.delete(0, tk.END)
    
    def show_search_books(self):
        """Display book search interface"""
        self.clear_content_frame()
        
        title_label = tk.Label(
            self.content_frame, 
            text="TÌM KIẾM SÁCH", 
            font=('Arial', 16, 'bold'),
            bg='#ecf0f1'
        )
        title_label.pack(pady=10)
        
        # Search frame
        search_frame = tk.Frame(self.content_frame, bg='#ecf0f1')
        search_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Search criteria
        criteria_frame = tk.Frame(search_frame, bg='#ecf0f1')
        criteria_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(criteria_frame, text="Tìm kiếm theo:", bg='#ecf0f1').grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.search_criteria = tk.StringVar(value="TenSach")
        criteria_options = [
            ("Tên sách", "TenSach"),
            ("Tác giả", "TacGia"),
            ("Thể loại", "TheLoai"),
            ("Nhà xuất bản", "NhaXB")
        ]
        
        for i, (text, value) in enumerate(criteria_options):
            tk.Radiobutton(
                criteria_frame, 
                text=text, 
                variable=self.search_criteria, 
                value=value,
                bg='#ecf0f1'
            ).grid(row=0, column=i+1, padx=10, pady=5)
        
        # Search input
        input_frame = tk.Frame(search_frame, bg='#ecf0f1')
        input_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(input_frame, text="Từ khóa:", bg='#ecf0f1').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.search_entry = tk.Entry(input_frame, width=50)
        self.search_entry.grid(row=0, column=1, pady=5, padx=10)
        
        tk.Button(
            input_frame, 
            text="Tìm kiếm", 
            command=self.perform_search,
            bg='#3498db',
            fg='white',
            width=15
        ).grid(row=0, column=2, padx=10)
        
        # Search results
        results_frame = tk.Frame(search_frame, bg='#ecf0f1')
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        columns = ("MaSach", "TenSach", "TacGia", "NamXB", "NhaXB", "TheLoai", "SoLuong")
        self.search_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.search_tree.heading(col, text=col)
            self.search_tree.column(col, width=120)
        
        self.search_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.search_tree.yview)
        self.search_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def perform_search(self):
        """Perform book search based on criteria"""
        criteria = self.search_criteria.get()
        keyword = self.search_entry.get()
        
        if not keyword:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập từ khóa tìm kiếm!")
            return
        
        # Clear existing data
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        # Perform search
        query = f"SELECT * FROM Sach WHERE {criteria} LIKE ?"
        self.cursor.execute(query, (f'%{keyword}%',))
        results = self.cursor.fetchall()
        
        # Display results
        for result in results:
            self.search_tree.insert('', tk.END, values=result)
        
        if not results:
            messagebox.showinfo("Thông báo", "Không tìm thấy kết quả phù hợp!")
    
    def show_search_students(self):
        """Display student search interface"""
        self.clear_content_frame()
        
        title_label = tk.Label(
            self.content_frame, 
            text="TÌM KIẾM SINH VIÊN", 
            font=('Arial', 16, 'bold'),
            bg='#ecf0f1'
        )
        title_label.pack(pady=10)
        
        # Search frame
        search_frame = tk.Frame(self.content_frame, bg='#ecf0f1')
        search_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Search criteria
        criteria_frame = tk.Frame(search_frame, bg='#ecf0f1')
        criteria_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(criteria_frame, text="Tìm kiếm theo:", bg='#ecf0f1').grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.search_student_criteria = tk.StringVar(value="TenSV")
        criteria_options = [
            ("Tên sinh viên", "TenSV"),
            ("Mã sinh viên", "MaSV"),
            ("Mã lớp", "MaLop"),
            ("Số điện thoại", "SDT")
        ]
        
        for i, (text, value) in enumerate(criteria_options):
            tk.Radiobutton(
                criteria_frame, 
                text=text, 
                variable=self.search_student_criteria, 
                value=value,
                bg='#ecf0f1'
            ).grid(row=0, column=i+1, padx=10, pady=5)
        
        # Search input
        input_frame = tk.Frame(search_frame, bg='#ecf0f1')
        input_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(input_frame, text="Từ khóa:", bg='#ecf0f1').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.search_student_entry = tk.Entry(input_frame, width=50)
        self.search_student_entry.grid(row=0, column=1, pady=5, padx=10)
        
        tk.Button(
            input_frame, 
            text="Tìm kiếm", 
            command=self.perform_student_search,
            bg='#3498db',
            fg='white',
            width=15
        ).grid(row=0, column=2, padx=10)
        
        # Search results
        results_frame = tk.Frame(search_frame, bg='#ecf0f1')
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        columns = ("MaSV", "TenSV", "NamSinh", "SDT", "MaLop", "Tuoi")
        self.search_student_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.search_student_tree.heading(col, text=col)
            self.search_student_tree.column(col, width=120)
        
        self.search_student_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.search_student_tree.yview)
        self.search_student_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def perform_student_search(self):
        """Perform student search based on criteria"""
        criteria = self.search_student_criteria.get()
        keyword = self.search_student_entry.get()
        
        if not keyword:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập từ khóa tìm kiếm!")
            return
        
        # Clear existing data
        for item in self.search_student_tree.get_children():
            self.search_student_tree.delete(item)
        
        # Perform search
        query = f"SELECT * FROM SinhVien WHERE {criteria} LIKE ? ORDER BY MaLop, MaSV"
        self.cursor.execute(query, (f'%{keyword}%',))
        results = self.cursor.fetchall()
        
        # Display results
        for result in results:
            self.search_student_tree.insert('', tk.END, values=result)
        
        if not results:
            messagebox.showinfo("Thông báo", "Không tìm thấy kết quả phù hợp!")
    
    def show_reports(self):
        """Display reports interface"""
        self.clear_content_frame()
        
        title_label = tk.Label(
            self.content_frame, 
            text="THỐNG KÊ BÁO CÁO", 
            font=('Arial', 16, 'bold'),
            bg='#ecf0f1'
        )
        title_label.pack(pady=10)
        
        # Reports frame
        reports_frame = tk.Frame(self.content_frame, bg='#ecf0f1')
        reports_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Report options
        options_frame = tk.Frame(reports_frame, bg='#ecf0f1')
        options_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(options_frame, text="Chọn báo cáo:", bg='#ecf0f1').grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.report_type = tk.StringVar(value="popular_books")
        report_options = [
            ("Sách được mượn nhiều nhất", "popular_books"),
            ("Sách sắp hết", "low_stock"),
            ("Sách quá hạn trả", "overdue_books")
        ]
        
        for i, (text, value) in enumerate(report_options):
            tk.Radiobutton(
                options_frame, 
                text=text, 
                variable=self.report_type, 
                value=value,
                bg='#ecf0f1'
            ).grid(row=0, column=i+1, padx=10, pady=5)
        
        # Generate report button
        button_frame = tk.Frame(reports_frame, bg='#ecf0f1')
        button_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            button_frame, 
            text="Tạo báo cáo", 
            command=self.generate_report,
            bg='#3498db',
            fg='white',
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # Report results
        results_frame = tk.Frame(reports_frame, bg='#ecf0f1')
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.report_text = tk.Text(results_frame, wrap=tk.WORD, width=80, height=20)
        self.report_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def generate_report(self):
        """Generate the selected report"""
        report_type = self.report_type.get()
        self.report_text.delete(1.0, tk.END)
        
        if report_type == "popular_books":
            self.generate_popular_books_report()
        elif report_type == "low_stock":
            self.generate_low_stock_report()
        elif report_type == "overdue_books":
            self.generate_overdue_books_report()
    
    def generate_popular_books_report(self):
        """Generate report of most borrowed books"""
        self.cursor.execute('''
            SELECT Sach.MaSach, Sach.TenSach, Sach.TacGia, SUM(Phieu.SoLuongMuon) as TotalBorrowed
            FROM Sach
            JOIN Phieu ON Sach.MaSach = Phieu.MaSach
            GROUP BY Sach.MaSach
            ORDER BY TotalBorrowed DESC
            LIMIT 10
        ''')
        
        results = self.cursor.fetchall()
        
        self.report_text.insert(tk.END, "TOP 10 SÁCH ĐƯỢC MƯỢN NHIỀU NHẤT\n")
        self.report_text.insert(tk.END, "=" * 50 + "\n\n")
        
        for i, (book_id, title, author, total) in enumerate(results, 1):
            self.report_text.insert(tk.END, f"{i}. {title} - {author}\n")
            self.report_text.insert(tk.END, f"   Mã sách: {book_id}, Số lượt mượn: {total}\n\n")
    
    def generate_low_stock_report(self):
        """Generate report of books with low stock"""
        self.cursor.execute('''
            SELECT MaSach, TenSach, TacGia, SoLuong
            FROM Sach
            WHERE SoLuong < 5
            ORDER BY SoLuong ASC
        ''')
        
        results = self.cursor.fetchall()
        
        self.report_text.insert(tk.END, "SÁCH SẮP HẾT TRONG KHO\n")
        self.report_text.insert(tk.END, "=" * 50 + "\n\n")
        
        for book_id, title, author, quantity in results:
            self.report_text.insert(tk.END, f"- {title} - {author}\n")
            self.report_text.insert(tk.END, f"  Mã sách: {book_id}, Số lượng còn: {quantity}\n\n")
    
    def generate_overdue_books_report(self):
        """Generate report of overdue books"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        self.cursor.execute('''
            SELECT Phieu.MaPhieu, SinhVien.TenSV, Sach.TenSach, Phieu.NgayTra
            FROM Phieu
            JOIN SinhVien ON Phieu.MaSV = SinhVien.MaSV
            JOIN Sach ON Phieu.MaSach = Sach.MaSach
            WHERE Phieu.NgayTra < ?
        ''', (today,))
        
        results = self.cursor.fetchall()
        
        self.report_text.insert(tk.END, "SÁCH QUÁ HẠN TRẢ\n")
        self.report_text.insert(tk.END, "=" * 50 + "\n\n")
        
        for record_id, student_name, book_title, due_date in results:
            self.report_text.insert(tk.END, f"- {book_title}\n")
            self.report_text.insert(tk.END, f"  Người mượn: {student_name}\n")
            self.report_text.insert(tk.END, f"  Hạn trả: {due_date}, Mã phiếu: {record_id}\n\n")
    
    def exit_app(self):
        """Exit the application"""
        if messagebox.askokcancel("Thoát", "Bạn có chắc chắn muốn thoát ứng dụng?"):
            self.conn.close()
            self.root.destroy()

def main():
    root = tk.Tk()
    app = LibraryManagementSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()