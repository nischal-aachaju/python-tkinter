from tkinter import *
import sqlite3
from PIL import Image, ImageTk
from tkinter import messagebox
import hashlib
#----------database-----------------
conn=sqlite3.connect("cdrs.db")
cur=conn.cursor()

root=Tk()
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
        role TEXT,
        security_password TEXT
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
        if reg_password.get() != reg_con_password.get():
            messagebox.showwarning("Error", "Passwords do not match")
            return
        if not reg_email.get() or not reg_password.get() or not role_var.get() or not security_password.get():
            messagebox.showwarning("Error", "All fields are required")
            return 

        try:
            cur.execute("INSERT INTO users VALUES(?,?,?,?,?)",
                        (reg_email.get(),reg_name.get(), hash_password(reg_password.get()),  role_var.get(),security_password.get()))
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

        if not forgot_security_password.get():
            messagebox.showwarning("Error", "Security Password required")
            return
        if forgot_security_password.get() != record[4]:
            messagebox.showerror("Error", "Security Password not matched")
            return
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

    Label(register_frame, text="Register", font=("Arial", 24, "bold"), bg="white").place(x=180,y=18)     
    Label(register_frame, text="to solve doubt", fg="gray", bg="white").place(x=200,y=60)


    Label(register_frame, text="User Name", bg="white",font=("Arial", 16)).place(x=50,y=90)
    reg_name = Entry(register_frame, width=30, bd=2, relief="groove",font=("Arial", 16))
    reg_name.place(x=50,y=120)

    Label(register_frame, text="Email", bg="white",font=("Arial", 16)).place(x=50,y=155)
    reg_email = Entry(register_frame, width=30, bd=2, relief="groove",font=("Arial", 16))
    reg_email.place(x=50,y=185)

    Label(register_frame, text="Password", bg="white",font=("Arial", 16)).place(x=50,y=215)
    reg_password = Entry(register_frame, width=30, show="*", bd=2, relief="groove",font=("Arial", 16))
    reg_password.place(x=50,y=245)  

    Label(register_frame, text="Confirm Password", bg="white",font=("Arial", 16)).place(x=50,y=275)
    reg_con_password = Entry(register_frame, width=30, show="*", bd=2, relief="groove",font=("Arial", 16))
    reg_con_password.place(x=50,y=305) 

    Label(register_frame, text="Security Password:", bg="white",font=("Arial", 10)).place(x=130,y=355)
    Label(register_frame, text="favouraite pet name?", bg="white",font=("Arial", 10)).place(x=255,y=335)
    security_password = Entry(register_frame, width=20,bd=2, relief="groove",font=("Arial", 10))
    security_password.place(x=250,y=355)

    role_var = StringVar()

    Radiobutton(register_frame, text="Student", variable=role_var,
                value="Student", bg="white").place(x=50,y=335)
    Radiobutton(register_frame, text="Teacher", variable=role_var,
                value="Teacher", bg="white").place(x=50,y=355)
    role_var.set("Student")
    Button(register_frame, text="Register", width=27, bg="#00bcd4",
        fg="white", font=("Arial",16,"bold"),
        command=register).place(x=50,y=380)

    # Back to login clickable
    back_login_lbl = Label(register_frame,
                        text="Already have account? Login",
                        fg="#0000FF", bg="white", cursor="hand2",font=("arial",13))
    back_login_lbl.place(x=50,y=430)
    back_login_lbl.bind("<Button-1>", lambda e: show_frame(login_frame))


    # ---------------- FORGOT FRAME ----------------
    forgot_frame = Frame(login_root, bg="white", width=500, height=480)

    Label(forgot_frame, text="Forgot Password",
        font=("Arial", 22, "bold"), bg="white").place(x=135,y=40)
    Label(forgot_frame, text="Reset your password",
        fg="gray", bg="white").place(x=190,y=80)

    Label(forgot_frame, text="Email", bg="white",font=("Arial", 16)).place(x=50,y=135)
    forgot_email = Entry(forgot_frame, width=30, bd=2, relief="groove",font=("Arial", 16))
    forgot_email.place(x=50,y=170)
    

    Label(forgot_frame, text="New Password", bg="white",font=("Arial", 16)).place(x=50,y=220)
    new_password = Entry(forgot_frame, width=30, show="*", bd=2, relief="groove",font=("Arial", 16))
    new_password.place(x=50,y=250)

    Label(forgot_frame, text="Security Password:", bg="white",font=("Arial", 16)).place(x=50,y=305)
    forgot_security_password = Entry(forgot_frame, width=30,show="*",bd=2, relief="groove",font=("Arial", 16))
    forgot_security_password.place(x=50,y=335)


    Button(forgot_frame, text="Submit", width=27, bg="#00bcd4",
        fg="white", font=("Arial",16,"bold"),
        command=reset_password).place(x=50,y=380)


    # Back to login clickable 
    forgot_back_lbl = Label(forgot_frame,
                            text="Back to Login",
                            fg="blue", bg="white", cursor="hand2",font=("Arial", 10))
    forgot_back_lbl.place(x=195,y=430)
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
    profile_logo.bind("<Button-1>", lambda e: profile_page(username)) # profile
    profile_logo.place(x=680,y=10)

    #-------------------profile text----------------------
    text_profile=Label(nav_frame,text=username+";",font=("Arial",20),bg="#23cff2",fg="black",bd=0)
    text_profile.place(x=580,y=25)

    #-------------------logout button----------------------
    image_logout=Image.open("assects/logout.png")
    image_logout=image_logout.resize((40,40))
    image_logoutTk=ImageTk.PhotoImage(image_logout)
    logout_logo=Label(nav_frame,image=image_logoutTk,bd=0)
    logout_logo.image = image_logoutTk
    logout_logo.place(x=750,y=20)
    logout_logo.bind("<Button-1>", lambda e: new_window())

    def new_window():
        root.destroy()
        login_page()

