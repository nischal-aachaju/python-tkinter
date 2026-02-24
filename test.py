from tkinter import *
from tkinter import messagebox
import sqlite3
import hashlib

root = Tk()
root.title("Login & Register")
root.geometry("800x520")
root.configure(bg="#f0f0f0")
root.resizable(False, False)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("userAuthUI.db")
cur = conn.cursor()

# Always create table with 4 columns
cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT,
    email TEXT PRIMARY KEY,
    password TEXT,
    role TEXT
)
""")

# Check if role column exists (for old database)
cur.execute("PRAGMA table_info(users)")
columns = [col[1] for col in cur.fetchall()]

if "role" not in columns:
    cur.execute("ALTER TABLE users ADD COLUMN role TEXT")

conn.commit()

# ---------------- HASH FUNCTION ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------- PAGE SWITCH ----------------
def show_frame(frame):
    login_email.delete(0, END)
    login_password.delete(0, END)
    reg_username.delete(0, END)
    reg_email.delete(0, END)
    reg_password.delete(0, END)
    forgot_email.delete(0, END)
    new_password.delete(0, END)

    if frame == register_frame:
        role_var.set(None)

    login_frame.pack_forget()
    register_frame.pack_forget()
    forgot_frame.pack_forget()
    frame.pack(pady=30)

# ---------------- LOGIN ----------------
def login():
    if not login_email.get() or not login_password.get():
        messagebox.showwarning("Error", "All fields required")
        return

    cur.execute("SELECT * FROM users WHERE email=?", (login_email.get(),))
    record = cur.fetchone()

    if record and hash_password(login_password.get()) == record[2]:
        messagebox.showinfo("Success", f"Welcome {record[0]} ({record[3]})")
    else:
        messagebox.showerror("Error", "Invalid credentials")

# ---------------- REGISTER ----------------
def register():
    if not reg_username.get() or not reg_email.get() or not reg_password.get() or not role_var.get():
        messagebox.showwarning("Error", "All fields required")
        return

    try:
        cur.execute("""
        INSERT INTO users (username, email, password, role)
        VALUES (?, ?, ?, ?)
        """, (
            reg_username.get(),
            reg_email.get(),
            hash_password(reg_password.get()),
            role_var.get()
        ))

        conn.commit()
        messagebox.showinfo("Success", "Registered Successfully")
        show_frame(login_frame)

    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Email already exists")

# ---------------- RESET PASSWORD ----------------
def reset_password():
    if not forgot_email.get() or not new_password.get():
        messagebox.showwarning("Error", "All fields required")
        return

    cur.execute("SELECT * FROM users WHERE email=?", (forgot_email.get(),))
    record = cur.fetchone()

    if record:
        cur.execute("UPDATE users SET password=? WHERE email=?",
                    (hash_password(new_password.get()), forgot_email.get()))
        conn.commit()
        messagebox.showinfo("Success", "Password Updated")
        show_frame(login_frame)
    else:
        messagebox.showerror("Error", "Email not found")

# ================= UI =================
ENTRY_WIDTH = 30
ENTRY_IPADY = 4
BUTTON_WIDTH = 20
BUTTON_HEIGHT = 1

# ---------------- LOGIN FRAME ----------------
login_frame = Frame(root, bg="white", width=420, height=500)
login_frame.pack_propagate(False)

Label(login_frame, text="Login", font=("Arial", 22, "bold"), bg="white").pack(pady=(30,5))
Label(login_frame, text="to solve doubt", fg="gray", bg="white").pack(pady=(0,25))

Label(login_frame, text="Email", bg="white").pack()
login_email = Entry(login_frame, width=ENTRY_WIDTH, font=("Arial",12))
login_email.pack(pady=6, ipady=ENTRY_IPADY)

Label(login_frame, text="Password", bg="white").pack()
login_password = Entry(login_frame, width=ENTRY_WIDTH, font=("Arial",12), show="*")
login_password.pack(pady=6, ipady=ENTRY_IPADY)

Button(login_frame, text="Login",
       bg="#00bcd4", fg="white",
       font=("Arial",11,"bold"),
       height=BUTTON_HEIGHT, width=BUTTON_WIDTH,
       command=login).pack(pady=20)

forgot_lbl = Label(login_frame, text="Forgot Password?",
                   fg="blue", bg="white", cursor="hand2")
forgot_lbl.pack()
forgot_lbl.bind("<Button-1>", lambda e: show_frame(forgot_frame))

register_lbl = Label(login_frame,
                     text="Don't have an account? Register",
                     fg="orange", bg="white", cursor="hand2")
register_lbl.pack(pady=10)
register_lbl.bind("<Button-1>", lambda e: show_frame(register_frame))

# ---------------- REGISTER FRAME ----------------
register_frame = Frame(root, bg="white", width=420, height=560)
register_frame.pack_propagate(False)

Label(register_frame, text="Register", font=("Arial", 22, "bold"), bg="white").pack(pady=(30,5))
Label(register_frame, text="to solve doubt", fg="gray", bg="white").pack(pady=(0,25))

Label(register_frame, text="Username", bg="white").pack()
reg_username = Entry(register_frame, width=ENTRY_WIDTH, font=("Arial",12))
reg_username.pack(pady=6, ipady=ENTRY_IPADY)

Label(register_frame, text="Email", bg="white").pack()
reg_email = Entry(register_frame, width=ENTRY_WIDTH, font=("Arial",12))
reg_email.pack(pady=6, ipady=ENTRY_IPADY)

Label(register_frame, text="Password", bg="white").pack()
reg_password = Entry(register_frame, width=ENTRY_WIDTH, font=("Arial",12), show="*")
reg_password.pack(pady=6, ipady=ENTRY_IPADY)

role_var = StringVar()
role_frame = Frame(register_frame, bg="white")
role_frame.pack(pady=10)

Radiobutton(role_frame, text="Student", variable=role_var,
            value="Student", bg="white").pack(side=LEFT, padx=20)

Radiobutton(role_frame, text="Teacher", variable=role_var,
            value="Teacher", bg="white").pack(side=LEFT, padx=20)

Button(register_frame, text="Register",
       bg="#00bcd4", fg="white",
       font=("Arial",11,"bold"),
       height=BUTTON_HEIGHT, width=BUTTON_WIDTH,
       command=register).pack(pady=12)

back_login_lbl = Label(register_frame,
                       text="Already have an account? Login",
                       fg="blue", bg="white",
                       cursor="hand2", font=("Arial",10,"underline"))
back_login_lbl.pack(pady=6)
back_login_lbl.bind("<Button-1>", lambda e: show_frame(login_frame))

# ---------------- FORGOT FRAME ----------------
forgot_frame = Frame(root, bg="white", width=420, height=500)
forgot_frame.pack_propagate(False)

Label(forgot_frame, text="Forgot Password",
      font=("Arial", 22, "bold"), bg="white").pack(pady=(30,5))
Label(forgot_frame, text="Reset your password",
      fg="gray", bg="white").pack(pady=(0,25))

Label(forgot_frame, text="Email", bg="white").pack()
forgot_email = Entry(forgot_frame, width=ENTRY_WIDTH, font=("Arial",12))
forgot_email.pack(pady=6, ipady=ENTRY_IPADY)

Label(forgot_frame, text="New Password", bg="white").pack()
new_password = Entry(forgot_frame, width=ENTRY_WIDTH, font=("Arial",12), show="*")
new_password.pack(pady=6, ipady=ENTRY_IPADY)

Button(forgot_frame, text="Submit",
       bg="#00bcd4", fg="white",
       font=("Arial",10,"bold"),
       height=BUTTON_HEIGHT, width=BUTTON_WIDTH,
       command=reset_password).pack(pady=20)

forgot_back_lbl = Label(forgot_frame,
                        text="Back to Login",
                        fg="blue", bg="white", cursor="hand2")
forgot_back_lbl.pack()
forgot_back_lbl.bind("<Button-1>", lambda e: show_frame(login_frame))

# ---------------- SHOW LOGIN FIRST ----------------
show_frame(login_frame)

root.mainloop()
conn.close()