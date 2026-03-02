from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3
import hashlib



#-------------------DATABASE SETUP-------------------

auth_conn = sqlite3.connect("userAuthUI.db")
auth_cur = auth_conn.cursor()
auth_cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        email             TEXT PRIMARY KEY,
        name              TEXT NOT NULL,
        password          TEXT NOT NULL,
        role              TEXT NOT NULL,
        security_password TEXT NOT NULL
    )
""")
auth_conn.commit()


# ----------DATABASE TABLES----------------

app_conn = sqlite3.connect("cdrs.db")
app_cur = app_conn.cursor()

# Authentication table
# doubts table
app_cur.execute("""
    CREATE TABLE IF NOT EXISTS doubts (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT NOT NULL,
        title        TEXT NOT NULL,
        description  TEXT NOT NULL,
        status       TEXT DEFAULT 'Open',
        posted_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# participants table
app_cur.execute("""
    CREATE TABLE IF NOT EXISTS participants (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        doubt_id     INTEGER NOT NULL REFERENCES doubts(id),
        student_name TEXT NOT NULL,
        joined_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(doubt_id, student_name)
    )
""")
# volunteers table
app_cur.execute("""
    CREATE TABLE IF NOT EXISTS volunteers (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        doubt_id       INTEGER NOT NULL REFERENCES doubts(id),
        volunteer_name TEXT NOT NULL,
        volunteered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(doubt_id, volunteer_name)
    )
""")
# sessions table
app_cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        doubt_id     INTEGER UNIQUE NOT NULL REFERENCES doubts(id),
        teacher_name TEXT NOT NULL,
        room         TEXT NOT NULL,
        scheduled_at TEXT NOT NULL,
        created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
# rooms table
app_cur.execute("""
    CREATE TABLE IF NOT EXISTS rooms (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        room_name    TEXT NOT NULL UNIQUE,
        is_available INTEGER DEFAULT 1
    )
""")

# Insert default rooms # refrences from stackoverflow
app_cur.executemany(
    "INSERT OR IGNORE INTO rooms (room_name) VALUES (?)",
    [("Block-E Seminar hall",), ("Block-D Seminar hall",), ("Block-C Seminar hall",)]
)
app_conn.commit()



# password hashing using sha256 python Hashlib
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# function to get user
def get_user(email):
    auth_cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    return auth_cur.fetchone()


# function to create user
def create_user(email, name, password, role, security_password):
    auth_cur.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                     (email, name, hash_password(password), role, security_password))
    auth_conn.commit()

# function to update password
def update_password(email, new_password):
    auth_cur.execute("UPDATE users SET password = ? WHERE email = ?",
                     (hash_password(new_password), email))
    auth_conn.commit()

# function to post doubt 
def post_doubt(student_name, title, description):
    app_cur.execute("INSERT INTO doubts (student_name, title, description) VALUES (?, ?, ?)",
                    (student_name, title, description))
    app_conn.commit()

def get_all_doubts():
    app_cur.execute("SELECT * FROM doubts ORDER BY posted_at DESC")
    return app_cur.fetchall()

def update_doubt_status(doubt_id, status):
    app_cur.execute("UPDATE doubts SET status = ? WHERE id = ?", (status, doubt_id))
    app_conn.commit()

def join_doubt(doubt_id, student_name):
    try:
        app_cur.execute("INSERT INTO participants (doubt_id, student_name) VALUES (?, ?)",
                        (doubt_id, student_name))
        app_conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def get_participants(doubt_id):
    app_cur.execute("SELECT student_name, joined_at FROM participants WHERE doubt_id = ?", (doubt_id,))
    return app_cur.fetchall()

def volunteer_for_doubt(doubt_id, volunteer_name):
    try:
        app_cur.execute("INSERT INTO volunteers (doubt_id, volunteer_name) VALUES (?, ?)",
                        (doubt_id, volunteer_name))
        app_conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def get_volunteers(doubt_id):
    app_cur.execute("SELECT volunteer_name, volunteered_at FROM volunteers WHERE doubt_id = ?", (doubt_id,))
    return app_cur.fetchall()

def schedule_session(doubt_id, teacher_name, room, scheduled_at):
    try:
        app_cur.execute("INSERT INTO sessions (doubt_id, teacher_name, room, scheduled_at) VALUES (?, ?, ?, ?)",
                        (doubt_id, teacher_name, room, scheduled_at))
        app_conn.commit()
        update_doubt_status(doubt_id, "Scheduled")
        return True
    except sqlite3.IntegrityError:
        return False

