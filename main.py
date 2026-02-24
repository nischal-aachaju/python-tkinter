from cProfile import label
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

def login_page():
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
        name TEXT,
        password TEXT,
        role TEXT
    )
    """)
    # to delete all table data
    # cur.execute("DELETE FROM users")


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


        if record and hash_password(login_password.get()) == record[2]:
            login_password.delete(0, END)
            login_email.delete(0, END)
            
            login_root.destroy()
            conn.close()
            if record[3] == "Student":
                student_page(record[1])
            elif record[3] == "Teacher":
                teacher_page(record[1])
            
        
        else:
            messagebox.showerror("Error", "Invalid credentials")
            login_password.delete(0, END)


    # ---------------- REGISTER FUNCTION ----------------
    def register():
        if not reg_email.get() or not reg_password.get() or not role_var.get():
            messagebox.showwarning("Error", "All fields are required")
            return

        try:
            cur.execute("INSERT INTO users VALUES(?,?,?,?)",
                        (reg_email.get(),reg_name.get(), hash_password(reg_password.get()),  role_var.get()))
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
            new_password.delete(0, END)
            forgot_email.delete(0, END)
            show_frame(login_frame)
        else:
            messagebox.showerror("Error", "Email not found")
            new_password.delete(0, END)
            forgot_email.delete(0, END)
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

    Label(register_frame, text="Register", font=("Arial", 24, "bold"), bg="white").place(x=180,y=20)     
    Label(register_frame, text="to solve doubt", fg="gray", bg="white").place(x=200,y=65)


    Label(register_frame, text="User Name", bg="white",font=("Arial", 16)).place(x=50,y=110)
    reg_name = Entry(register_frame, width=30, bd=2, relief="groove",font=("Arial", 16))
    reg_name.place(x=50,y=145)

    Label(register_frame, text="Email", bg="white",font=("Arial", 16)).place(x=50,y=190)
    reg_email = Entry(register_frame, width=30, bd=2, relief="groove",font=("Arial", 16))
    reg_email.place(x=50,y=225)

    Label(register_frame, text="Password", bg="white",font=("Arial", 16)).place(x=50,y=270)
    reg_password = Entry(register_frame, width=30, show="*", bd=2, relief="groove",font=("Arial", 16))
    reg_password.place(x=50,y=305)  

    role_var = StringVar()

    Radiobutton(register_frame, text="Student", variable=role_var,
                value="Student", bg="white").place(x=50,y=365)
    Radiobutton(register_frame, text="Teacher", variable=role_var,
                value="Teacher", bg="white").place(x=50,y=340)
    role_var.set(0)
    Button(register_frame, text="Register", width=27, bg="#00bcd4",
        fg="white", font=("Arial",16,"bold"),
        command=register).place(x=50,y=400)

    # Back to login clickable
    back_login_lbl = Label(register_frame,
                        text="Already have account? Login",
                        fg="blue", bg="white", cursor="hand2")
    back_login_lbl.place(x=50,y=445)
    back_login_lbl.bind("<Button-1>", lambda e: show_frame(login_frame))


    # ---------------- FORGOT FRAME ----------------
    forgot_frame = Frame(login_root, bg="white", width=500, height=480)

    Label(forgot_frame, text="Forgot Password",
        font=("Arial", 22, "bold"), bg="white").place(x=135,y=40)
    Label(forgot_frame, text="Reset your password",
        fg="gray", bg="white").place(x=190,y=80)

    Label(forgot_frame, text="Email", bg="white",font=("Arial", 16)).place(x=50,y=140)
    forgot_email = Entry(forgot_frame, width=30, bd=2, relief="groove",font=("Arial", 16))
    forgot_email.place(x=50,y=175)
    

    Label(forgot_frame, text="New Password", bg="white",font=("Arial", 16)).place(x=50,y=225)
    new_password = Entry(forgot_frame, width=30, show="*", bd=2, relief="groove",font=("Arial", 16))
    new_password.place(x=50,y=255)

    Button(forgot_frame, text="Submit", width=27, bg="#00bcd4",
        fg="white", font=("Arial",16,"bold"),
        command=reset_password).place(x=50,y=310)


    # Back to login clickable 
    forgot_back_lbl = Label(forgot_frame,
                            text="Back to Login",
                            fg="blue", bg="white", cursor="hand2")
    forgot_back_lbl.place(x=195,y=360)
    forgot_back_lbl.bind("<Button-1>", lambda e: show_frame(login_frame))

    # Show login first
    show_frame(login_frame)
    
    def new_window():
        login_root.destroy()
        root.deiconify() 
    login_root.protocol("WM_DELETE_WINDOW", new_window)

def Navbar(root,username):
    #-------------------navbar----------------------
    nav_frame=Frame(root,bg="#23cff2",height=80)
    nav_frame.pack(fill=X)

    #-------------------logo----------------------
    image_logo=Image.open("assects/logo.png")
    image_logo=image_logo.resize((80,80))
    image_logoTk=ImageTk.PhotoImage(image_logo)
    lbl_logo=Label(nav_frame,image=image_logoTk,bd=0)
    lbl_logo.image = image_logoTk
    lbl_logo.place(x=10,y=0)

    #-------------------logo text----------------------
    image_text=Image.open("assects/logo_text.png")
    image_text=image_text.resize((150,50))
    image_textTk=ImageTk.PhotoImage(image_text)
    text_logo=Label(nav_frame,image=image_textTk,bd=0)
    text_logo.image = image_textTk
    text_logo.place(x=100,y=15)

    #-------------------profile image----------------------
    image_profile=Image.open("assects/main_profile.png")
    image_profile=image_profile.resize((60,60))
    image_profileTk=ImageTk.PhotoImage(image_profile)
    profile_logo=Label(nav_frame,image=image_profileTk,bd=0)
    profile_logo.image = image_profileTk
    profile_logo.place(x=720,y=10)

    #-------------------profile text----------------------
    text_profile=Label(nav_frame,text=username+";",font=("Arial",20),bg="#23cff2",fg="black",bd=0)
    text_profile.place(x=630,y=25)


def student_page(name):
    student_root = Toplevel(root)
    student_root.geometry("800x650")
    student_root.resizable(0, 0)
    student_root.title("Student")
    root.withdraw()
    Navbar(student_root,name)


    # Label(student_root,text="Student Dashboard",font=("Arial",24,"bold"),bg="white").pack()
    def new_window():
        student_root.destroy()
        root.deiconify() 

    student_root.protocol("WM_DELETE_WINDOW", new_window)

def teacher_page(name):
    teacher_root = Toplevel(root)
    teacher_root.geometry("800x650")
    teacher_root.resizable(0, 0)
    teacher_root.title("Teacher")
    root.withdraw()
    Navbar(teacher_root,name)

    # Label(teacher_root,text="Teacher Dashboard",font=("Arial",24,"bold"),bg="white").pack()
    def new_window():
        teacher_root.destroy()
        root.deiconify() 

    teacher_root.protocol("WM_DELETE_WINDOW", new_window)
    
image_bg = Image.open("assects/dashboard.jpg")
resize_bg =image_bg.resize((800, 600))
final_bg = ImageTk.PhotoImage(resize_bg)

lbl = Label(root, image=final_bg)
lbl.image = final_bg 
lbl.pack()

button = Label(root,
                    text="Login",
                    fg="white",bg="#00bcd4", cursor="hand2",font=("Arial",16,"bold"))
button.place(x=370,y=390)
button.bind("<Button-1>", lambda e: login_page())

root.mainloop()