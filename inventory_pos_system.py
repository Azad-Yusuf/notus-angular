# FULL CustomTkinter Inventory POS System with SQLite, all in one file
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import sqlite3
import barcode
from barcode.writer import ImageWriter
import os
import tempfile
import platform
from datetime import datetime
import csv
import hashlib

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

DB_FILE = "inventory.db"

class LoginWindow(ctk.CTkToplevel):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.title("Login")
        self.geometry("400x350")
        self.resizable(False, False)
        self.on_success = on_success
        self.conn = sqlite3.connect(DB_FILE)
        self.cursor = self.conn.cursor()
        self.init_users_table()
        self.create_widgets()
        self.grab_set()
        self.focus_force()
        self.lift()

    def init_users_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, role TEXT NOT NULL)''')
        self.conn.commit()
        # Create default admin if not exists
        self.cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not self.cursor.fetchone():
            pw_hash = hashlib.sha256("admin".encode()).hexdigest()
            self.cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", pw_hash, "Admin"))
            self.conn.commit()

    def create_widgets(self):
        # Main frame
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Title
        title_label = ctk.CTkLabel(frame, text="Inventory POS System", font=("Segoe UI", 20, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Username
        ctk.CTkLabel(frame, text="Username", font=("Segoe UI", 12)).pack(anchor="w", pady=(0, 4))
        self.username_entry = ctk.CTkEntry(frame, placeholder_text="Enter username")
        self.username_entry.pack(fill="x", pady=(0, 12))
        
        # Password
        ctk.CTkLabel(frame, text="Password", font=("Segoe UI", 12)).pack(anchor="w", pady=(0, 4))
        self.password_entry = ctk.CTkEntry(frame, show="*", placeholder_text="Enter password")
        self.password_entry.pack(fill="x", pady=(0, 12))
        
        # Role
        self.role_var = tk.StringVar(value="Admin")
        ctk.CTkLabel(frame, text="Role", font=("Segoe UI", 12)).pack(anchor="w", pady=(0, 4))
        self.role_combo = ctk.CTkComboBox(frame, values=["Admin", "Cashier"], variable=self.role_var, state="readonly")
        self.role_combo.pack(fill="x", pady=(0, 12))
        
        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        self.login_btn = ctk.CTkButton(
            button_frame, 
            text="Login", 
            command=self.login,
            fg_color="#007bff",
            hover_color="#0056b3",
            font=("Segoe UI", 12, "bold"),
            height=40
        )
        self.login_btn.pack(fill="x", pady=(0, 10))
        
        self.register_btn = ctk.CTkButton(
            button_frame, 
            text="Register New User", 
            command=self.register_user,
            fg_color="#6c757d",
            hover_color="#495057",
            font=("Segoe UI", 12),
            height=35
        )
        self.register_btn.pack(fill="x")
        
        # Default credentials info
        info_label = ctk.CTkLabel(frame, text="Default: admin/admin", font=("Segoe UI", 10), text_color="gray")
        info_label.pack(pady=(15, 0))
        
        # Bind Enter key to login
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self.login())
        
        # Focus on username entry
        self.username_entry.focus()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password!")
            return
            
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute("SELECT * FROM users WHERE username = ? AND password = ? AND role = ?", (username, pw_hash, role))
        user = self.cursor.fetchone()
        
        if user:
            self.on_success(username, role)
            self.destroy()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials or role.")
            self.password_entry.delete(0, "end")
            self.password_entry.focus()

    def register_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password required!")
            return
            
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            self.cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, pw_hash, role))
            self.conn.commit()
            messagebox.showinfo("Success", "User registered! You can now log in.")
            self.username_entry.delete(0, "end")
            self.password_entry.delete(0, "end")
            self.username_entry.focus()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists!")

class InventoryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Inventory Management & POS System")
        self.geometry("1400x900")
        self.configure(bg="#f0f2f5")
        self.conn = sqlite3.connect(DB_FILE)
        self.cursor = self.conn.cursor()
        self.init_database()
        self.withdraw()
        LoginWindow(self, self.on_login_success)

    def on_login_success(self, username, role):
        self.username = username
        self.role = role
        self.deiconify()
        self.create_ui()

    def init_database(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS subcategories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, category_id INTEGER, UNIQUE(name, category_id), FOREIGN KEY (category_id) REFERENCES categories(id))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, category_id INTEGER, subcategory_id INTEGER, brand TEXT, mrp REAL NOT NULL, selling_price REAL NOT NULL, purchase_price REAL NOT NULL, stock_quantity INTEGER NOT NULL, sku TEXT UNIQUE NOT NULL, barcode TEXT UNIQUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (category_id) REFERENCES categories(id), FOREIGN KEY (subcategory_id) REFERENCES subcategories(id))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY AUTOINCREMENT, item_id INTEGER, item_name TEXT, quantity INTEGER, unit_price REAL, total_price REAL, discount REAL, tax REAL, payment_method TEXT, bill_number TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (item_id) REFERENCES items(id))''')
        self.conn.commit()

    def create_ui(self):
        self.tabs = ctk.CTkTabview(self, width=1280, height=60, corner_radius=8)
        self.tabs.pack(padx=20, pady=(20, 0), fill="x")
        # Tabs based on role
        if self.role == "Admin":
            self.tabs.add("Add Items")
            self.add_items_tab = AddItemsTab(self.tabs.tab("Add Items"), self.conn)
            self.tabs.add("Category Management")
            self.category_tab = CategoryTab(self.tabs.tab("Category Management"), self.conn, self.add_items_tab)
            self.tabs.add("Point of Sale")
            self.pos_tab = POSTab(self.tabs.tab("Point of Sale"), self.conn)
            self.tabs.add("Stock Management")
            self.stock_tab = StockTab(self.tabs.tab("Stock Management"), self.conn)
            self.tabs.add("Reports")
            self.reports_tab = ReportsTab(self.tabs.tab("Reports"), self.conn)
        elif self.role == "Cashier":
            self.tabs.add("Point of Sale")
            self.pos_tab = POSTab(self.tabs.tab("Point of Sale"), self.conn)
        self.tabs.set(self.tabs._tab_list[0])