def get_session(doubt_id):
    app_cur.execute("SELECT * FROM sessions WHERE doubt_id = ?", (doubt_id,))
    return app_cur.fetchone()

def get_available_rooms():
    app_cur.execute("SELECT room_name FROM rooms WHERE is_available = 1")
    return [row[0] for row in app_cur.fetchall()]



# -----------------------UI-----------------------


root = Tk()
root.geometry("800x600")
root.resizable(0, 0)
root.iconbitmap('assects/logo.ico')


def login_page():
    login_root = Toplevel(root)
    login_root.geometry("800x650")
    login_root.resizable(0, 0)
    login_root.title("Login")
    root.withdraw()

    def show_frame(frame):
        login_frame.pack_forget()
        register_frame.pack_forget()
        forgot_frame.pack_forget()
        frame.pack(pady=60)

    def login():
        if not login_email.get() or not login_password.get():
            messagebox.showwarning("Error", "All fields are required", parent=login_root)
            return
        record = get_user(login_email.get())
        if record and hash_password(login_password.get()) == record[2]:
            login_password.delete(0, END)
            login_email.delete(0, END)
            login_root.destroy()
            if record[3] == "Student":
                student_page(record[1])
            elif record[3] == "Teacher":
                teacher_page(record[1])
        else:
            messagebox.showerror("Error", "Invalid credentials", parent=login_root)
            login_password.delete(0, END)

    def register():
        if reg_password.get() != reg_con_password.get():
            messagebox.showwarning("Error", "Passwords do not match", parent=login_root)
            return
        if not all([reg_email.get(), reg_name.get(), reg_password.get(), role_var.get(), security_password.get()]):
            messagebox.showwarning("Error", "All fields are required", parent=login_root)
            return
        try:
            create_user(reg_email.get(), reg_name.get(), reg_password.get(), role_var.get(), security_password.get())
            messagebox.showinfo("Success", "Registered Successfully", parent=login_root)
            show_frame(login_frame)
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Email already exists", parent=login_root)

    def reset_password():
        if not forgot_email.get() or not new_password.get():
            messagebox.showwarning("Error", "All fields required", parent=login_root)
            return
        record = get_user(forgot_email.get())
        if not record:
            messagebox.showerror("Error", "Email not found", parent=login_root)
            return
        if not forgot_security_password.get():
            messagebox.showwarning("Error", "Security Password required", parent=login_root)
            return
        if forgot_security_password.get() != record[4]:
            messagebox.showerror("Error", "Security Password not matched", parent=login_root)
            return
        update_password(forgot_email.get(), new_password.get())
        messagebox.showinfo("Success", "Password Updated Successfully", parent=login_root)
        new_password.delete(0, END)
        forgot_email.delete(0, END)
        forgot_security_password.delete(0, END)
        show_frame(login_frame)

    login_frame = Frame(login_root, bg="white", width=500, height=480)
    login_frame.pack_propagate(False)
    login_frame.pack(pady=60)
    Label(login_frame, text="Login", font=("Arial", 24, "bold"), bg="white").pack(pady=(20, 5))
    Label(login_frame, text="to solve doubt", fg="gray", bg="white").pack(pady=(0, 20))
    Label(login_frame, text="Email", bg="white", font=("Arial", 16)).place(x=50, y=120)
    login_email = Entry(login_frame, width=30, bd=2, relief="groove", font=("Arial", 16))
    login_email.place(x=50, y=155)
    Label(login_frame, text="Password", bg="white", font=("Arial", 16)).place(x=50, y=210)
    login_password = Entry(login_frame, width=30, show="*", bd=2, relief="groove", font=("Arial", 16))
    login_password.place(x=50, y=245)
    Button(login_frame, text="Login", width=27, bg="#00bcd4", fg="white",
           font=("Arial", 16, "bold"), command=login).place(x=50, y=300)
    forgot_lbl = Label(login_frame, text="Forgot Password?", fg="blue", bg="white", cursor="hand2", font=("Arial", 10))
    forgot_lbl.place(x=175, y=350)
    forgot_lbl.bind("<Button-1>", lambda e: show_frame(forgot_frame))
    register_lbl = Label(login_frame, text="Don't have an account? Register", fg="#EB310C", bg="white", cursor="hand2", font=("", 12))
    register_lbl.place(x=50, y=390)
    register_lbl.bind("<Button-1>", lambda e: show_frame(register_frame))

    register_frame = Frame(login_root, bg="white", width=500, height=480)
    Label(register_frame, text="Register", font=("Arial", 24, "bold"), bg="white").place(x=180, y=18)
    Label(register_frame, text="to solve doubt", fg="gray", bg="white").place(x=200, y=60)
    Label(register_frame, text="User Name", bg="white", font=("Arial", 16)).place(x=50, y=90)
    reg_name = Entry(register_frame, width=30, bd=2, relief="groove", font=("Arial", 16))
    reg_name.place(x=50, y=120)
    Label(register_frame, text="Email", bg="white", font=("Arial", 16)).place(x=50, y=155)
    reg_email = Entry(register_frame, width=30, bd=2, relief="groove", font=("Arial", 16))
    reg_email.place(x=50, y=185)
    Label(register_frame, text="Password", bg="white", font=("Arial", 16)).place(x=50, y=215)
    reg_password = Entry(register_frame, width=30, show="*", bd=2, relief="groove", font=("Arial", 16))
    reg_password.place(x=50, y=245)
    Label(register_frame, text="Confirm Password", bg="white", font=("Arial", 16)).place(x=50, y=275)
    reg_con_password = Entry(register_frame, width=30, show="*", bd=2, relief="groove", font=("Arial", 16))
    reg_con_password.place(x=50, y=305)
    Label(register_frame, text="Security Password:", bg="white", font=("Arial", 10)).place(x=130, y=355)
    Label(register_frame, text="favourite pet name?", bg="white", font=("Arial", 10)).place(x=255, y=335)
    security_password = Entry(register_frame, width=20, bd=2, relief="groove", font=("Arial", 10))
    security_password.place(x=250, y=355)
    role_var = StringVar(value="Student")
    Radiobutton(register_frame, text="Student", variable=role_var, value="Student", bg="white").place(x=50, y=335)
    Radiobutton(register_frame, text="Teacher", variable=role_var, value="Teacher", bg="white").place(x=50, y=355)
    Button(register_frame, text="Register", width=27, bg="#00bcd4", fg="white",
           font=("Arial", 16, "bold"), command=register).place(x=50, y=380)
    back_login_lbl = Label(register_frame, text="Already have account? Login", fg="#0000FF", bg="white", cursor="hand2", font=("arial", 13))
    back_login_lbl.place(x=50, y=430)
    back_login_lbl.bind("<Button-1>", lambda e: show_frame(login_frame))

    forgot_frame = Frame(login_root, bg="white", width=500, height=480)
    Label(forgot_frame, text="Forgot Password", font=("Arial", 22, "bold"), bg="white").place(x=135, y=40)
    Label(forgot_frame, text="Reset your password", fg="gray", bg="white").place(x=190, y=80)
    Label(forgot_frame, text="Email", bg="white", font=("Arial", 16)).place(x=50, y=135)
    forgot_email = Entry(forgot_frame, width=30, bd=2, relief="groove", font=("Arial", 16))
    forgot_email.place(x=50, y=170)
    Label(forgot_frame, text="New Password", bg="white", font=("Arial", 16)).place(x=50, y=220)
    new_password = Entry(forgot_frame, width=30, show="*", bd=2, relief="groove", font=("Arial", 16))
    new_password.place(x=50, y=250)
    Label(forgot_frame, text="Security Password:", bg="white", font=("Arial", 16)).place(x=50, y=305)
    forgot_security_password = Entry(forgot_frame, width=30, show="*", bd=2, relief="groove", font=("Arial", 16))
    forgot_security_password.place(x=50, y=335)
    Button(forgot_frame, text="Submit", width=27, bg="#00bcd4", fg="white",
           font=("Arial", 16, "bold"), command=reset_password).place(x=50, y=380)
    forgot_back_lbl = Label(forgot_frame, text="Back to Login", fg="blue", bg="white", cursor="hand2", font=("Arial", 10))
    forgot_back_lbl.place(x=195, y=430)
    forgot_back_lbl.bind("<Button-1>", lambda e: show_frame(login_frame))

    show_frame(login_frame)

    def on_close():
        login_root.destroy()
        root.deiconify()
    login_root.protocol("WM_DELETE_WINDOW", on_close)


