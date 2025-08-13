import tkinter as tk
from tkinter import messagebox, simpledialog
from spfet.auth import register_user, login_user
from spfet.storage import UserStore, Transaction
from spfet.constants import ALLOWED_CATEGORIES, TRANSACTION_TYPES
import matplotlib.pyplot as plt
from datetime import datetime

class Page(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
    def show(self):
        self.lift()

class LoginPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        tk.Label(self, text="SPFET Login/Register", font=("Arial", 18, "bold"), fg="#273c75", bg="#f5f6fa").pack(pady=20)
        tk.Label(self, text="Username:", font=("Arial", 12), bg="#f5f6fa").pack(pady=5)
        self.username_entry = tk.Entry(self, font=("Arial", 12), width=24)
        self.username_entry.pack(pady=2)
        tk.Label(self, text="Password:", font=("Arial", 12), bg="#f5f6fa").pack(pady=5)
        self.password_entry = tk.Entry(self, show="*", font=("Arial", 12), width=24)
        self.password_entry.pack(pady=2)
    # ...existing code...
        btn_frame = tk.Frame(self, bg="#f5f6fa")
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Login", width=12, font=("Arial", 11, "bold"), bg="#44bd32", fg="white", command=self.do_login).pack(side='left', padx=8)
        tk.Button(btn_frame, text="Register", width=12, font=("Arial", 11, "bold"), bg="#40739e", fg="white", command=self.do_register).pack(side='left', padx=8)
    # ...existing code...
    def do_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        user_data = login_user(username, password)
        if user_data:
            self.app.username = username
            self.app.user_store = UserStore(username)
            self.app.user_store.load()
            self.app.show_main()
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password.")
    def do_register(self):
        from spfet.constants import PASSWORD_MIN_LEN, USERNAME_PATTERN
        import re
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not re.match(USERNAME_PATTERN, username):
            messagebox.showerror("Register Failed", "Username must contain only letters, numbers, or underscore.")
            return
        if len(password) < PASSWORD_MIN_LEN:
            messagebox.showerror("Register Failed", f"Password must be at least {PASSWORD_MIN_LEN} characters.")
            return
        if register_user(username, password):
            messagebox.showinfo("Register", "User registered. You can now log in.")
        else:
            messagebox.showerror("Register Failed", "Username already exists.")
    # Forget Password feature removed

class MainMenuPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        tk.Label(self, textvariable=app.welcome_var, font=("Arial", 16, "bold"), fg="#192a56", bg="#f5f6fa").pack(pady=18)
        btn_frame = tk.Frame(self, bg="#f5f6fa")
        btn_frame.pack(pady=10)
        button_style = {"width": 22, "font": ("Arial", 12, "bold"), "bg": "#00a8ff", "fg": "white", "bd": 0, "relief": "ridge", "padx": 4, "pady": 4}
        tk.Button(btn_frame, text="Add Transaction", command=app.show_add, **button_style).pack(pady=7)
        tk.Button(btn_frame, text="View Transactions", command=app.show_view, **button_style).pack(pady=7)
        tk.Button(btn_frame, text="Set/View Budgets", command=app.show_budget, **button_style).pack(pady=7)
        tk.Button(btn_frame, text="Show Statistics", command=app.show_stats, **button_style).pack(pady=7)
        tk.Button(btn_frame, text="Export to CSV", command=app.export_csv, **button_style).pack(pady=7)
        cp_style = button_style.copy()
        cp_style["bg"] = "#fbc531"
        tk.Button(btn_frame, text="Change Password", command=app.change_password, **cp_style).pack(pady=7)
        logout_style = button_style.copy()
        logout_style["bg"] = "#e84118"
        tk.Button(btn_frame, text="Logout", command=app.logout, **logout_style).pack(pady=14)

class AddTransactionPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        tk.Label(self, text="Add Transaction", font=("Arial", 14)).pack(pady=10)
        self.amount_var = tk.DoubleVar()
        tk.Label(self, text="Amount:").pack()
        tk.Entry(self, textvariable=self.amount_var).pack()
        tk.Label(self, text="Category:").pack()
        self.cat_var = tk.IntVar()
        categories = sorted(ALLOWED_CATEGORIES)
        for i, cat in enumerate(categories):
            tk.Radiobutton(self, text=cat, variable=self.cat_var, value=i).pack(anchor='w')
        tk.Label(self, text="Type:").pack()
        self.type_var = tk.IntVar()
        ttypes = sorted(TRANSACTION_TYPES)
        for i, ttype in enumerate(ttypes):
            tk.Radiobutton(self, text=ttype, variable=self.type_var, value=i).pack(anchor='w')
        tk.Button(self, text="Add", command=self.add_tx).pack(pady=10)
        tk.Button(self, text="Back", command=app.show_main).pack()
    def add_tx(self):
        amount = self.amount_var.get()
        categories = sorted(ALLOWED_CATEGORIES)
        ttypes = sorted(TRANSACTION_TYPES)
        cat_idx = self.cat_var.get()
        ttype_idx = self.type_var.get()
        if amount <= 0:
            messagebox.showerror("Error", "Amount must be positive.")
            return
        category = categories[cat_idx]
        ttype = ttypes[ttype_idx]
        # Budget check
        if ttype == "expense":
            now = datetime.utcnow()
            month = now.month
            year = now.year
            total = 0.0
            for t in self.app.user_store.data.transactions:
                tdate = t.get("date", "")
                try:
                    dt = datetime.fromisoformat(tdate.replace("Z", ""))
                    if dt.year == year and dt.month == month and t["category"] == category and t["ttype"] == "expense":
                        total += t["amount"]
                except Exception:
                    continue
            new_total = total + amount
            budget = self.app.user_store.data.budgets.get(category, 0.0)
            if budget > 0 and new_total > budget:
                messagebox.showwarning("Budget Exceeded", f"This expense will exceed your budget for {category} ({budget:.2f})!")
        tx = Transaction(amount=amount, category=category, ttype=ttype)
        self.app.user_store.data.transactions.append({
            "amount": tx.amount,
            "category": tx.category,
            "ttype": tx.ttype,
            "date": tx.date
        })
        self.app.user_store.save()
        messagebox.showinfo("Transaction", "Transaction added.")
        self.app.show_main()

class ViewTransactionsPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        tk.Label(self, text="Transactions", font=("Arial", 14)).pack(pady=10)
        self.frame = tk.Frame(self)
        self.frame.pack()
        tk.Button(self, text="Back", command=app.show_main).pack(pady=10)
    def show(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        tk.Label(self.frame, text="Date", width=20, anchor='w').grid(row=0, column=0)
        tk.Label(self.frame, text="Type", width=10, anchor='w').grid(row=0, column=1)
        tk.Label(self.frame, text="Category", width=15, anchor='w').grid(row=0, column=2)
        tk.Label(self.frame, text="Amount", width=10, anchor='e').grid(row=0, column=3)
        for i, t in enumerate(self.app.user_store.data.transactions, 1):
            tk.Label(self.frame, text=t['date'], width=20, anchor='w').grid(row=i, column=0)
            tk.Label(self.frame, text=t['ttype'], width=10, anchor='w').grid(row=i, column=1)
            tk.Label(self.frame, text=t['category'], width=15, anchor='w').grid(row=i, column=2)
            tk.Label(self.frame, text=f"{t['amount']:.2f}", width=10, anchor='e').grid(row=i, column=3)
        super().show()

class BudgetPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        tk.Label(self, text="Set/View Budgets", font=("Arial", 14)).pack(pady=10)
        self.frame = tk.Frame(self)
        self.frame.pack()
        tk.Button(self, text="Back", command=app.show_main).pack(pady=10)
    def show(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        categories = sorted(self.app.user_store.data.budgets)
        for i, cat in enumerate(categories):
            tk.Label(self.frame, text=cat, width=15, anchor='w').grid(row=i, column=0)
            tk.Label(self.frame, text=f"{self.app.user_store.data.budgets[cat]:.2f}", width=10, anchor='e').grid(row=i, column=1)
            def set_budget(cat=cat):
                amount = simpledialog.askfloat("Set Budget", f"Enter new budget for {cat}:", minvalue=0.0)
                if amount is not None and amount >= 0:
                    self.app.user_store.data.budgets[cat] = amount
                    self.app.user_store.save()
                    messagebox.showinfo("Budget", f"Budget for {cat} set to {amount:.2f}")
                    self.show()
            tk.Button(self.frame, text="Set", command=set_budget).grid(row=i, column=2)
        super().show()

class StatsPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        tk.Label(self, text="Statistics", font=("Arial", 14)).pack(pady=10)
        self.frame = tk.Frame(self)
        self.frame.pack()
        tk.Button(self, text="Show Graphs", command=self.show_graphs).pack(pady=5)
        tk.Button(self, text="Back", command=app.show_main).pack(pady=10)
    def show(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        from collections import defaultdict
        # Expense breakdown
        expense_totals = defaultdict(float)
        income_totals = defaultdict(float)
        for t in self.app.user_store.data.transactions:
            if t["ttype"] == "expense":
                expense_totals[t["category"]] += t["amount"]
            elif t["ttype"] == "income":
                income_totals[t["category"]] += t["amount"]
        tk.Label(self.frame, text="Expense Breakdown by Category:", font=("Arial", 12)).grid(row=0, column=0, sticky='w')
        for i, cat in enumerate(sorted(expense_totals)):
            tk.Label(self.frame, text=f"{cat}: {expense_totals[cat]:.2f}").grid(row=i+1, column=0, sticky='w')
        row_offset = len(expense_totals) + 2
        tk.Label(self.frame, text="Income Breakdown by Category:", font=("Arial", 12)).grid(row=row_offset, column=0, sticky='w')
        for i, cat in enumerate(sorted(income_totals)):
            tk.Label(self.frame, text=f"{cat}: {income_totals[cat]:.2f}").grid(row=row_offset+1+i, column=0, sticky='w')
        from datetime import datetime
        expense_month_totals = defaultdict(float)
        income_month_totals = defaultdict(float)
        for t in self.app.user_store.data.transactions:
            try:
                dt = datetime.fromisoformat(t["date"].replace("Z", ""))
                key = f"{dt.year}-{dt.month:02d}"
                if t["ttype"] == "expense":
                    expense_month_totals[key] += t["amount"]
                elif t["ttype"] == "income":
                    income_month_totals[key] += t["amount"]
            except Exception:
                continue
        row_offset2 = row_offset + 1 + len(income_totals) + 1
        tk.Label(self.frame, text="Monthly Spending Trend (expenses):", font=("Arial", 12)).grid(row=row_offset2, column=0, sticky='w')
        for i, m in enumerate(sorted(expense_month_totals)):
            tk.Label(self.frame, text=f"{m}: {expense_month_totals[m]:.2f}").grid(row=row_offset2+1+i, column=0, sticky='w')
        row_offset3 = row_offset2 + 1 + len(expense_month_totals) + 1
        tk.Label(self.frame, text="Monthly Income Trend:", font=("Arial", 12)).grid(row=row_offset3, column=0, sticky='w')
        for i, m in enumerate(sorted(income_month_totals)):
            tk.Label(self.frame, text=f"{m}: {income_month_totals[m]:.2f}").grid(row=row_offset3+1+i, column=0, sticky='w')
        super().show()
    def show_graphs(self):
        from collections import defaultdict
        cat_totals = defaultdict(float)
        for t in self.app.user_store.data.transactions:
            if t["ttype"] == "expense":
                cat_totals[t["category"]] += t["amount"]
        month_totals = defaultdict(float)
        for t in self.app.user_store.data.transactions:
            if t["ttype"] == "expense":
                try:
                    dt = datetime.fromisoformat(t["date"].replace("Z", ""))
                    key = f"{dt.year}-{dt.month:02d}"
                    month_totals[key] += t["amount"]
                except Exception:
                    continue
        if month_totals:
            plt.figure(figsize=(6,4))
            plt.plot(list(month_totals.keys()), list(month_totals.values()), marker='o')
            plt.title('Monthly Spending Trend')
            plt.xlabel('Month')
            plt.ylabel('Expenses')
            plt.tight_layout()
            plt.show()
        if cat_totals:
            plt.figure(figsize=(6,4))
            plt.bar(list(cat_totals.keys()), list(cat_totals.values()))
            plt.title('Expense Breakdown by Category')
            plt.xlabel('Category')
            plt.ylabel('Expenses')
            plt.tight_layout()
            plt.show()

class SPFETApp(tk.Tk):
    def change_password(self):
        from tkinter import simpledialog
        from spfet.constants import PASSWORD_MIN_LEN
        if not self.user_store or not self.user_store.data:
            messagebox.showerror("Change Password", "No user loaded.")
            return
        old_pwd = simpledialog.askstring("Change Password", "Enter current password:", show="*")
        if old_pwd is None:
            return
        from spfet.utils import verify_password
        auth = self.user_store.data.auth
        if not verify_password(old_pwd, auth["salt"], auth["password_hash"], auth.get("iterations", 100_000)):
            messagebox.showerror("Change Password", "Incorrect current password.")
            return
        # Prompt for new password immediately after verifying old password
        new_pwd = simpledialog.askstring("Change Password", "Enter new password:", show="*")
        if not new_pwd:
            messagebox.showerror("Change Password", "Password cannot be empty.")
            return
        if len(new_pwd) < PASSWORD_MIN_LEN:
            messagebox.showerror("Change Password", f"Password must be at least {PASSWORD_MIN_LEN} characters.")
            return
        from spfet.utils import hash_password
        ph, salt, iters = hash_password(new_pwd)
        auth["password_hash"] = ph
        auth["salt"] = salt
        auth["iterations"] = iters
        self.user_store.save()
        messagebox.showinfo("Change Password", "Password changed successfully.")
    def export_csv(self):
        import csv
        from tkinter import filedialog
        if not self.user_store or not self.user_store.data or not self.user_store.data.transactions:
            messagebox.showerror("Export", "No transactions to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Save CSV")
        if not file_path:
            return
        with open(file_path, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Category", "Type", "Amount"])
            for t in self.user_store.data.transactions:
                writer.writerow([t["date"], t["category"], t["ttype"], t["amount"]])
        messagebox.showinfo("Export", f"Transactions exported to {file_path}")
    def __init__(self):
        super().__init__()
        self.title("Smart Personal Finance & Expense Tracker (SPFET)")
        self.geometry("500x500")
        self.username = None
        self.user_store = None
        self.welcome_var = tk.StringVar()
        self.pages = {}
        for PageClass in (LoginPage, MainMenuPage, AddTransactionPage, ViewTransactionsPage, BudgetPage, StatsPage):
            page = PageClass(self, self)
            self.pages[PageClass.__name__] = page
            page.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.show_login()
    def show_login(self):
        self.pages['LoginPage'].show()
    def show_main(self):
        self.welcome_var.set(f"Welcome, {self.username}")
        self.pages['MainMenuPage'].show()
    def show_add(self):
        self.pages['AddTransactionPage'].show()
    def show_view(self):
        self.pages['ViewTransactionsPage'].show()
    def show_budget(self):
        self.pages['BudgetPage'].show()
    def show_stats(self):
        self.pages['StatsPage'].show()
    def logout(self):
        if self.user_store:
            self.user_store.save()
        self.username = None
        self.user_store = None
        self.show_login()

if __name__ == "__main__":
    app = SPFETApp()
    app.mainloop()