class AddItemsTab(ctk.CTkFrame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.cursor = conn.cursor()
        self.pack(fill="both", expand=True)
        self.create_widgets()
        self.refresh_categories()
        self.refresh_table()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color="#f0f2f5")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        # Left: Add New Item Card
        add_card = ctk.CTkFrame(main_frame, width=400, height=600, corner_radius=12, fg_color="#fff", border_width=1, border_color="#e0e0e0")
        add_card.grid(row=0, column=0, sticky="nsw", padx=(0, 24), pady=0)
        add_card.grid_propagate(False)
        header = ctk.CTkLabel(add_card, text="Add New Item", font=("Segoe UI", 18, "bold"), text_color="#fff", fg_color="#007bff", corner_radius=12, height=48)
        header.pack(fill="x", pady=(0, 0))
        form_frame = ctk.CTkFrame(add_card, fg_color="#fff")
        form_frame.pack(fill="both", expand=True, padx=24, pady=24)
        self.category_combo = ctk.CTkComboBox(form_frame, values=["Select Category"])
        self.subcategory_combo = ctk.CTkComboBox(form_frame, values=["Select Sub-category"])
        self.item_name_entry = ctk.CTkEntry(form_frame, placeholder_text="Enter item name")
        self.brand_entry = ctk.CTkEntry(form_frame, placeholder_text="Enter brand")
        self.mrp_entry = ctk.CTkEntry(form_frame, placeholder_text="0.00")
        self.selling_price_entry = ctk.CTkEntry(form_frame, placeholder_text="0.00")
        self.purchase_price_entry = ctk.CTkEntry(form_frame, placeholder_text="0.00")
        self.stock_quantity_entry = ctk.CTkEntry(form_frame, placeholder_text="0")
        self.barcode_entry = ctk.CTkEntry(form_frame, placeholder_text="Enter or scan barcode")
        # Layout
        labels = ["Category *", "Sub-category", "Item Name *", "Brand", "MRP *", "Selling Price *", "Purchase Price *", "Stock Quantity *", "Barcode"]
        widgets = [self.category_combo, self.subcategory_combo, self.item_name_entry, self.brand_entry, self.mrp_entry, self.selling_price_entry, self.purchase_price_entry, self.stock_quantity_entry, self.barcode_entry]
        for i, (label, widget) in enumerate(zip(labels, widgets)):
            lbl = ctk.CTkLabel(form_frame, text=label, font=("Segoe UI", 12, "bold"), anchor="w", text_color="#222")
            lbl.grid(row=i, column=0, sticky="w", pady=(0, 8))
            widget.grid(row=i, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))
            form_frame.grid_columnconfigure(1, weight=1)
        # Category change updates subcategories
        self.category_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_subcategories())
        # Buttons
        btn_frame = ctk.CTkFrame(form_frame, fg_color="#fff")
        btn_frame.grid(row=len(labels), column=0, columnspan=2, pady=(16, 0), sticky="ew")
        add_btn = ctk.CTkButton(btn_frame, text="Add Item", fg_color="#007bff", hover_color="#0056b3", font=("Segoe UI", 12, "bold"), width=120, command=self.add_item)
        clear_btn = ctk.CTkButton(btn_frame, text="Clear Form", fg_color="#6c757d", hover_color="#495057", font=("Segoe UI", 12, "bold"), width=120, command=self.clear_form)
        add_btn.pack(side="left", padx=(0, 12))
        clear_btn.pack(side="left")
        # Right: Items List Card
        list_card = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#fff", border_width=1, border_color="#e0e0e0")
        list_card.grid(row=0, column=1, sticky="nsew")
        list_card.grid_rowconfigure(2, weight=1)
        list_card.grid_columnconfigure(0, weight=1)
        header_row = ctk.CTkFrame(list_card, fg_color="#fff")
        header_row.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 0))
        title = ctk.CTkLabel(header_row, text="Current Items", font=("Segoe UI", 16, "bold"), text_color="#222")
        title.pack(side="left")
        self.barcode_btn = ctk.CTkButton(header_row, text="Generate Barcode", fg_color="#6c757d", hover_color="#495057", font=("Segoe UI", 12), width=140, command=self.generate_barcode)
        self.print_btn = ctk.CTkButton(header_row, text="Print Barcode", fg_color="#6c757d", hover_color="#495057", font=("Segoe UI", 12), width=140, command=self.print_barcode)
        self.refresh_btn = ctk.CTkButton(header_row, text="Refresh", fg_color="#6c757d", hover_color="#495057", font=("Segoe UI", 12), width=100, command=self.refresh_table)
        self.barcode_btn.pack(side="left", padx=(24, 6))
        self.print_btn.pack(side="left", padx=6)
        self.refresh_btn.pack(side="left", padx=6)
        # Table
        table_frame = ctk.CTkFrame(list_card, fg_color="#fff")
        table_frame.grid(row=2, column=0, sticky="nsew", padx=24, pady=(12, 24))
        self.table = ttk.Treeview(table_frame, columns=("name", "category", "subcategory", "brand", "price", "stock", "sku", "barcode"), show="headings", height=15)
        for col, text, w in zip(["name", "category", "subcategory", "brand", "price", "stock", "sku", "barcode"], ["Item Name", "Category", "Sub-category", "Brand", "Selling Price", "Stock", "SKU", "Barcode"], [160, 120, 120, 120, 120, 80, 120, 120]):
            self.table.heading(col, text=text)
            self.table.column(col, width=w)
        self.table.pack(fill="both", expand=True)
        self.table.bind("<Double-1>", self.edit_item_dialog)
        # Context menu for delete
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Delete Item", command=self.delete_selected_item)
        self.table.bind("<Button-3>", self.show_context_menu)

    def refresh_categories(self):
        self.cursor.execute("SELECT name FROM categories ORDER BY name")
        cats = [row[0] for row in self.cursor.fetchall()]
        self.category_combo.configure(values=["Select Category"] + cats)
        self.category_combo.set("Select Category")
        self.refresh_subcategories()

    def refresh_subcategories(self):
        cat = self.category_combo.get()
        if cat and cat != "Select Category":
            self.cursor.execute("SELECT id FROM categories WHERE name = ?", (cat,))
            cat_id = self.cursor.fetchone()
            if cat_id:
                self.cursor.execute("SELECT name FROM subcategories WHERE category_id = ? ORDER BY name", (cat_id[0],))
                subcats = [row[0] for row in self.cursor.fetchall()]
                self.subcategory_combo.configure(values=["Select Sub-category"] + subcats)
                self.subcategory_combo.set("Select Sub-category")
                return
        self.subcategory_combo.configure(values=["Select Sub-category"])
        self.subcategory_combo.set("Select Sub-category")

    def refresh_table(self):
        for row in self.table.get_children():
            self.table.delete(row)
        self.cursor.execute('''SELECT i.name, c.name, s.name, i.brand, i.selling_price, i.stock_quantity, i.sku, i.barcode FROM items i LEFT JOIN categories c ON i.category_id = c.id LEFT JOIN subcategories s ON i.subcategory_id = s.id''')
        for item in self.cursor.fetchall():
            self.table.insert("", "end", values=item)

    def add_item(self):
        name = self.item_name_entry.get().strip()
        category = self.category_combo.get().strip()
        subcategory = self.subcategory_combo.get().strip()
        brand = self.brand_entry.get().strip()
        mrp = self.mrp_entry.get().strip()
        selling_price = self.selling_price_entry.get().strip()
        purchase_price = self.purchase_price_entry.get().strip()
        stock_quantity = self.stock_quantity_entry.get().strip()
        barcode_val = self.barcode_entry.get().strip()
        if not name or not category or category == "Select Category" or not mrp or not selling_price or not purchase_price or not stock_quantity:
            messagebox.showerror("Error", "Please fill all required fields!")
            return
        # Get category/subcategory IDs
        self.cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
        cat_row = self.cursor.fetchone()
        cat_id = cat_row[0] if cat_row else None
        subcat_id = None
        if subcategory and subcategory != "Select Sub-category":
            self.cursor.execute("SELECT id FROM subcategories WHERE name = ? AND category_id = ?", (subcategory, cat_id))
            subcat_row = self.cursor.fetchone()
            if subcat_row:
                subcat_id = subcat_row[0]
        # Auto-generate SKU
        self.cursor.execute("SELECT sku FROM items ORDER BY id DESC LIMIT 1")
        last_sku = self.cursor.fetchone()
        if last_sku and last_sku[0] and last_sku[0].startswith("ITM"):
            try:
                last_num = int(last_sku[0][3:])
            except Exception:
                last_num = 0
        else:
            last_num = 0
        sku = f"ITM{last_num+1:06d}"
        # Barcode logic: default to SKU if not provided
        if not barcode_val:
            barcode_val = sku
        # Check for duplicate barcode
        self.cursor.execute("SELECT id FROM items WHERE barcode = ?", (barcode_val,))
        if self.cursor.fetchone():
            messagebox.showerror("Error", "Barcode already exists! Please use a different barcode.")
            return
        # Insert into database
        self.cursor.execute('''INSERT INTO items (name, category_id, subcategory_id, brand, mrp, selling_price, purchase_price, stock_quantity, sku, barcode) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (name, cat_id, subcat_id, brand, float(mrp), float(selling_price), float(purchase_price), int(stock_quantity), sku, barcode_val))
        self.conn.commit()
        messagebox.showinfo("Success", "Item added successfully!")
        self.clear_form()
        self.refresh_table()
        self.refresh_categories()

    def clear_form(self):
        self.item_name_entry.delete(0, "end")
        self.brand_entry.delete(0, "end")
        self.mrp_entry.delete(0, "end")
        self.selling_price_entry.delete(0, "end")
        self.purchase_price_entry.delete(0, "end")
        self.stock_quantity_entry.delete(0, "end")
        self.barcode_entry.delete(0, "end")
        self.refresh_categories()

    def generate_barcode(self):
        selection = self.table.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item!")
            return
        item_data = self.table.item(selection[0])['values']
        if not item_data:
            messagebox.showwarning("Warning", "No item data found!")
            return
        barcode_val = item_data[7] if len(item_data) > 7 else None
        if not barcode_val:
            messagebox.showwarning("Warning", "No barcode value found!")
            return
        try:
            code128 = barcode.get_barcode_class('code128')
            barcode_instance = code128(str(barcode_val), writer=ImageWriter())
            filename = f"barcode_{barcode_val}"
            barcode_path = barcode_instance.save(filename)
            messagebox.showinfo("Success", f"Barcode generated: {barcode_path}")
            if platform.system() == "Windows":
                os.startfile(barcode_path)
            elif platform.system() == "Darwin":
                os.system(f"open {barcode_path}")
            else:
                os.system(f"xdg-open {barcode_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate barcode: {str(e)}")

    def print_barcode(self):
        selection = self.table.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item!")
            return
        item_data = self.table.item(selection[0])['values']
        if not item_data:
            messagebox.showwarning("Warning", "No item data found!")
            return
        copies = simpledialog.askinteger("Print Copies", "Number of copies to print:", initialvalue=1, minvalue=1, maxvalue=100)
        if not copies:
            return
        try:
            html_content = f"""
            <html>
            <head>
                <style>
                    .barcode-label {{
                        width: 50mm;
                        height: 38.2mm;
                        border: 1px solid black;
                        margin: 2mm;
                        padding: 2mm;
                        text-align: center;
                        font-family: Arial, sans-serif;
                        font-size: 8pt;
                        display: inline-block;
                    }}
                    .item-name {{
                        font-weight: bold;
                        margin-bottom: 2mm;
                    }}
                    .price {{
                        font-size: 10pt;
                        font-weight: bold;
                    }}
                </style>
            </head>
            <body>
            """
            for i in range(copies):
                html_content += f"""
                <div class=\"barcode-label\">
                    <div class=\"item-name\">{item_data[0]}</div>
                    <div>SKU: {item_data[6]}</div>
                    <div class=\"price\">{item_data[4]}</div>
                    <div style=\"font-size: 6pt;\">{item_data[7]}</div>
                </div>
                """
            html_content += "</body></html>"
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp_file:
                temp_file.write(html_content)
                temp_file_path = temp_file.name
            if platform.system() == "Windows":
                os.startfile(temp_file_path)
            elif platform.system() == "Darwin":
                os.system(f"open {temp_file_path}")
            else:
                os.system(f"xdg-open {temp_file_path}")
            messagebox.showinfo("Success", f"Barcode labels ready for printing ({copies} copies)")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to prepare barcode for printing: {str(e)}")

    def show_context_menu(self, event):
        iid = self.table.identify_row(event.y)
        if iid:
            self.table.selection_set(iid)
            self.menu.post(event.x_root, event.y_root)

    def delete_selected_item(self):
        selection = self.table.selection()
        if not selection:
            return
        item_data = self.table.item(selection[0])['values']
        if not item_data:
            return
        if messagebox.askyesno("Delete Item", f"Delete item '{item_data[0]}'?"):
            self.cursor.execute("DELETE FROM items WHERE sku = ?", (item_data[6],))
            self.conn.commit()
            self.refresh_table()

    def edit_item_dialog(self, event):
        selection = self.table.selection()
        if not selection:
            return
        item_data = self.table.item(selection[0])['values']
        if not item_data:
            return
        # Simple edit dialog for name, brand, prices, stock
        edit_win = tk.Toplevel(self)
        edit_win.title(f"Edit Item: {item_data[0]}")
        edit_win.geometry("400x400")
        edit_win.grab_set()
        fields = ["Item Name", "Brand", "MRP", "Selling Price", "Purchase Price", "Stock Quantity"]
        entries = []
        for i, (label, val) in enumerate(zip(fields, [item_data[0], item_data[3], '', item_data[4], '', item_data[5]])):
            tk.Label(edit_win, text=label+":").pack(anchor="w", pady=(10 if i==0 else 4, 2))
            e = tk.Entry(edit_win)
            e.pack(fill="x", padx=10)
            e.insert(0, val)
            entries.append(e)
        def save_edit():
            new_name = entries[0].get().strip()
            new_brand = entries[1].get().strip()
            new_mrp = entries[2].get().strip()
            new_selling = entries[3].get().strip().replace('₹','')
            new_purchase = entries[4].get().strip()
            new_stock = entries[5].get().strip()
            if not new_name or not new_mrp or not new_selling or not new_purchase or not new_stock:
                messagebox.showerror("Error", "All fields required!")
                return
            self.cursor.execute('''UPDATE items SET name=?, brand=?, mrp=?, selling_price=?, purchase_price=?, stock_quantity=? WHERE sku=?''', (new_name, new_brand, float(new_mrp), float(new_selling), float(new_purchase), int(new_stock), item_data[6]))
            self.conn.commit()
            edit_win.destroy()
            self.refresh_table()
        tk.Button(edit_win, text="Save", command=save_edit).pack(pady=20)
        tk.Button(edit_win, text="Cancel", command=edit_win.destroy).pack()

class CategoryTab(ctk.CTkFrame):
    def __init__(self, parent, conn, add_items_tab):
        super().__init__(parent)
        self.conn = conn
        self.cursor = conn.cursor()
        self.add_items_tab = add_items_tab
        self.pack(fill="both", expand=True)
        self.create_widgets()
        self.refresh_category_listbox()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color="#f0f2f5")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        # Category List
        cat_frame = ctk.CTkFrame(main_frame, fg_color="#fff", corner_radius=12, border_width=1, border_color="#e0e0e0")
        cat_frame.pack(side="left", fill="y", padx=(0, 24), pady=0)
        cat_label = ctk.CTkLabel(cat_frame, text="Categories", font=("Segoe UI", 14, "bold"), text_color="#222")
        cat_label.pack(pady=(16, 8))
        self.category_listbox = tk.Listbox(cat_frame, height=15)
        self.category_listbox.pack(fill="y", expand=True, padx=10, pady=5)
        self.category_listbox.bind('<<ListboxSelect>>', self.on_category_select)
        cat_btn_frame = ctk.CTkFrame(cat_frame, fg_color="#fff")
        cat_btn_frame.pack(pady=5)
        ctk.CTkButton(cat_btn_frame, text="Add", command=self.add_category_dialog, width=80).pack(side="left", padx=2)
        ctk.CTkButton(cat_btn_frame, text="Edit", command=self.edit_category_dialog, width=80).pack(side="left", padx=2)
        ctk.CTkButton(cat_btn_frame, text="Delete", command=self.delete_category, width=80).pack(side="left", padx=2)
        # Subcategory List
        subcat_frame = ctk.CTkFrame(main_frame, fg_color="#fff", corner_radius=12, border_width=1, border_color="#e0e0e0")
        subcat_frame.pack(side="left", fill="y", padx=(0, 24), pady=0)
        subcat_label = ctk.CTkLabel(subcat_frame, text="Subcategories", font=("Segoe UI", 14, "bold"), text_color="#222")
        subcat_label.pack(pady=(16, 8))
        self.subcategory_listbox = tk.Listbox(subcat_frame, height=15)
        self.subcategory_listbox.pack(fill="y", expand=True, padx=10, pady=5)
        subcat_btn_frame = ctk.CTkFrame(subcat_frame, fg_color="#fff")
        subcat_btn_frame.pack(pady=5)
        ctk.CTkButton(subcat_btn_frame, text="Add", command=self.add_subcategory_dialog, width=80).pack(side="left", padx=2)
        ctk.CTkButton(subcat_btn_frame, text="Edit", command=self.edit_subcategory_dialog, width=80).pack(side="left", padx=2)
        ctk.CTkButton(subcat_btn_frame, text="Delete", command=self.delete_subcategory, width=80).pack(side="left", padx=2)

    def refresh_category_listbox(self):
        self.category_listbox.delete(0, tk.END)
        self.cursor.execute("SELECT name FROM categories ORDER BY name")
        for row in self.cursor.fetchall():
            self.category_listbox.insert(tk.END, row[0])
        self.subcategory_listbox.delete(0, tk.END)

    def on_category_select(self, event=None):
        sel = self.category_listbox.curselection()
        if not sel:
            self.subcategory_listbox.delete(0, tk.END)
            return
        cat_name = self.category_listbox.get(sel[0])
        self.cursor.execute("SELECT id FROM categories WHERE name = ?", (cat_name,))
        cat_id = self.cursor.fetchone()[0]
        self.subcategory_listbox.delete(0, tk.END)
        self.cursor.execute("SELECT name FROM subcategories WHERE category_id = ? ORDER BY name", (cat_id,))
        for row in self.cursor.fetchall():
            self.subcategory_listbox.insert(tk.END, row[0])

    def add_category_dialog(self):
        name = simpledialog.askstring("Add Category", "Category name:")
        if name:
            try:
                self.cursor.execute("INSERT INTO categories (name) VALUES (?)", (name.strip(),))
                self.conn.commit()
                self.refresh_category_listbox()
                self.add_items_tab.refresh_categories()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add category: {str(e)}")

    def edit_category_dialog(self):
        sel = self.category_listbox.curselection()
        if not sel:
            return
        old_name = self.category_listbox.get(sel[0])
        new_name = simpledialog.askstring("Edit Category", "New name:", initialvalue=old_name)
        if new_name and new_name != old_name:
            try:
                self.cursor.execute("UPDATE categories SET name = ? WHERE name = ?", (new_name.strip(), old_name))
                self.conn.commit()
                self.refresh_category_listbox()
                self.add_items_tab.refresh_categories()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to edit category: {str(e)}")

    def delete_category(self):
        sel = self.category_listbox.curselection()
        if not sel:
            return
        name = self.category_listbox.get(sel[0])
        if messagebox.askyesno("Delete Category", f"Delete category '{name}' and all its subcategories?"):
            try:
                self.cursor.execute("DELETE FROM subcategories WHERE category_id = (SELECT id FROM categories WHERE name = ?)", (name,))
                self.cursor.execute("DELETE FROM categories WHERE name = ?", (name,))
                self.conn.commit()
                self.refresh_category_listbox()
                self.add_items_tab.refresh_categories()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete category: {str(e)}")

    def add_subcategory_dialog(self):
        sel = self.category_listbox.curselection()
        if not sel:
            return
        cat_name = self.category_listbox.get(sel[0])
        self.cursor.execute("SELECT id FROM categories WHERE name = ?", (cat_name,))
        cat_id = self.cursor.fetchone()[0]
        name = simpledialog.askstring("Add Subcategory", "Subcategory name:")
        if name:
            try:
                self.cursor.execute("INSERT INTO subcategories (name, category_id) VALUES (?, ?)", (name.strip(), cat_id))
                self.conn.commit()
                self.on_category_select()
                self.add_items_tab.refresh_categories()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add subcategory: {str(e)}")

    def edit_subcategory_dialog(self):
        sel_cat = self.category_listbox.curselection()
        sel_sub = self.subcategory_listbox.curselection()
        if not sel_cat or not sel_sub:
            return
        cat_name = self.category_listbox.get(sel_cat[0])
        subcat_name = self.subcategory_listbox.get(sel_sub[0])
        new_name = simpledialog.askstring("Edit Subcategory", "New name:", initialvalue=subcat_name)
        if new_name and new_name != subcat_name:
            self.cursor.execute("SELECT id FROM categories WHERE name = ?", (cat_name,))
            cat_id = self.cursor.fetchone()[0]
            try:
                self.cursor.execute("UPDATE subcategories SET name = ? WHERE name = ? AND category_id = ?", (new_name.strip(), subcat_name, cat_id))
                self.conn.commit()
                self.on_category_select()
                self.add_items_tab.refresh_categories()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to edit subcategory: {str(e)}")

    def delete_subcategory(self):
        sel_cat = self.category_listbox.curselection()
        sel_sub = self.subcategory_listbox.curselection()
        if not sel_cat or not sel_sub:
            return
        cat_name = self.category_listbox.get(sel_cat[0])
        subcat_name = self.subcategory_listbox.get(sel_sub[0])
        if messagebox.askyesno("Delete Subcategory", f"Delete subcategory '{subcat_name}'?"):
            self.cursor.execute("SELECT id FROM categories WHERE name = ?", (cat_name,))
            cat_id = self.cursor.fetchone()[0]
            try:
                self.cursor.execute("DELETE FROM subcategories WHERE name = ? AND category_id = ?", (subcat_name, cat_id))
                self.conn.commit()
                self.on_category_select()
                self.add_items_tab.refresh_categories()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete subcategory: {str(e)}")

class POSTab(ctk.CTkFrame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.cursor = conn.cursor()
        self.pack(fill="both", expand=True)
        self.cart_items = []
        self.total_amount = 0.0
        self.create_widgets()
        self.load_items_for_selection()
        self.calculate_total()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color="#f0f2f5")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        # Left: Barcode/manual selection
        left_panel = ctk.CTkFrame(main_frame, fg_color="#fff", corner_radius=12, border_width=1, border_color="#e0e0e0")
        left_panel.grid(row=0, column=0, sticky="nsw", padx=(0, 24), pady=0)
        left_panel.grid_propagate(False)
        left_panel.configure(width=400)
        # Barcode entry
        barcode_label = ctk.CTkLabel(left_panel, text="Barcode Scanner", font=("Segoe UI", 14, "bold"), text_color="#222")
        barcode_label.pack(pady=(16, 4))
        self.barcode_var = tk.StringVar()
        barcode_entry = ctk.CTkEntry(left_panel, textvariable=self.barcode_var, font=("Segoe UI", 14), width=300)
        barcode_entry.pack(padx=20, pady=(0, 10))
        barcode_entry.bind('<Return>', self.scan_barcode)
        barcode_entry.focus()
        # Manual item selection
        manual_label = ctk.CTkLabel(left_panel, text="Manual Item Selection", font=("Segoe UI", 12, "bold"), text_color="#222")
        manual_label.pack(pady=(10, 2))
        self.search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(left_panel, textvariable=self.search_var, font=("Segoe UI", 12), width=300)
        search_entry.pack(padx=20, pady=(0, 5))
        search_entry.bind('<KeyRelease>', self.search_items)
        self.items_listbox = tk.Listbox(left_panel, height=8)
        self.items_listbox.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self.items_listbox.bind('<Double-Button-1>', self.add_item_to_cart)
        # Add to cart button
        add_btn = ctk.CTkButton(left_panel, text="Add to Cart", fg_color="#007bff", hover_color="#0056b3", font=("Segoe UI", 12, "bold"), width=120, command=self.add_item_to_cart)
        add_btn.pack(pady=(0, 16))
        # Right: Cart and billing
        right_panel = ctk.CTkFrame(main_frame, fg_color="#fff", corner_radius=12, border_width=1, border_color="#e0e0e0")
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_rowconfigure(1, weight=1)
        # Cart label
        cart_label = ctk.CTkLabel(right_panel, text="Shopping Cart", font=("Segoe UI", 14, "bold"), text_color="#222")
        cart_label.pack(pady=(16, 4))
        # Cart table
        cart_frame = ctk.CTkFrame(right_panel, fg_color="#fff")
        cart_frame.pack(fill="both", expand=True, padx=24, pady=(0, 10))
        self.cart_tree = ttk.Treeview(cart_frame, columns=("item", "qty", "price", "total"), show="headings", height=10)
        for col, text, w in zip(["item", "qty", "price", "total"], ["Item", "Qty", "Price", "Total"], [200, 60, 100, 100]):
            self.cart_tree.heading(col, text=text)
            self.cart_tree.column(col, width=w, anchor="center")
        self.cart_tree.pack(fill="both", expand=True)
        # Cart buttons
        cart_btns = ctk.CTkFrame(right_panel, fg_color="#fff")
        cart_btns.pack(pady=5)
        ctk.CTkButton(cart_btns, text="Remove Item", command=self.remove_from_cart, width=120).pack(side="left", padx=5)
        ctk.CTkButton(cart_btns, text="Clear Cart", command=self.clear_cart, width=120).pack(side="left", padx=5)
        # Billing frame
        billing_frame = ctk.CTkFrame(right_panel, fg_color="#fff")
        billing_frame.pack(fill="x", padx=24, pady=(0, 10))
        # Discount
        discount_label = ctk.CTkLabel(billing_frame, text="Discount (%) :", font=("Segoe UI", 12), text_color="#222")
        discount_label.grid(row=0, column=0, sticky="w", pady=4)
        self.discount_var = tk.StringVar(value="0")
        discount_entry = ctk.CTkEntry(billing_frame, textvariable=self.discount_var, width=60)
        discount_entry.grid(row=0, column=1, pady=4, padx=(0, 20))
        # Tax
        tax_label = ctk.CTkLabel(billing_frame, text="Tax (%) :", font=("Segoe UI", 12), text_color="#222")
        tax_label.grid(row=0, column=2, sticky="w", pady=4)
        self.tax_var = tk.StringVar(value="18")
        tax_entry = ctk.CTkEntry(billing_frame, textvariable=self.tax_var, width=60)
        tax_entry.grid(row=0, column=3, pady=4, padx=(0, 20))
        # Total
        total_label = ctk.CTkLabel(billing_frame, text="Total Amount:", font=("Segoe UI", 13, "bold"), text_color="#007bff")
        total_label.grid(row=1, column=0, sticky="w", pady=8)
        self.total_label = ctk.CTkLabel(billing_frame, text="₹0.00", font=("Segoe UI", 13, "bold"), text_color="#d32f2f")
        self.total_label.grid(row=1, column=1, sticky="w", pady=8)
        # Payment method
        payment_label = ctk.CTkLabel(billing_frame, text="Payment Method:", font=("Segoe UI", 12), text_color="#222")
        payment_label.grid(row=2, column=0, sticky="w", pady=4)
        self.payment_var = tk.StringVar(value="Cash")
        self.payment_combo = ctk.CTkComboBox(billing_frame, values=["Cash", "UPI", "Card", "Credit"], variable=self.payment_var, width=120)
        self.payment_combo.grid(row=2, column=1, pady=4, padx=(0, 20))
        # Final buttons
        final_btns = ctk.CTkFrame(billing_frame, fg_color="#fff")
        final_btns.grid(row=3, column=0, columnspan=4, pady=10)
        ctk.CTkButton(final_btns, text="Calculate Total", command=self.calculate_total, width=140).pack(side="left", padx=5)
        ctk.CTkButton(final_btns, text="Print Bill", command=self.print_bill, width=140).pack(side="left", padx=5)
        ctk.CTkButton(final_btns, text="Complete Sale", command=self.complete_sale, width=140).pack(side="left", padx=5)

    def load_items_for_selection(self):
        self.items_listbox.delete(0, tk.END)
        self.cursor.execute("SELECT name, selling_price, stock_quantity FROM items WHERE stock_quantity > 0")
        items = self.cursor.fetchall()
        for item in items:
            display_text = f"{item[0]} - ₹{item[1]} (Stock: {item[2]})"
            self.items_listbox.insert(tk.END, display_text)

    def search_items(self, event=None):
        search_term = self.search_var.get().lower()
        self.items_listbox.delete(0, tk.END)
        self.cursor.execute("SELECT name, selling_price, stock_quantity FROM items WHERE stock_quantity > 0 AND LOWER(name) LIKE ?", (f"%{search_term}%",))
        items = self.cursor.fetchall()
        for item in items:
            display_text = f"{item[0]} - ₹{item[1]} (Stock: {item[2]})"
            self.items_listbox.insert(tk.END, display_text)

    def scan_barcode(self, event=None):
        barcode_data = self.barcode_var.get().strip()
        if not barcode_data:
            return
        self.cursor.execute("SELECT * FROM items WHERE LOWER(barcode) = ? AND stock_quantity > 0", (barcode_data.lower(),))
        item = self.cursor.fetchone()
        if item:
            self.add_item_to_cart_by_data(item)
            self.barcode_var.set("")
            if event and hasattr(event, 'widget'):
                event.widget.focus_set()
        else:
            self.cursor.execute("SELECT * FROM items WHERE LOWER(barcode) = ?", (barcode_data.lower(),))
            item_any_stock = self.cursor.fetchone()
            if item_any_stock:
                messagebox.showwarning("Out of Stock", "Item found but out of stock!")
            else:
                messagebox.showwarning("Item Not Found", "Item not found!")
            self.barcode_var.set("")
            if event and hasattr(event, 'widget'):
                event.widget.focus_set()

    def add_item_to_cart(self, event=None):
        selection = self.items_listbox.curselection()
        if not selection:
            return
        item_text = self.items_listbox.get(selection[0])
        item_name = item_text.split(" - ")[0]
        self.cursor.execute("SELECT * FROM items WHERE name = ?", (item_name,))
        item = self.cursor.fetchone()
        if item:
            self.add_item_to_cart_by_data(item)

    def add_item_to_cart_by_data(self, item):
        for cart_item in self.cart_items:
            if cart_item['id'] == item[0]:
                if cart_item['quantity'] < item[8]:
                    cart_item['quantity'] += 1
                    cart_item['total'] = cart_item['quantity'] * cart_item['price']
                    self.refresh_cart_display()
                    return
                else:
                    messagebox.showwarning("Stock Limit", "Cannot add more items. Stock limit reached!")
                    return
        cart_item = {
            'id': item[0],
            'name': item[1],
            'price': item[6],
            'quantity': 1,
            'total': item[6],
            'stock': item[8]
        }
        self.cart_items.append(cart_item)
        self.refresh_cart_display()

    def refresh_cart_display(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        for cart_item in self.cart_items:
            self.cart_tree.insert("", tk.END, values=(cart_item['name'], cart_item['quantity'], f"₹{cart_item['price']:.2f}", f"₹{cart_item['total']:.2f}"))
        self.calculate_total()

    def remove_from_cart(self):
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove!")
            return
        item_index = self.cart_tree.index(selection[0])
        del self.cart_items[item_index]
        self.refresh_cart_display()

    def clear_cart(self):
        self.cart_items.clear()
        self.refresh_cart_display()

    def calculate_total(self):
        subtotal = sum(item['total'] for item in self.cart_items)
        try:
            discount_percent = float(self.discount_var.get() or 0)
            tax_percent = float(self.tax_var.get() or 0)
        except ValueError:
            discount_percent = 0
            tax_percent = 0
        discount_amount = subtotal * (discount_percent / 100)
        taxable_amount = subtotal - discount_amount
        tax_amount = taxable_amount * (tax_percent / 100)
        self.total_amount = taxable_amount + tax_amount
        self.total_label.configure(text=f"₹{self.total_amount:.2f}")

    def print_bill(self):
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty!")
            return
        self.calculate_total()
        bill_number = f"BILL{datetime.now().strftime('%Y%m%d%H%M%S')}"
        bill_content = f"""
        ================================
             STORE MANAGEMENT SYSTEM
        ================================
        Bill No: {bill_number}
        Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        ================================
        Items:
        """
        subtotal = 0
        for item in self.cart_items:
            bill_content += f"\n{item['name']:<20} x{item['quantity']:<3} ₹{item['total']:.2f}"
            subtotal += item['total']
        discount_percent = float(self.discount_var.get() or 0)
        tax_percent = float(self.tax_var.get() or 0)
        discount_amount = subtotal * (discount_percent / 100)
        tax_amount = (subtotal - discount_amount) * (tax_percent / 100)
        bill_content += f"""
        ================================
        Subtotal:               ₹{subtotal:.2f}
        Discount ({discount_percent}%):        -₹{discount_amount:.2f}
        Tax ({tax_percent}%):               ₹{tax_amount:.2f}
        ================================
        TOTAL:                  ₹{self.total_amount:.2f}
        Payment Method: {self.payment_var.get()}
        Thank you for shopping with us!
        ================================
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(bill_content)
            temp_file_path = temp_file.name
        if platform.system() == "Windows":
            os.startfile(temp_file_path)
        else:
            os.system(f"open {temp_file_path}" if platform.system() == "Darwin" else f"xdg-open {temp_file_path}")
        messagebox.showinfo("Success", "Bill generated and ready for printing!")

    def complete_sale(self):
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty!")
            return
        self.calculate_total()
        try:
            bill_number = f"BILL{datetime.now().strftime('%Y%m%d%H%M%S')}"
            for item in self.cart_items:
                discount_percent = float(self.discount_var.get() or 0)
                tax_percent = float(self.tax_var.get() or 0)
                self.cursor.execute('''INSERT INTO sales (item_id, item_name, quantity, unit_price, total_price, discount, tax, payment_method, bill_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (item['id'], item['name'], item['quantity'], item['price'], item['total'], discount_percent, tax_percent, self.payment_var.get(), bill_number))
                self.cursor.execute('''UPDATE items SET stock_quantity = stock_quantity - ? WHERE id = ?''', (item['quantity'], item['id']))
            self.conn.commit()
            messagebox.showinfo("Success", f"Sale completed! Bill Number: {bill_number}")
            self.clear_cart()
            self.load_items_for_selection()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to complete sale: {str(e)}")

class StockTab(ctk.CTkFrame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.cursor = conn.cursor()
        self.pack(fill="both", expand=True)
        self.create_widgets()
        self.refresh_stock_list()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color="#f0f2f5")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        # Search
        search_frame = ctk.CTkFrame(main_frame, fg_color="#fff")
        search_frame.pack(fill="x", padx=10, pady=(10, 0))
        ctk.CTkLabel(search_frame, text="Search Item:", font=("Segoe UI", 12), text_color="#222").pack(side="left")
        self.stock_search_var = tk.StringVar()
        stock_search_entry = ctk.CTkEntry(search_frame, textvariable=self.stock_search_var, width=300)
        stock_search_entry.pack(side="left", padx=10)
        ctk.CTkButton(search_frame, text="Search", command=self.search_stock_items, width=100).pack(side="left", padx=5)
        # Stock table
        table_frame = ctk.CTkFrame(main_frame, fg_color="#fff")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.stock_tree = ttk.Treeview(table_frame, columns=("name", "category", "stock", "price"), show="headings", height=15)
        for col, text, w in zip(["name", "category", "stock", "price"], ["Item Name", "Category", "Current Stock", "Price"], [250, 150, 120, 100]):
            self.stock_tree.heading(col, text=text)
            self.stock_tree.column(col, width=w)
        self.stock_tree.pack(fill="both", expand=True)
        # Stock buttons
        stock_btns = ctk.CTkFrame(main_frame, fg_color="#f0f2f5")
        stock_btns.pack(pady=10)
        ctk.CTkButton(stock_btns, text="Update Stock", command=self.update_stock_dialog, width=120).pack(side="left", padx=5)
        ctk.CTkButton(stock_btns, text="Low Stock Alert", command=self.show_low_stock, width=140).pack(side="left", padx=5)
        ctk.CTkButton(stock_btns, text="Refresh", command=self.refresh_stock_list, width=100).pack(side="left", padx=5)

    def search_stock_items(self):
        search_term = self.stock_search_var.get().lower()
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)
        self.cursor.execute('''SELECT i.name, c.name, i.stock_quantity, i.selling_price FROM items i LEFT JOIN categories c ON i.category_id = c.id WHERE LOWER(i.name) LIKE ? OR LOWER(c.name) LIKE ?''', (f"%{search_term}%", f"%{search_term}%"))
        items = self.cursor.fetchall()
        for item in items:
            if item[2] <= 5:
                self.stock_tree.insert("", tk.END, values=item, tags=('low_stock',))
            else:
                self.stock_tree.insert("", tk.END, values=item)
        self.stock_tree.tag_configure('low_stock', background='#ffcccc')

    def refresh_stock_list(self):
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)
        self.cursor.execute('''SELECT i.name, c.name, i.stock_quantity, i.selling_price FROM items i LEFT JOIN categories c ON i.category_id = c.id''')
        items = self.cursor.fetchall()
        for item in items:
            if item[2] <= 5:
                self.stock_tree.insert("", tk.END, values=item, tags=('low_stock',))
            else:
                self.stock_tree.insert("", tk.END, values=item)
        self.stock_tree.tag_configure('low_stock', background='#ffcccc')

    def update_stock_dialog(self):
        selection = self.stock_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item!")
            return
        item_data = self.stock_tree.item(selection[0])['values']
        item_name = item_data[0]
        current_stock = item_data[2]
        dialog = tk.Toplevel(self)
        dialog.title("Update Stock")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        tk.Label(dialog, text=f"Item: {item_name}", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Label(dialog, text=f"Current Stock: {current_stock}").pack(pady=5)
        tk.Label(dialog, text="New Stock Quantity:").pack(pady=5)
        new_stock_var = tk.StringVar(value=str(current_stock))
        stock_entry = tk.Entry(dialog, textvariable=new_stock_var, width=20)
        stock_entry.pack(pady=5)
        stock_entry.focus()
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        def update_stock():
            try:
                new_stock = int(new_stock_var.get())
                if new_stock < 0:
                    messagebox.showerror("Error", "Stock quantity cannot be negative!")
                    return
                self.cursor.execute("UPDATE items SET stock_quantity = ? WHERE name = ?", (new_stock, item_name))
                self.conn.commit()
                messagebox.showinfo("Success", "Stock updated successfully!")
                dialog.destroy()
                self.refresh_stock_list()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update stock: {str(e)}")
        tk.Button(button_frame, text="Update", command=update_stock).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=10)

    def show_low_stock(self):
        self.cursor.execute("SELECT name, stock_quantity FROM items WHERE stock_quantity <= 5")
        low_stock_items = self.cursor.fetchall()
        if low_stock_items:
            alert_message = "Low Stock Alert!\n\nFollowing items are running low:\n\n"
            for item in low_stock_items:
                alert_message += f"• {item[0]}: {item[1]} units remaining\n"
            messagebox.showwarning("Low Stock Alert", alert_message)
        else:
            messagebox.showinfo("Stock Status", "All items have sufficient stock!")