def Navbar(page_root, username):
    nav_frame = Frame(page_root, bg="#23cff2", height=80)
    nav_frame.pack(fill=X)
    image_logo = Image.open("assects/logo.png").resize((80, 80))
    image_logoTk = ImageTk.PhotoImage(image_logo)
    lbl_logo = Label(nav_frame, image=image_logoTk, bd=0)
    lbl_logo.image = image_logoTk
    lbl_logo.place(x=10, y=0)
    image_text = Image.open("assects/logo_text.png").resize((150, 50))
    image_textTk = ImageTk.PhotoImage(image_text)
    text_logo = Label(nav_frame, image=image_textTk, bd=0)
    text_logo.image = image_textTk
    text_logo.place(x=100, y=15)
    image_profile = Image.open("assects/main_profile.png").resize((40, 40))
    image_profileTk = ImageTk.PhotoImage(image_profile)
    profile_logo = Label(nav_frame, image=image_profileTk, bd=0)
    profile_logo.image = image_profileTk
    profile_logo.bind("<Button-1>", lambda e: profile_page(username))
    profile_logo.place(x=700, y=10)
    text_profile = Label(nav_frame, text=username + ";", font=("Arial", 14), bg="#23cff2", fg="black", bd=0)
    text_profile.place(x=640, y=54)
    image_logout = Image.open("assects/logout.png").resize((30, 30))
    image_logoutTk = ImageTk.PhotoImage(image_logout)
    logout_logo = Label(nav_frame, image=image_logoutTk, bd=0)
    logout_logo.image = image_logoutTk
    logout_logo.place(x=750, y=22)
    def do_logout():
        page_root.destroy()
        root.deiconify()
        login_page()
    logout_logo.bind("<Button-1>", lambda e: do_logout())


