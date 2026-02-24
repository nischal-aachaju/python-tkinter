from tkinter import *
import sqlite3
from PIL import Image, ImageTk

#----------database-----------------
conn=sqlite3.connect("cdrs.db")
cur=conn.cursor()

root =Tk()
root.geometry("800x600")
root.resizable(0,0)
root.iconbitmap('assects/logo.ico')

def Navbar():
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
    text_profile=Label(nav_frame,text="Nischal ;",font=("Arial",20),bg="#23cff2",fg="black",bd=0)
    text_profile.place(x=600,y=25)



if __name__ == "__main__":
    Navbar()

root.mainloop()