def name_logo(frame):
    avtar_image=Image.open("assects/question.png")
    avtar_image=avtar_image.resize((20,20))
    avtar_imageTk=ImageTk.PhotoImage(avtar_image)
    lbl_logo=Label(frame,image=avtar_imageTk,bd=0)
    lbl_logo.image = avtar_imageTk
    lbl_logo.place(x=28,y=10)

def student_content(root, name, parent):  # add name, parent
    frame=Frame(root,bg="#E1E9E5",width=750,height=150,bd=2,relief="groove")
    frame.pack_propagate(False)
    frame.pack(pady=10)
    name_logo(frame)

    Label(frame,text="Nischal",font=("Arial",12,"bold"),bg="#E1E9E5").place(x=50,y=10)
    Label(frame,text="Topic: "+"Use of pack_propogate()",font=("Arial",10,"bold"),bg="#E1E9E5").place(x=25,y=40)
    Label(frame,text="loram hello world If you don't use this line, the frame will shrink\n or expand to perfectlyfit whatever buttons or labels you"+" ......",
            font=("Arial",10), bg="#E1E9E5", justify="left").place(x=25,y=60)

    Volunteer = Label(frame, text="Volunteer", bd=2, relief="groove",
                    fg="white", bg="#23cff2", cursor="hand2", font=("Arial",12,"bold"), padx=5, pady=2)
    Volunteer.place(x=30,y=110)
    Volunteer.bind("<Button-1>", lambda e: login_page())

    Teacher = Label(frame, text="Teacher_name", bd=2, relief="groove",
                    fg="white", bg="#23cff2", cursor="hand2", font=("Arial",12,"bold"), padx=5, pady=2)
    Teacher.place(x=130,y=110)
    Teacher.bind("<Button-1>", lambda e: login_page())

    frame2=Frame(frame,bg="#E1E9E5",width=200,height=145)
    frame2.place(x=545,y=0) 
    Label(frame2,text="👨🏽‍🎓"+"Enrolled Students",font=("Arial",12,),bg="#E1E9E5").place(x=10,y=10)
    Label(frame2,text="• "+"Name1",font=("Arial",10,),bg="#E1E9E5").place(x=30,y=30)
    Label(frame2,text="• "+"Name2",font=("Arial",10,),bg="#E1E9E5").place(x=30,y=50)
    Label(frame2,text="• "+"Name3",font=("Arial",10,),bg="#E1E9E5").place(x=30,y=70)
    Label(frame2,text="• "+"Name4",font=("Arial",10,),bg="#E1E9E5").place(x=30,y=90)

    Enroll = Label(frame2, text="Enroll Now", fg="white", bg="#23cff2", cursor="hand2",
                    font=("Arial",12,"bold"), padx=5, pady=2, bd=2, relief="groove")
    Enroll.place(x=30,y=115)
    Enroll.bind("<Button-1>", lambda e: joining_page(parent, name))  