def name_logo(frame):
    avtar_image = Image.open("assects/question.png").resize((20, 20))
    avtar_imageTk = ImageTk.PhotoImage(avtar_image)
    lbl_logo = Label(frame, image=avtar_imageTk, bd=0)
    lbl_logo.image = avtar_imageTk
    lbl_logo.place(x=28, y=10)


def student_content(parent_frame, current_user, parent_root, doubt, on_back=None):
    doubt_id, posted_by, title, description, status, posted_at = doubt

    frame = Frame(parent_frame, bg="#E1E9E5", width=750, height=150, bd=2, relief="groove")
    frame.pack_propagate(False)
    frame.pack(pady=10)
    name_logo(frame)

    Label(frame, text=posted_by, font=("Arial", 12, "bold"), bg="#E1E9E5").place(x=50, y=10)
    Label(frame, text="Topic: " + title, font=("Arial", 10, "bold"), bg="#E1E9E5").place(x=25, y=40)
    short_desc = description[:80] + " ......" if len(description) > 80 else description
    Label(frame, text=short_desc, font=("Arial", 10), bg="#E1E9E5", justify="left").place(x=25, y=60)

    Volunteer = Label(frame, text="Volunteer", bd=2, relief="groove",
                      fg="white", bg="#23cff2", cursor="hand2", font=("Arial", 12, "bold"), padx=5, pady=2)
    Volunteer.place(x=30, y=110)
    Volunteer.bind("<Button-1>", lambda e: joining_page(parent_root, current_user, doubt_id, "volunteer", on_back))

    session = get_session(doubt_id)
    teacher_label = session[2] if session else "No Teacher Yet"
    Teacher = Label(frame, text=teacher_label, bd=2, relief="groove",
                    fg="white", bg="#23cff2", cursor="hand2", font=("Arial", 12, "bold"), padx=5, pady=2)
    Teacher.place(x=130, y=110)
    Teacher.bind("<Button-1>", lambda e: joining_page(parent_root, current_user, doubt_id, "join", on_back))

    frame2 = Frame(frame, bg="#E1E9E5", width=200, height=145)
    frame2.place(x=545, y=0)
    Label(frame2, text="👨🏽‍🎓 Enrolled Students", font=("Arial", 12), bg="#E1E9E5").place(x=10, y=10)

    participants = get_participants(doubt_id)
    volunteers  = get_volunteers(doubt_id)
    all_enrolled = [(pname, "student") for pname, _ in participants] + \
                   [(vname, "volunteer") for vname, _ in volunteers]
    if all_enrolled:
        for i, (pname, role) in enumerate(all_enrolled[:4]):
            display = f"• {pname} (volunteer)" if role == "volunteer" else f"• {pname}"
            Label(frame2, text=display, font=("Arial", 10), bg="#E1E9E5").place(x=10, y=30 + i * 20)
    else:
        Label(frame2, text="No students yet", font=("Arial", 10), fg="gray", bg="#E1E9E5").place(x=10, y=30)

    Enroll = Label(frame2, text="Enroll Now", fg="white", bg="#23cff2", cursor="hand2",
                   font=("Arial", 12, "bold"), padx=5, pady=2, bd=2, relief="groove")
    Enroll.place(x=10, y=115)
    Enroll.bind("<Button-1>", lambda e: joining_page(parent_root, current_user, doubt_id, "join", on_back))


