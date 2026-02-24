from tkinter import *
from tkinter import messagebox
import sqlite3
import hashlib

root = Tk()
root.title("Login & Register")
root.geometry("800x500")
root.configure(bg="#f0f0f0")
root.resizable(False, False)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("userAuthUI.db")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    email TEXT PRIMARY KEY,
    password TEXT,
    role TEXT
)
""")
conn.commit()

# ---------------- HASH FUNCTION ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------- PAGE SWITCHING ----------------
def show_frame(frame):
    login_frame.pack_forget()
    register_frame.pack_forget()
    forgot_frame.pack_forget()
    frame.pack(pady=60)

# ---------------- LOGIN FUNCTION ----------------
def login():
    if not login_email.get() or not login_password.get():
        messagebox.showwarning("Error", "All fields are required")
        return

    cur.execute("SELECT * FROM users WHERE email=?", (login_email.get(),))
    record = cur.fetchone()

    if record and hash_password(login_password.get()) == record[1]:
        messagebox.showinfo("Success", f"Login successful as {record[2]}")
    else:
        messagebox.showerror("Error", "Invalid credentials")

# ---------------- REGISTER FUNCTION ----------------
def register():
    if not reg_email.get() or not reg_password.get() or not role_var.get():
        messagebox.showwarning("Error", "All fields are required")
        return

    try:
        cur.execute("INSERT INTO users VALUES(?,?,?)",
                    (reg_email.get(), hash_password(reg_password.get()), role_var.get()))
        conn.commit()
        messagebox.showinfo("Success", "Registered Successfully")
        show_frame(login_frame)
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Email already exists")

# ---------------- FORGOT PASSWORD FUNCTION ----------------
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
        messagebox.showinfo("Success", "Password Updated Successfully")
        show_frame(login_frame)
    else:
        messagebox.showerror("Error", "Email not found")

# ---------------- UI DESIGN --------------

# ---------------- LOGIN FRAME ----------------
login_frame = Frame(root, bg="white", width=400, height=380)
login_frame.pack(pady=60)

Label(login_frame, text="Login", font=("Arial", 22, "bold"), bg="white").pack(pady=(20,5))
Label(login_frame, text="to solve doubt", fg="gray", bg="white").pack(pady=(0,20))

Label(login_frame, text="Email", bg="white").pack()
login_email = Entry(login_frame, width=30, bd=2, relief="groove")
login_email.pack(pady=5)

Label(login_frame, text="Password", bg="white").pack()
login_password = Entry(login_frame, width=30, show="*", bd=2, relief="groove")
login_password.pack(pady=5)

Button(login_frame, text="Login", width=25, bg="#00bcd4", fg="white",
       font=("Arial",10,"bold"), command=login).pack(pady=15)

# Forgot Password clickable label
forgot_lbl = Label(login_frame, text="Forgot Password?",
                   fg="blue", bg="white", cursor="hand2")
forgot_lbl.pack()
forgot_lbl.bind("<Button-1>", lambda e: show_frame(forgot_frame))

# Register clickable label
register_lbl = Label(login_frame,
                     text="Don't have an account? Register",
                     fg="orange", bg="white", cursor="hand2")
register_lbl.pack(pady=10)
register_lbl.bind("<Button-1>", lambda e: show_frame(register_frame))


# ---------------- REGISTER FRAME ----------------
register_frame = Frame(root, bg="white", width=400, height=420)

Label(register_frame, text="Register", font=("Arial", 22, "bold"), bg="white").pack(pady=(20,5))
Label(register_frame, text="to solve doubt", fg="gray", bg="white").pack(pady=(0,20))

Label(register_frame, text="Email", bg="white").pack()
reg_email = Entry(register_frame, width=30, bd=2, relief="groove")
reg_email.pack(pady=5)

Label(register_frame, text="Password", bg="white").pack()
reg_password = Entry(register_frame, width=30, show="*", bd=2, relief="groove")
reg_password.pack(pady=5)

role_var = StringVar()

Radiobutton(register_frame, text="Student", variable=role_var,
            value="Student", bg="white").pack()
Radiobutton(register_frame, text="Teacher", variable=role_var,
            value="Teacher", bg="white").pack()

Button(register_frame, text="Register", width=25, bg="#00bcd4",
       fg="white", font=("Arial",10,"bold"),
       command=register).pack(pady=15)

# Back to login clickable
back_login_lbl = Label(register_frame,
                       text="Already have account? Login",
                       fg="blue", bg="white", cursor="hand2")
back_login_lbl.pack()
back_login_lbl.bind("<Button-1>", lambda e: show_frame(login_frame))


# ---------------- FORGOT FRAME ----------------
forgot_frame = Frame(root, bg="white", width=400, height=380)

Label(forgot_frame, text="Forgot Password",
      font=("Arial", 22, "bold"), bg="white").pack(pady=(20,5))
Label(forgot_frame, text="Reset your password",
      fg="gray", bg="white").pack(pady=(0,20))

Label(forgot_frame, text="Email", bg="white").pack()
forgot_email = Entry(forgot_frame, width=30, bd=2, relief="groove")
forgot_email.pack(pady=5)

Label(forgot_frame, text="New Password", bg="white").pack()
new_password = Entry(forgot_frame, width=30, show="*", bd=2, relief="groove")
new_password.pack(pady=5)

Button(forgot_frame, text="Submit", width=25, bg="#00bcd4",
       fg="white", font=("Arial",10,"bold"),
       command=reset_password).pack(pady=15)

# Back to login clickable
forgot_back_lbl = Label(forgot_frame,
                        text="Back to Login",
                        fg="blue", bg="white", cursor="hand2")
forgot_back_lbl.pack()
forgot_back_lbl.bind("<Button-1>", lambda e: show_frame(login_frame))

# Show login first
show_frame(login_frame)

root.mainloop()
conn.close()