def teacher_content(root, name, parent):  # add parent
    frame=Frame(root,bg="#E1E9E5",width=750,height=150,bd=2,relief="groove")
    frame.pack_propagate(False)
    frame.pack(pady=10)
    name_logo(frame)
    Label(frame,text="Nischal",font=("Arial",12,"bold"),bg="#E1E9E5").place(x=50,y=10)
    Label(frame,text="Topic: "+"Use of pack_propogate()",font=("Arial",10,"bold"),bg="#E1E9E5").place(x=25,y=40)
    Label(frame,text="loram hello world If you don't use this line, the frame will shrink\n or expand to perfectlyfit whatever buttons or labels you"+" ......",
            font=("Arial",10), bg="#E1E9E5", justify="left").place(x=25,y=60)

    Volunteer = Label(frame, text="Volunteer _name", bd=2, relief="groove",
                    fg="white", bg="#23cff2", cursor="hand2", font=("Arial",12,"bold"), padx=5, pady=2)
    Volunteer.place(x=30,y=110)
    Volunteer.bind("<Button-1>", lambda e: joining_page(parent, name)) 

    frame2=Frame(frame,bg="#E1E9E5",width=200,height=145)
    frame2.place(x=545,y=0) 
    Label(frame2,text="👨🏽‍🎓"+"Enrolled Students",font=("Arial",12,),bg="#E1E9E5").place(x=10,y=10)
    Label(frame2,text="• "+"Name1",font=("Arial",10,),bg="#E1E9E5").place(x=30,y=30)
    Label(frame2,text="• "+"Name2",font=("Arial",10,),bg="#E1E9E5").place(x=30,y=50)
    Label(frame2,text="• "+"Name3",font=("Arial",10,),bg="#E1E9E5").place(x=30,y=70)
    Label(frame2,text="• "+"Name4",font=("Arial",10,),bg="#E1E9E5").place(x=30,y=90)

    Enroll = Label(frame2, text="Join as tutor", fg="white", bg="#23cff2", cursor="hand2",
                    font=("Arial",12,"bold"), padx=5, pady=2, bd=2, relief="groove")
    Enroll.place(x=30,y=115)
    Enroll.bind("<Button-1>", lambda e: joining_page(parent, name))  
    frame=Frame(root,bg="#E1E9E5",width=750,height=150,bd=2,relief="groove")
    frame.pack_propagate(False)
    frame.pack(pady=10)
    #-------------------avtar image----------------------

    name_logo(frame)
    Label(frame,text="Nischal",font=("Arial",12,"bold"),bg="#E1E9E5").place(x=50,y=10)
    Label(frame,text="Topic: "+"Use of pack_propogate()",font=("Arial",10,"bold"),bg="#E1E9E5").place(x=25,y=40)
    Label(frame,text="loram hello world If you don't use this line, the frame will shrink\n or expand to perfectlyfit whatever buttons or labels you"+" ......",
            font=("Arial",10),
            bg="#E1E9E5",
            justify="left"
            ).place(x=25,y=60)
    Volunteer = Label(frame,
                    text="Volunteer _name",
                    bd=2,relief="groove",
                    fg="white",bg="#23cff2", cursor="hand2",font=("Arial",12,"bold"),padx=5,pady=2)
    Volunteer.place(x=30,y=110)
    Volunteer.bind("<Button-1>", lambda e: login_page())


    frame2=Frame(frame,bg="#E1E9E5",width=200,height=145)
    frame2.place(x=545,y=0) 
    Label(frame2,text="👨🏽‍🎓"+"Enrolled Students",font=("Arial",12,),bg="#E1E9E5").place(x=10,y=10)
    Label(frame2,text="• "+"Name1",font=("Arial",10,),bg="#E1E9E5").place(x=30,y=30)
    Label(frame2,text="• "+"Name2",font=("Arial",10,),bg="#E1E9E5").place(x=30,y=50)
    Label(frame2,text="• "+"Name3",font=("Arial",10,),bg="#E1E9E5").place(x=30,y=70)
    Label(frame2,text="• "+"Name4",font=("Arial",10,),bg="#E1E9E5").place(x=30,y=90)

    Enroll = Label(frame2,
                    text="Join as tutor",
                    fg="white",bg="#23cff2", cursor="hand2",font=("Arial",12,"bold"),padx=5,pady=2,bd=2,relief="groove")
    Enroll.place(x=30,y=115)
    Enroll.bind("<Button-1>", lambda e: joining_page(root,name))