def teacher_content(parent_frame, current_user, parent_root, doubt, on_back=None):
    doubt_id, posted_by, title, description, status, posted_at = doubt

    frame = Frame(parent_frame, bg="#E1E9E5", width=750, height=150, bd=2, relief="groove")
    frame.pack_propagate(False)
    frame.pack(pady=10)
    name_logo(frame)

    Label(frame, text=posted_by, font=("Arial", 12, "bold"), bg="#E1E9E5").place(x=50, y=10)
    Label(frame, text="Topic: " + title, font=("Arial", 10, "bold"), bg="#E1E9E5").place(x=25, y=40)
    short_desc = description[:80] + " ......" if len(description) > 80 else description
    Label(frame, text=short_desc, font=("Arial", 10), bg="#E1E9E5", justify="left").place(x=25, y=60)

    volunteers  = get_volunteers(doubt_id)
    vol_label = volunteers[0][0] if volunteers else "No Volunteer Yet"
    Volunteer = Label(frame, text=vol_label, bd=2, relief="groove",
                      fg="white", bg="#23cff2", cursor="hand2", font=("Arial", 12, "bold"), padx=5, pady=2)
    Volunteer.place(x=30, y=110)
    Volunteer.bind("<Button-1>", lambda e: joining_page(parent_root, current_user, doubt_id, "teacher", on_back))

    frame2 = Frame(frame, bg="#E1E9E5", width=200, height=145)
    frame2.place(x=545, y=0)
    Label(frame2, text="👨🏽‍🎓 Enrolled Students", font=("Arial", 12), bg="#E1E9E5").place(x=10, y=10)

    participants = get_participants(doubt_id)
    volunteers  = get_volunteers(doubt_id)
    all_enrolled = [(pname, "student") for pname, _ in participants] + \
                   [(vname, "volunteer") for vname, _ in volunteers]
    if all_enrolled:
        for i, (pname, role) in enumerate(all_enrolled[:4]):
            display = f"• {pname} (volunteer)" if role == "volunteer" else f"• {pname}"
            Label(frame2, text=display, font=("Arial", 10), bg="#E1E9E5").place(x=10, y=30 + i * 20)
    else:
        Label(frame2, text="No students yet", font=("Arial", 10), fg="gray", bg="#E1E9E5").place(x=10, y=30)

    Enroll = Label(frame2, text="Join as tutor", fg="white", bg="#23cff2", cursor="hand2",
                   font=("Arial", 12, "bold"), padx=5, pady=2, bd=2, relief="groove")
    Enroll.place(x=10, y=115)
    Enroll.bind("<Button-1>", lambda e: joining_page(parent_root, current_user, doubt_id, "teacher", on_back))


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