class ReportsTab(ctk.CTkFrame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.cursor = conn.cursor()
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color="#f0f2f5")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        # Report buttons
        report_btns = ctk.CTkFrame(main_frame, fg_color="#fff")
        report_btns.pack(pady=20)
        ctk.CTkButton(report_btns, text="Daily Sales Report", command=self.daily_sales_report, width=160).pack(side="left", padx=10)
        ctk.CTkButton(report_btns, text="Item-wise Sales", command=self.item_wise_sales_report, width=160).pack(side="left", padx=10)
        ctk.CTkButton(report_btns, text="Low Stock Report", command=self.low_stock_report, width=160).pack(side="left", padx=10)
        ctk.CTkButton(report_btns, text="Export to CSV", command=self.export_to_csv, width=160).pack(side="left", padx=10)
        # Report display area
        text_frame = ctk.CTkFrame(main_frame, fg_color="#fff")
        text_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.report_text = tk.Text(text_frame, height=25, width=100, font=("Consolas", 11))
        self.report_text.pack(fill="both", expand=True, side="left")
        report_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.report_text.yview)
        report_scrollbar.pack(side="right", fill="y")
        self.report_text.configure(yscrollcommand=report_scrollbar.set)

    def daily_sales_report(self):
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute('''SELECT item_name, SUM(quantity), SUM(total_price), payment_method, COUNT(*) FROM sales WHERE DATE(created_at) = ? GROUP BY item_name, payment_method''', (today,))
        sales_data = self.cursor.fetchall()
        if not sales_data:
            report = f"Daily Sales Report - {today}\n\nNo sales recorded for today."
        else:
            report = f"Daily Sales Report - {today}\n"
            report += "=" * 60 + "\n\n"
            total_revenue = 0
            total_items = 0
            report += f"{'Item Name':<25} {'Qty':<8} {'Revenue':<12} {'Payment':<10} {'Bills':<8}\n"
            report += "-" * 60 + "\n"
            for sale in sales_data:
                report += f"{sale[0]:<25} {sale[1]:<8} ₹{sale[2]:<11.2f} {sale[3]:<10} {sale[4]:<8}\n"
                total_revenue += sale[2]
                total_items += sale[1]
            report += "-" * 60 + "\n"
            report += f"Total Items Sold: {total_items}\n"
            report += f"Total Revenue: ₹{total_revenue:.2f}\n"
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, report)

    def item_wise_sales_report(self):
        self.cursor.execute('''SELECT item_name, SUM(quantity), SUM(total_price), AVG(unit_price) FROM sales GROUP BY item_name ORDER BY SUM(total_price) DESC''')
        sales_data = self.cursor.fetchall()
        if not sales_data:
            report = "Item-wise Sales Report\n\nNo sales data available."
        else:
            report = "Item-wise Sales Report (All Time)\n"
            report += "=" * 70 + "\n\n"
            report += f"{'Item Name':<30} {'Qty Sold':<10} {'Revenue':<12} {'Avg Price':<12}\n"
            report += "-" * 70 + "\n"
            for sale in sales_data:
                report += f"{sale[0]:<30} {sale[1]:<10} ₹{sale[2]:<11.2f} ₹{sale[3]:<11.2f}\n"
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, report)

    def low_stock_report(self):
        self.cursor.execute("SELECT name, stock_quantity, selling_price FROM items WHERE stock_quantity <= 5")
        low_stock_items = self.cursor.fetchall()
        if not low_stock_items:
            report = "Low Stock Report\n\nAll items have sufficient stock!"
        else:
            report = "Low Stock Report\n"
            report += "=" * 60 + "\n\n"
            report += f"{'Item Name':<25} {'Stock':<8} {'Price':<12}\n"
            report += "-" * 60 + "\n"
            for item in low_stock_items:
                report += f"{item[0]:<25} {item[1]:<8} ₹{item[2]:<11.2f}\n"
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, report)

    def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not file_path:
            return
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # Export items data
                writer.writerow(["=== ITEMS DATA ==="])
                writer.writerow(["Name", "Category", "Sub-Category", "Brand", "MRP", "Selling Price", "Purchase Price", "Stock", "SKU"])
                self.cursor.execute('''SELECT i.name, c.name, s.name, i.brand, i.mrp, i.selling_price, i.purchase_price, i.stock_quantity, i.sku FROM items i LEFT JOIN categories c ON i.category_id = c.id LEFT JOIN subcategories s ON i.subcategory_id = s.id''')
                items = self.cursor.fetchall()
                writer.writerows(items)
                writer.writerow([])
                # Export sales data
                writer.writerow(["=== SALES DATA ==="])
                writer.writerow(["Item Name", "Quantity", "Unit Price", "Total Price", "Discount", "Tax", "Payment Method", "Sale Date", "Bill Number"])
                self.cursor.execute("SELECT item_name, quantity, unit_price, total_price, discount, tax, payment_method, created_at, bill_number FROM sales")
                sales = self.cursor.fetchall()
                writer.writerows(sales)
            messagebox.showinfo("Success", f"Data exported successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()