def profile_page(name):
    profile_root = Toplevel(root)
    profile_root.title("Profile")
    profile_root.geometry("800x600")
    profile_root.resizable(0, 0)
    root.withdraw()
    Navbar(profile_root, name)
    Label(profile_root, text=f"User Profile: {name}", font=("Arial", 20, "bold")).pack(pady=20)

    def on_close():
        profile_root.destroy()
        root.deiconify() 

    profile_root.protocol("WM_DELETE_WINDOW", on_close)   

def post_page(name):
    post_root = Toplevel(root)
    post_root.title("Post")
    post_root.geometry("800x600")
    post_root.resizable(0, 0)
    post_root.configure(bg="#f2f2f2") 
    root.withdraw()
    
    Navbar(post_root, name)

    # --- Title Section ---
    Label(post_root, text="Title", font=("Arial", 16), bg="#f2f2f2").place(x=50, y=100)
    title_entry = Entry(post_root, font=("Arial", 14), width=30, bd=1, relief="solid")
    title_entry.place(x=50, y=135)

    # --- Description Section ---
    Label(post_root, text="Description", font=("Arial", 16), bg="#f2f2f2").place(x=50, y=190)
    # Using Text widget instead of Entry for multi-line description
    description_entry = Text(post_root, font=("Arial", 12), width=60, height=10, bd=1, relief="solid")
    description_entry.place(x=50, y=225)

    # --- Post Button ---
 
    post_btn = Label(
        post_root, 
        text="Post now  +", 
        font=("Arial", 16, "bold"), 
        bg="#23cff2", 
        fg="white",
        padx=20, 
        pady=10,
        cursor="hand2",
        bd=1,
        relief="solid"
    )
    post_btn.place(x=50, y=450)
    

    post_btn.bind("<Button-1>", lambda e: print("Post Logic Here"))

    def on_close():
        post_root.destroy()
        root.deiconify()
        
    post_root.protocol("WM_DELETE_WINDOW", on_close)
def student_page(name):
    student_root = Toplevel(root)
    student_root.geometry("800x650")
    student_root.resizable(0, 0)
    student_root.title("Student")
    root.withdraw()
    Navbar(student_root, name)

    student_frame = Frame(student_root, bg="#f2f2f2", width=800, height=650)
    student_frame.pack_propagate(False)
    student_frame.pack()
    Label(student_frame,text="Welcome;",font=("Arial",12,"bold"),bg="#f2f2f2").place(x=20,y=10)
    Label(student_frame,text="Do you have any doubts?",font=("Arial",10,),bg="#f2f2f2").place(x=470,y=14)
    button = Label(student_frame, text="Post doubts here", fg="white", bg="#00bcd4",
                    cursor="hand2", font=("Arial",12,"bold"), padx=5, pady=2)
    button.place(x=625,y=10)
    button.bind("<Button-1>", lambda e: post_page(name))

    data_frame=Frame(student_frame,width=750,height=500)
    data_frame.place(x=20,y=40)

    student_content(data_frame, name, student_root)  
    student_content(data_frame, name, student_root)
    student_content(data_frame, name, student_root)

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
    Navbar(teacher_root, name)
    teacher_content(teacher_root, name, teacher_root) 
    teacher_content(teacher_root, name, teacher_root)
    teacher_content(teacher_root, name, teacher_root)

    def new_window():
        teacher_root.destroy()
        root.deiconify()

    teacher_root.protocol("WM_DELETE_WINDOW", new_window)