def post_page(name, on_back=None):
    post_root = Toplevel(root)
    post_root.title("Post")
    post_root.geometry("800x600")
    post_root.resizable(0, 0)
    post_root.configure(bg="#f2f2f2")
    root.withdraw()
    Navbar(post_root, name)

    def submit_post():
        title = title_entry.get().strip()
        description = description_entry.get("1.0", END).strip()
        if not title or not description:
            messagebox.showwarning("Error", "Title and Description are required", parent=post_root)
            return
        post_doubt(name, title, description)
        messagebox.showinfo("Success", "Doubt posted successfully!", parent=post_root)
        title_entry.delete(0, END)
        description_entry.delete("1.0", END)

    Label(post_root, text="Title", font=("Arial", 16), bg="#f2f2f2").place(x=50, y=100)
    title_entry = Entry(post_root, font=("Arial", 14), width=30, bd=1, relief="solid")
    title_entry.place(x=50, y=135)
    Label(post_root, text="Description", font=("Arial", 16), bg="#f2f2f2").place(x=50, y=190)
    description_entry = Text(post_root, font=("Arial", 12), width=60, height=10, bd=1, relief="solid")
    description_entry.place(x=50, y=225)
    post_btn = Label(post_root, text="Post now  +", font=("Arial", 16, "bold"),
                     bg="#23cff2", fg="white", padx=20, pady=10, cursor="hand2", bd=1, relief="solid")
    post_btn.place(x=50, y=450)
    post_btn.bind("<Button-1>", lambda e: submit_post())

    def on_close():
        post_root.destroy()
        root.deiconify()
        if on_back:
            on_back()
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
    Label(student_frame, text="Welcome;", font=("Arial", 12, "bold"), bg="#f2f2f2").place(x=20, y=10)
    Label(student_frame, text="Do you have any doubts?", font=("Arial", 10), bg="#f2f2f2").place(x=470, y=14)

    canvas = Canvas(student_frame, bg="#f2f2f2", width=760, height=560)
    scrollbar = Scrollbar(student_frame, orient=VERTICAL, command=canvas.yview)
    data_frame = Frame(canvas, bg="#f2f2f2")
    data_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=data_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.place(x=10, y=45)
    scrollbar.place(x=770, y=45, height=560)

    def refresh_cards():
        for w in data_frame.winfo_children():
            w.destroy()
        doubts = get_all_doubts()
        if doubts:
            for doubt in doubts:
                student_content(data_frame, name, student_root, doubt, refresh_cards)
        else:
            Label(data_frame, text="No doubts posted yet.", font=("Arial", 14),
                  bg="#f2f2f2", fg="gray").pack(pady=40)


    button = Label(student_frame, text="Post doubts here", fg="white", bg="#00bcd4",
                   cursor="hand2", font=("Arial", 12, "bold"), padx=5, pady=2)
    button.place(x=625, y=10)
    button.bind("<Button-1>", lambda e: post_page(name, refresh_cards))

    refresh_cards()  

    def on_close():
        student_root.destroy()
        root.deiconify()
    student_root.protocol("WM_DELETE_WINDOW", on_close)


def teacher_page(name):
    teacher_root = Toplevel(root)
    teacher_root.geometry("800x650")
    teacher_root.resizable(0, 0)
    teacher_root.title("Teacher")
    root.withdraw()
    Navbar(teacher_root, name)

    teacher_frame = Frame(teacher_root, bg="#f2f2f2", width=800, height=650)
    teacher_frame.pack_propagate(False)
    teacher_frame.pack()
    Label(teacher_frame, text="Teacher Dashboard", font=("Arial", 12, "bold"), bg="#f2f2f2").place(x=20, y=10)

    canvas = Canvas(teacher_frame, bg="#f2f2f2", width=760, height=560)
    scrollbar = Scrollbar(teacher_frame, orient=VERTICAL, command=canvas.yview)
    data_frame = Frame(canvas, bg="#f2f2f2")
    data_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=data_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.place(x=10, y=45)
    scrollbar.place(x=770, y=45, height=560)

    def refresh_cards():
        for w in data_frame.winfo_children():
            w.destroy()
        doubts = get_all_doubts()
        if doubts:
            for doubt in doubts:
                teacher_content(data_frame, name, teacher_root, doubt, refresh_cards)
        else:
            Label(data_frame, text="No doubts posted yet.", font=("Arial", 14),
                  bg="#f2f2f2", fg="gray").pack(pady=40)

    refresh_cards()   

    def on_close():
        teacher_root.destroy()
        root.deiconify()
    teacher_root.protocol("WM_DELETE_WINDOW", on_close)


