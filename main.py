from tkinter import *
from tkinter import messagebox
import random
import pyperclip
import sqlite3

# ---------------------------- PASSWORD GENERATOR --------------------------- #

def password_gen():
    password_entry.delete(0, END)
    pass_word = ''
    for _ in range(8):
        pass_word += chr(random.randint(47, 125))
    password_entry.insert(string=f"{pass_word}", index=0)

# ---------------------------- SAVE PASSWORD ------------------------------- #

def save(username, db_name):
    website = web_entry.get()
    username_entry = mail_entry.get()
    password_value = password_entry.get()

    if not website or not username_entry or not password_value:
        messagebox.showerror(title="Invalid Entry", message="Please enter all the details.")
        return

    conn = sqlite3.connect(f"{db_name}.db")
    cursor = conn.cursor()

    # Create the 'passwords' table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS passwords (
                        website TEXT UNIQUE,
                        username TEXT,
                        password TEXT
                    )''')
    conn.commit()

    try:
        cursor.execute("INSERT INTO passwords (website, username, password) VALUES (?, ?, ?)",
                       (website, username_entry, password_value))
        conn.commit()
        messagebox.showinfo(title="Success", message="Password details saved successfully.")
        web_entry.delete(0, END)
        mail_entry.delete(0, END)
        password_entry.delete(0, END)
    except sqlite3.IntegrityError:
        response = messagebox.askyesno(title="Duplicate Entry",
                                       message="Website already exists in the database. Do you want to update the password?")
        if response:
            cursor.execute("UPDATE passwords SET password = ? WHERE website = ?",
                           (password_value, website))
            conn.commit()
            messagebox.showinfo(title="Success", message="Password updated successfully.")
            web_entry.delete(0, END)
            mail_entry.delete(0, END)
            password_entry.delete(0, END)

    conn.close()

# ---------------------------- SEARCH PASSWORD ----------------------------- #

def search(username, db_name):
    website = web_entry.get()

    if not website:
        messagebox.showerror(title="Invalid Entry", message="Please enter a website.")
        return

    conn = sqlite3.connect(f"{db_name}.db")
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM passwords WHERE website = ?", (website,))
    password_result = cursor.fetchone()

    conn.close()

    if password_result:
        password = password_result[0]
        messagebox.showinfo(title="Password Found", message=f"Password for {website}:\n{password}")
        pyperclip.copy(password)
    else:
        messagebox.showerror(title="Password Not Found", message=f"No password found for {website}.")

# ---------------------------- UI SETUP ------------------------------- #

def register_user():
    username = signup_username_entry.get()
    password = signup_password_entry.get()

    if not username or not password:
        messagebox.showerror(title="Invalid Entry", message="Please enter a username and password.")
        return

    conn = sqlite3.connect("user_auth.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, password, db_name) VALUES (?, ?, ?)",
                       (username, password, f"{username}_db"))
        conn.commit()
        messagebox.showinfo(title="Success", message="Registration successful. You can now log in.")
        signup_screen.destroy()
        show_login_screen()
    except sqlite3.IntegrityError:
        messagebox.showerror(title="Duplicate Entry", message="Username already exists.")

    conn.close()

def login_user():
    username = login_username_entry.get()
    password = login_password_entry.get()

    if not username or not password:
        messagebox.showerror(title="Invalid Entry", message="Please enter a username and password.")
        return

    conn = sqlite3.connect("user_auth.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()

    conn.close()

    if user:
        login_screen.destroy()
        show_password_manager(user[0], user[2])
    else:
        messagebox.showerror(title="Login Failed", message="Invalid username or password.")

def show_login_screen():
    global login_screen, login_username_entry, login_password_entry

    login_screen = Tk()
    login_screen.title("Login")
    login_screen.config(padx=30, pady=30, bg="white")

    login_label = Label(login_screen, text="Login", font=("Arial", 24, "bold"), bg="white")
    login_label.grid(row=0, column=0, columnspan=2, pady=10)

    username_label = Label(login_screen, text="Username:", bg="white")
    username_label.grid(row=1, column=0, sticky=E)

    password_label = Label(login_screen, text="Password:", bg="white")
    password_label.grid(row=2, column=0, sticky=E)

    login_username_entry = Entry(login_screen, width=30)
    login_username_entry.grid(row=1, column=1, padx=5, pady=5)
    login_username_entry.focus()

    login_password_entry = Entry(login_screen, width=30, show="*")
    login_password_entry.grid(row=2, column=1, padx=5, pady=5)

    login_button = Button(login_screen, text="Login", width=15, command=login_user)
    login_button.grid(row=3, column=0, columnspan=2, pady=10)

    signup_button = Button(login_screen, text="Sign Up", width=15, command=show_signup_screen)
    signup_button.grid(row=4, column=0, columnspan=2, pady=10)

    login_screen.mainloop()

def show_signup_screen():
    global signup_screen, signup_username_entry, signup_password_entry

    signup_screen = Tk()
    signup_screen.title("Sign Up")
    signup_screen.config(padx=30, pady=30, bg="white")

    signup_label = Label(signup_screen, text="Sign Up", font=("Arial", 24, "bold"), bg="white")
    signup_label.grid(row=0, column=0, columnspan=2, pady=10)

    username_label = Label(signup_screen, text="Username:", bg="white")
    username_label.grid(row=1, column=0, sticky=E)

    password_label = Label(signup_screen, text="Password:", bg="white")
    password_label.grid(row=2, column=0, sticky=E)

    signup_username_entry = Entry(signup_screen, width=30)
    signup_username_entry.grid(row=1, column=1, padx=5, pady=5)
    signup_username_entry.focus()

    signup_password_entry = Entry(signup_screen, width=30, show="*")
    signup_password_entry.grid(row=2, column=1, padx=5, pady=5)

    signup_button = Button(signup_screen, text="Sign Up", width=15, command=register_user)
    signup_button.grid(row=3, column=0, columnspan=2, pady=10)

    signup_screen.mainloop()

def show_password_manager(username, db_name):
    global password_manager_screen, web_entry, mail_entry, password_entry

    password_manager_screen = Tk()
    password_manager_screen.title("Password Manager")
    password_manager_screen.config(padx=30, pady=30, bg="white")

    canvas = Canvas(password_manager_screen, width=200, height=190, bg="white", highlightthickness=0)
    lock = PhotoImage(file="logo.png")

    canvas.create_image(100, 100, image=lock)
    canvas.grid(row=0, column=1)

    web_name = Label(password_manager_screen, text="Website:", bg="white")
    web_name.grid(row=1, column=0, sticky=E)

    mail_label = Label(password_manager_screen, text="Email/Username:", bg="white")
    mail_label.grid(row=2, column=0, sticky=E)

    password_label = Label(password_manager_screen, text="Password:", bg="white")
    password_label.grid(row=3, column=0, sticky=E)

    web_entry = Entry(password_manager_screen, width=52)
    web_entry.grid(row=1, column=1, columnspan=2, sticky=W)
    web_entry.focus()

    mail_entry = Entry(password_manager_screen, width=52)
    mail_entry.grid(row=2, column=1, columnspan=2, sticky=W)

    password_entry = Entry(password_manager_screen, width=31,show="*")          # show="*" can be used
    password_entry.grid(row=3, column=1, sticky=W)

    gen_pass = Button(password_manager_screen, text="Generate Password", bg="white", width=15, command=password_gen)
    gen_pass.grid(row=3, column=2, sticky=W)

    add = Button(password_manager_screen, text="Add", width=44, bg="white", command=lambda: save(username, db_name))
    add.grid(row=4, column=1, columnspan=2, sticky=W)

    search_button = Button(password_manager_screen, text="Search", width=15, bg="white",
                           command=lambda: search(username, db_name))
    search_button.grid(row=1, column=3, sticky=W)

    logout_button = Button(password_manager_screen, text="Logout", width=15, bg="white",
                           command=lambda: logout(password_manager_screen))
    logout_button.grid(row=2, column=3, sticky=W)

    password_manager_screen.mainloop()

def logout(screen):
    screen.destroy()
    show_login_screen()

# ---------------------------- MAIN PROGRAM ------------------------------ #

show_login_screen()