def joining_page(root, name):
    join_root = Toplevel(root)
    join_root.geometry("800x650")
    join_root.resizable(0, 0)
    join_root.title("Join Session")
    join_root.configure(bg="white")
    root.withdraw()
    
    Navbar(join_root, name)

    # Main Container Frame
    # Using a flat background with a light border to match the clean UI
    main_frame = Frame(join_root, bg="white", width=760, height=540)
    main_frame.place(x=20, y=100)

    name_logo(main_frame)  # Uses your existing name_logo function
    Label(main_frame, text="Nischal", font=("Arial", 14, "bold"), bg="white").place(x=60, y=8)


    title_entry = Entry(main_frame, font=("Arial", 12), width=45, bd=1, relief="solid", bg="#f2f2f2")
    title_entry.insert(0, "Python") # Placeholder
    title_entry.place(x=30, y=80, height=40)

    # Description Text (Larger box)
    desc_text = Text(main_frame, font=("Arial", 11), width=45, height=8, bd=1, relief="solid", bg="white")
    desc_text.insert("1.0", "Lorem Ipsum is simply dummy text of the printing and typesetting industry...")
    desc_text.place(x=30, y=140)


    global clicked_block
    clicked_block = StringVar(value="Block-E Seminar hall") # Default value

  
    Label(main_frame, text="Select Location:", font=("Arial", 10), bg="white").place(x=30, y=295)


    block_menu = OptionMenu(
        main_frame, 
        clicked_block, 
        "Block-E Seminar hall", 
        "Block-D Seminar hall", 
        "Block-C Seminar hall"
    )
    

    block_menu.config(
        bg="#f2f2f2", 
        fg="black", 
        font=("Arial", 11), 
        indicatoron=True, 
        bd=1, 
        relief="solid"
    )
    block_menu["menu"].config(bg="#f2f2f2", font=("Arial", 11))
    # block_menu.place(x=30, y=320, width=235, height=40)
    block_menu.place(x=30, y=320, height=40)


    enrolled_frame = Frame(main_frame, bg="#f2f2f2", width=220, height=350, bd=1, relief="solid")
    enrolled_frame.place(x=510, y=30)
    
    Label(enrolled_frame, text="Enrolled", font=("Arial", 14), bg="#f2f2f2").pack(pady=10)
    
    # List of names with bullet points
    students = ["Nischal Shrestha", "Norman Singh", "Anurag Pandey", "Samir D.C"]
    for student in students:
        Label(enrolled_frame, text=f"•  {student}", font=("Arial", 11), bg="#f2f2f2", anchor="w").pack(fill="x", padx=20, pady=2)


    join_btn = Button(
        main_frame, 
        text="Join Now", 
        font=("Arial", 14, "bold"), 
        bg="#23cff2", 
        fg="white", 
        width=15,
        bd=0, 
        cursor="hand2",
        activebackground="#1eb6d4"
    )
    join_btn.place(x=300, y=480, height=35)

    def on_close():
        join_root.destroy()
        root.deiconify()
        
    join_root.protocol("WM_DELETE_WINDOW", on_close)

image_bg = Image.open("assects/dashboard.jpg")
resize_bg =image_bg.resize((800, 600))
final_bg = ImageTk.PhotoImage(resize_bg)

lbl = Label(root, image=final_bg)
lbl.image = final_bg 
lbl.pack()

button = Label(root,
                    text="Login",
                    fg="white",bg="#72dae4", cursor="hand2",font=("Arial",16,"bold"),padx=20,pady=2)
button.place(x=350,y=390)
button.bind("<Button-1>", lambda e: login_page())

root.mainloop()