def joining_page(prev_root, name, doubt_id, mode="join", on_back=None):
    join_root = Toplevel(root)
    join_root.geometry("800x650")
    join_root.resizable(0, 0)
    join_root.title("Join Session")
    join_root.configure(bg="white")
    prev_root.withdraw()

    Navbar(join_root, name)

    main_frame = Frame(join_root, bg="white", width=760, height=540)
    main_frame.place(x=20, y=100)

    app_cur.execute("SELECT * FROM doubts WHERE id = ?", (doubt_id,))
    doubt = app_cur.fetchone()

    name_logo(main_frame)
    Label(main_frame, text=doubt[1], font=("Arial", 14, "bold"), bg="white").place(x=60, y=8)

    title_entry = Entry(main_frame, font=("Arial", 12), width=45, bd=1, relief="solid", bg="#f2f2f2")
    title_entry.insert(0, doubt[2])
    title_entry.place(x=30, y=80, height=40)

    desc_text = Text(main_frame, font=("Arial", 11), width=45, height=8, bd=1, relief="solid", bg="white")
    desc_text.insert("1.0", doubt[3])
    desc_text.place(x=30, y=140)

    available_rooms = get_available_rooms()
    clicked_block = StringVar(value=available_rooms[0] if available_rooms else "No rooms available")
    Label(main_frame, text="Select Location:", font=("Arial", 10), bg="white").place(x=30, y=295)
    block_menu = OptionMenu(main_frame, clicked_block, *available_rooms)
    block_menu.config(bg="#f2f2f2", fg="black", font=("Arial", 11), indicatoron=True, bd=1, relief="solid")
    block_menu["menu"].config(bg="#f2f2f2", font=("Arial", 11))
    block_menu.place(x=30, y=320, height=40)

    time_entry = Entry(main_frame, font=("Arial", 12), width=25, bd=1, relief="solid", bg="#f2f2f2")
    time_entry.insert(0, "2026/01/25 ( 12:00 PM)")
    time_entry.place(x=30, y=380, height=40)

    enrolled_frame = Frame(main_frame, bg="#f2f2f2", width=220, height=350, bd=1, relief="solid")
    enrolled_frame.place(x=510, y=30)

    def refresh_enrolled():
        for w in enrolled_frame.winfo_children():
            w.destroy()
        Label(enrolled_frame, text="Enrolled", font=("Arial", 14), bg="#f2f2f2").pack(pady=10)
        all_enrolled = [(p, "student") for p, _ in get_participants(doubt_id)] + \
                       [(v, "volunteer") for v, _ in get_volunteers(doubt_id)]
        if all_enrolled:
            for pname, role in all_enrolled:
                display = f"•  {pname} (volunteer)" if role == "volunteer" else f"•  {pname}"
                Label(enrolled_frame, text=display, font=("Arial", 11), bg="#f2f2f2",
                      anchor="w").pack(fill="x", padx=20, pady=2)
        else:
            Label(enrolled_frame, text="No students yet", font=("Arial", 10),
                  bg="#f2f2f2", fg="gray").pack(pady=5)

    refresh_enrolled()

    btn_text = "Join Now" if mode == "join" else "Volunteer Now" if mode == "volunteer" else "Schedule Session"

    def on_action():
        if mode == "join":
            success = join_doubt(doubt_id, name)
            if success:
                messagebox.showinfo("Success", "You have successfully joined!", parent=join_root)
                refresh_enrolled()
            else:
                messagebox.showinfo("Info", "You already joined this session.", parent=join_root)
        elif mode == "volunteer":
            success = volunteer_for_doubt(doubt_id, name)
            if success:
                messagebox.showinfo("Success", "You have successfully volunteered!", parent=join_root)
                refresh_enrolled()
            else:
                messagebox.showinfo("Info", "You already volunteered for this doubt.", parent=join_root)
        elif mode == "teacher":
            room = clicked_block.get()
            scheduled_at = time_entry.get().strip()
            if not scheduled_at:
                messagebox.showwarning("Error", "Please enter a date and time.", parent=join_root)
                return
            success = schedule_session(doubt_id, name, room, scheduled_at)
            if success:
                messagebox.showinfo("Success", "Session scheduled successfully!", parent=join_root)
            else:
                messagebox.showinfo("Info", "A session already exists for this doubt.", parent=join_root)

    Button(main_frame, text=btn_text, font=("Arial", 14, "bold"),
           bg="#23cff2", fg="white", width=15, bd=0, cursor="hand2",
           activebackground="#1eb6d4", command=on_action).place(x=300, y=480, height=35)

    def on_close():
        join_root.destroy()
        prev_root.deiconify()
        if on_back:
            on_back()
    join_root.protocol("WM_DELETE_WINDOW", on_close)


#   MAIN DASHBOARD


image_bg = Image.open("assects/dashboard.png")
resize_bg = image_bg.resize((800, 600))
final_bg = ImageTk.PhotoImage(resize_bg)

lbl = Label(root, image=final_bg)
lbl.image = final_bg
lbl.pack()

button = Label(root, text="Login", fg="white", bg="#72dae4", cursor="hand2",
               font=("Arial", 16, "bold"), padx=20, pady=2)
button.place(x=350, y=390)
button.bind("<Button-1>", lambda e: login_page())

root.mainloop()