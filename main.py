from tkinter import *
import sqlite3
from PIL import Image, ImageTk
from tkinter import messagebox
import hashlib
#----------database-----------------
conn=sqlite3.connect("cdrs.db")
cur=conn.cursor()

root =Tk()
root.geometry("800x600")
root.resizable(0,0)
root.iconbitmap('assects/logo.ico')

def login():
    login_root = Toplevel(root)
    login_root.geometry("800x650")
    login_root.resizable(0, 0)
    login_root.title("Login")
    root.withdraw()
    # ---------------- DATABASE ----------------
    conn = sqlite3.connect("userAuthUI.db")
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        email TEXT PRIMARY KEY,
        password TEXT,
        name TEXT,
        role TEXT
    )
    """)
    
    # cur.execute('''
    #         DELETE FROM users       
    #         ''')


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
            login_password.delete(0, END)
            login_email.delete(0, END)
            messagebox.showinfo("Success", f"Login successful as {record[2]}")
            conn.close()
        else:
            messagebox.showerror("Error", "Invalid credentials")
            login_password.delete(0, END)

    # ---------------- REGISTER FUNCTION ----------------
    def register():
        if not reg_email.get() or not reg_password.get() or not role_var.get():
            messagebox.showwarning("Error", "All fields are required")
            return

        try:
            cur.execute("INSERT INTO users VALUES(?,?,?,?,?)",
                        (reg_email.get(), hash_password(reg_password.get()), reg_name.get(), role_var.get()))
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
    login_frame = Frame(login_root, bg="white", width=500, height=480)
    login_frame.pack_propagate(False)
    login_frame.pack(pady=60)

    #-------------------login text----------------------
    Label(login_frame, text="Login", font=("Arial", 24, "bold"), bg="white").pack(pady=(20,5))
    Label(login_frame, text="to solve doubt", fg="gray", bg="white").pack(pady=(0,20))

    # user email
    Label(login_frame, text="Email", bg="white",font=("Arial", 16)).place(x=50,y=120)
    login_email = Entry(login_frame, width=30,bd=2, relief="groove",font=("Arial", 16))
    login_email.place(x=50,y=155)

    # user password
    Label(login_frame, text="Password", bg="white",font=("Arial", 16)).place(x=50,y=210)
    login_password = Entry(login_frame, width=30, show="*", bd=2, relief="groove",font=("Arial", 16))
    login_password.place(x=50,y=245)

    # login button
    Button(login_frame, text="Login", width=27, bg="#00bcd4", fg="white",   
        font=("Arial",16,"bold"), command=login).place(x=50,y=300)
    #-------------------Forgot Password Frame-------------------
    # Forgot Password clickable label
    forgot_lbl = Label(login_frame, text="Forgot Password?",
                    fg="blue", bg="white", cursor="hand2",font=("Arial", 10))
    forgot_lbl.place(x=175,y=350)
    forgot_lbl.bind("<Button-1>", lambda e: show_frame(forgot_frame))

    # Register clickable label
    register_lbl = Label(login_frame,
                        text="Don't have an account? Register",
                        fg="#EB310C", bg="white", cursor="hand2",font=("",12))
    register_lbl.place(x=50,y=390)
    register_lbl.bind("<Button-1>", lambda e: show_frame(register_frame))


    # ---------------- REGISTER FRAME ----------------
    register_frame = Frame(login_root, bg="white", width=500, height=480)

    Label(register_frame, text="Register", font=("Arial", 22, "bold"), bg="white").place(x=50,y=20)     
    Label(register_frame, text="to solve doubt", fg="gray", bg="white").place(x=50,y=60)


    Label(register_frame, text="User Name", bg="white").place(x=50,y=120)
    reg_name = Entry(register_frame, width=30, bd=2, relief="groove")
    reg_name.place(x=50,y=155)

    Label(register_frame, text="Email", bg="white").place(x=50,y=210)
    reg_email = Entry(register_frame, width=30, bd=2, relief="groove")
    reg_email.place(x=50,y=245)

    Label(register_frame, text="Password", bg="white").place(x=50,y=290)
    reg_password = Entry(register_frame, width=30, show="*", bd=2, relief="groove")
    reg_password.place(x=50,y=325)  

    role_var = StringVar()

    Radiobutton(register_frame, text="Student", variable=role_var,
                value="Student", bg="white").place(x=50,y=370)
    Radiobutton(register_frame, text="Teacher", variable=role_var,
                value="Teacher", bg="white").place(x=50,y=335)
    role_var.set(0)
    Button(register_frame, text="Register", width=25, bg="#00bcd4",
        fg="white", font=("Arial",10,"bold"),
        command=register).place(x=50,y=390)

    # Back to login clickable
    back_login_lbl = Label(register_frame,
                        text="Already have account? Login",
                        fg="blue", bg="white", cursor="hand2")
    back_login_lbl.place(x=50,y=440)
    back_login_lbl.bind("<Button-1>", lambda e: show_frame(login_frame))


    # ---------------- FORGOT FRAME ----------------
    forgot_frame = Frame(login_root, bg="white", width=500, height=480)

    Label(forgot_frame, text="Forgot Password",
        font=("Arial", 22, "bold"), bg="white").place(x=50,y=20)
    Label(forgot_frame, text="Reset your password",
        fg="gray", bg="white").place(x=50,y=120)

    Label(forgot_frame, text="Email", bg="white").place(x=50,y=220)
    forgot_email = Entry(forgot_frame, width=30, bd=2, relief="groove")
    forgot_email.place(x=50,y=255)

    Label(forgot_frame, text="New Password", bg="white").place(x=50,y=320)
    new_password = Entry(forgot_frame, width=30, show="*", bd=2, relief="groove")
    new_password.place(x=50,y=355)

    Button(forgot_frame, text="Submit", width=25, bg="#00bcd4",
        fg="white", font=("Arial",10,"bold"),
        command=reset_password).place(x=50,y=400)

    # Back to login clickable 
    forgot_back_lbl = Label(forgot_frame,
                            text="Back to Login",
                            fg="blue", bg="white", cursor="hand2")
    forgot_back_lbl.place(x=50,y=450)
    forgot_back_lbl.bind("<Button-1>", lambda e: show_frame(login_frame))

    # Show login first
    show_frame(login_frame)
    
    def new_window():
        login_root.destroy()
        root.deiconify() 

    login_root.protocol("WM_DELETE_WINDOW", new_window)


button=Button(root,text="Login",command=login)
button.pack()

root.mainloop()

