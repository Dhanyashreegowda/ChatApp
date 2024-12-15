import socket
import threading
import tkinter as tk
from tkinter import Toplevel, Button, Scrollbar, messagebox
from tkinter import font as tkFont
import random

# Dummy user storage (Use a database for production applications)
users = {}  # {username: {'password': password, 'email': email}}
codes = {}  # {username: reset_code}

class ChatClient:
    def __init__(self, host='localhost', port=12345):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))

        # Theme settings (default to light theme)
        self.theme = 'light'
        self.themes = {
            'light': {
                'bg': '#f0f0f0',  # Light background
                'fg': '#000000',  # Black text
                'button_bg': '#4CAF50',  # Green buttons
                'entry_bg': '#FFFFFF'  # White entry field
            },
            'dark': {
                'bg': '#2c2f33',  # Dark background
                'fg': '#FFFFFF',  # White text
                'button_bg': '#7289da',  # Blue buttons
                'entry_bg': '#23272a'  # Dark entry field
            },
            'blue': {
                'bg': '#87CEEB',  # Blue background
                'fg': '#000000',  # Black text
                'button_bg': '#1E90FF',  # Blue buttons
                'entry_bg': '#B0E0E6'  # Light blue entry field
            },
            'pink': {
                'bg': '#FFC0CB',  # Pink background
                'fg': '#000000',  # Black text
                'button_bg': '#FF69B4',  # Hot pink buttons
                'entry_bg': '#FFB6C1'  # Light pink entry field
            }
        }

        # Show the login window first
        self.show_login_window()

    def show_login_window(self):
        # Create a login window
        self.login_window = tk.Tk()
        self.login_window.title("Login/Register")
        self.login_window.geometry("400x570")
        self.login_window.configure(bg=self.themes[self.theme]['bg'])  # Light background color
        self.apply_theme(self.login_window)

        # Title label
        label_title = tk.Label(self.login_window, text="Welcome to ChatApp", font=("Arial", 20, "bold"), fg=self.themes[self.theme]['fg'], bg=self.themes[self.theme]['bg'])
        label_title.pack(pady=(20, 10))

        # Username, password, and email fields
        self.create_entry("Username", self.themes[self.theme]['bg'], self.themes[self.theme]['fg'])
        self.create_password_entry("Password", self.themes[self.theme]['bg'], self.themes[self.theme]['fg'])
        self.create_entry("Email", self.themes[self.theme]['bg'], self.themes[self.theme]['fg'])

        # Buttons
        self.create_button("Login", self.login, self.themes[self.theme]['button_bg'], self.themes[self.theme]['fg'])
        self.create_button("Register", self.register, self.themes[self.theme]['button_bg'], self.themes[self.theme]['fg'])
        self.create_button("Reset Password", self.reset_password_prompt, self.themes[self.theme]['button_bg'], self.themes[self.theme]['fg'])
        
         # Heading for theme selection
        label_theme = tk.Label(self.login_window, text="Change Theme:", font=("Arial", 14, "bold"), fg=self.themes[self.theme]['fg'], bg=self.themes[self.theme]['bg'])
        label_theme.pack(pady=(15, 5))

        # Theme dropdown menu
        self.theme_var = tk.StringVar(value=self.theme)
        self.theme_dropdown = tk.OptionMenu(self.login_window, self.theme_var, *self.themes.keys(), command=self.change_theme)
        self.theme_dropdown.pack(pady=(10, 10))


        self.login_window.mainloop()

    def create_entry(self, label_text, bg, fg, show=None):
        label = tk.Label(self.login_window, text=label_text, font=("Arial", 12), bg=bg, fg=fg)
        label.pack(pady=(10, 5))

        entry = tk.Entry(self.login_window, width=30, font=("Arial", 12), bd=2, relief="solid", bg=self.themes[self.theme]['entry_bg'], fg=fg, show=show)
        entry.pack(pady=(0, 10))

        if label_text.lower() == "username":
            self.entry_username = entry
        elif label_text.lower() == "email":
            self.entry_email = entry

        self.fade_in_widget(entry)

    def create_password_entry(self, label_text, bg, fg):
        label = tk.Label(self.login_window, text=label_text, font=("Arial", 12), bg=bg, fg=fg)
        label.pack(pady=(10, 5))

        password_frame = tk.Frame(self.login_window, bg=bg)
        password_frame.pack(pady=(0, 10))

        self.entry_password = tk.Entry(password_frame, width=25, font=("Arial", 12), bd=2, relief="solid", bg=self.themes[self.theme]['entry_bg'], fg=fg, show="*")
        self.entry_password.pack(side="left", padx=(0, 10))

        self.show_password = False
        self.toggle_password_button = tk.Button(password_frame, text="👁️", command=self.toggle_password_visibility, font=("Arial", 12))
        self.toggle_password_button.pack(side="left")

        self.fade_in_widget(self.entry_password)

    def toggle_password_visibility(self):
        if self.show_password:
            self.entry_password.config(show="*")
        else:
            self.entry_password.config(show="")
        self.show_password = not self.show_password

    def create_button(self, text, command, bg, fg):
        button = tk.Button(
            self.login_window,
            text=text,
            command=command,
            font=("Arial", 12),
            bg=bg,
            fg=fg,
            bd=4,  # Set the border width to 4
            relief="groove",  # Change relief to 'groove' for a better effect
            padx=10,
            pady=5
        )
        button.pack(pady=(5, 10))

        # Apply fade-in effect
        self.fade_in_widget(button)

        # Bind hover events
        button.bind("<Enter>", lambda e: self.on_enter(button))
        button.bind("<Leave>", lambda e: self.on_leave(button))

    def fade_in_widget(self, widget, start_opacity=0.0, end_opacity=1.0, step=0.1):
        current_opacity = widget.winfo_fpixels('1.0i')
        if current_opacity < end_opacity:
            current_opacity += step
            widget.after(50, lambda: widget.tk.call(widget._w, 'attributes', '-alpha', current_opacity))
            self.fade_in_widget(widget, current_opacity, end_opacity, step)


    def on_enter(self, button):
        button['bg'] = '#3E8E41'  # Darker green for hover

    def on_leave(self, button):
        button['bg'] = self.themes[self.theme]['button_bg']  # Original color

    def toggle_theme(self):
        theme_list = list(self.themes.keys())
        current_index = theme_list.index(self.theme)
        self.theme = theme_list[(current_index + 1) % len(theme_list)]
        self.apply_theme(self.login_window)

    def change_theme(self, selected_theme):
        self.theme = selected_theme
        self.apply_theme(self.login_window)

    def apply_theme(self, window):
        window.configure(bg=self.themes[self.theme]['bg'])
        for widget in window.winfo_children():
            widget_type = widget.winfo_class()
            if widget_type == 'Label' or widget_type == 'Button':
                widget.configure(bg=self.themes[self.theme]['bg'], fg=self.themes[self.theme]['fg'])
            elif widget_type == 'Entry':
                widget.configure(bg=self.themes[self.theme]['entry_bg'], fg=self.themes[self.theme]['fg'])

    def clear_entries(self):
        """Clear all entry fields in the login window."""
        self.entry_username.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)

    def register(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        email = self.entry_email.get()

        if username in users:
            messagebox.showerror("Error", "Username already exists!")
        elif username == "" or password == "" or email == "":
            messagebox.showerror("Error", "All fields are required!")
        else:
            users[username] = {'password': password, 'email': email}
            messagebox.showinfo("Success", "Registration successful! Please login now.")
            self.clear_entries()  # Clear entries after successful registration

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        if username not in users:
            messagebox.showerror("Error", "Username not registered! Please register first.")
        elif users[username]['password'] == password:
            self.username = username
            
            # Send username to the server for validation
            self.client_socket.send(self.username.encode('utf-8'))  
            
            # Check for server response to see if username is taken
            response = self.client_socket.recv(1024).decode('utf-8')
            if response == "USERNAME_TAKEN":
                messagebox.showerror("Error", "Username already taken. Please choose another username.")
            else:
                messagebox.showinfo("Success", f"Welcome, {username}!")
                self.login_window.destroy()
                self.open_chat_window()
        else:
            messagebox.showerror("Error", "Incorrect password! Try again or reset password.")

    def reset_password_prompt(self):
        # Position the reset password window below the login window
        email_window = Toplevel(self.login_window)
        email_window.title("Reset Password")
        x = self.login_window.winfo_x()
        y = self.login_window.winfo_y() + self.login_window.winfo_height() + 10  # 10 pixels below the login window
        email_window.geometry(f"300x150+{x}+{y}")

        label_email = tk.Label(email_window, text="Enter your registered email:", font=("Arial", 12))
        label_email.pack(pady=(10, 5))

        self.entry_reset_email = tk.Entry(email_window, width=30)
        self.entry_reset_email.pack(pady=(0, 10))

        btn_send_code = tk.Button(email_window, text="Send Code", command=self.send_reset_code)
        btn_send_code.pack(pady=(5, 5))

        self.fade_in_widget(btn_send_code)  # Apply fade-in effect

    def send_reset_code(self):
        username = self.entry_username.get()
        email = self.entry_reset_email.get()

        if username not in users or users[username]['email'] != email:
            messagebox.showerror("Error", "Username and email do not match!")
            return

        reset_code = random.randint(100000, 999999)  # Generate a random reset code
        codes[username] = reset_code
        messagebox.showinfo("Success", f"Reset code sent to {email}. Your code is: {reset_code}")  # Simulated email sending

        # Prompt for new password
        self.prompt_new_password(username)

    def prompt_new_password(self, username):
        new_password_window = Toplevel(self.login_window)
        new_password_window.title("Set New Password")
        new_password_window.geometry("300x200")

        label_code = tk.Label(new_password_window, text="Enter reset code:", font=("Arial", 12))
        label_code.pack(pady=(10, 5))

        self.entry_reset_code = tk.Entry(new_password_window, width=30)
        self.entry_reset_code.pack(pady=(0, 10))

        label_new_password = tk.Label(new_password_window, text="Enter new password:", font=("Arial", 12))
        label_new_password.pack(pady=(10, 5))

        self.entry_new_password = tk.Entry(new_password_window, width=30, show="*")
        self.entry_new_password.pack(pady=(0, 10))

        btn_set_password = tk.Button(new_password_window, text="Set Password", command=lambda: self.set_new_password(username))
        btn_set_password.pack(pady=(5, 5))

    def set_new_password(self, username):
        reset_code = self.entry_reset_code.get()
        new_password = self.entry_new_password.get()

        if reset_code == str(codes.get(username)):
            users[username]['password'] = new_password
            messagebox.showinfo("Success", "Password has been reset successfully!")
        else:
            messagebox.showerror("Error", "Invalid reset code!")


    def open_chat_window(self):
        self.root = tk.Tk()
        self.root.title(f"{self.username}'s Chat Room")
        self.root.configure(bg=self.themes[self.theme]['bg'])

        self.chat_box = tk.Text(self.root, height=15, width=50, bg=self.themes[self.theme]['bg'], fg=self.themes[self.theme]['fg'], state="disabled")
        self.chat_box.pack(padx=10, pady=10, expand=True, fill='both')

        scrollbar = tk.Scrollbar(self.root, command=self.chat_box.yview)
        scrollbar.pack(side='right', fill='y')
        self.chat_box['yscrollcommand'] = scrollbar.set

        # Create a frame to hold the emoji button and the input box together
        input_frame = tk.Frame(self.root, bg=self.themes[self.theme]['bg'])
        input_frame.pack(side='top', fill='x', padx=10, pady=(0, 10))

        # Emoji button on the left-hand side
        self.button_emoji = tk.Button(input_frame, text="😊", command=self.open_emoji_picker, bg=self.themes[self.theme]['button_bg'], fg=self.themes[self.theme]['fg'])
        self.button_emoji.pack(side='left', padx=(0, 5))

        # Message entry next to the emoji button
        self.message_entry = tk.Entry(input_frame, width=40, font=("Arial", 12), bg=self.themes[self.theme]['entry_bg'], fg=self.themes[self.theme]['fg'])
        self.message_entry.pack(side='left', expand=True, fill='x', padx=(0, 5))

        # Bind the Enter key to send the message
        self.message_entry.bind('<Return>', lambda event: self.send_message())


        # Send button on the right-hand side
        self.send_button = tk.Button(input_frame, text="Send", command=self.send_message, font=("Arial", 12), bg=self.themes[self.theme]['button_bg'], fg=self.themes[self.theme]['fg'])
        self.send_button.pack(side='right')

        # Disconnect button below the input box
        self.disconnect_button = tk.Button(self.root, text="Disconnect", command=self.disconnect, font=("Arial", 12), bg="red", fg=self.themes[self.theme]['fg'])
        self.disconnect_button.pack(pady=(10, 0))  # Adjust the position below the input frame

        # Start a new thread to listen for messages from the server
        threading.Thread(target=self.receive_messages, daemon=True).start()

        self.root.mainloop()


    def disconnect(self):
        """Disconnect from the chat and close the window."""
        self.client_socket.close()  # Close the socket connection
        self.root.destroy()  # Close the chat window

    def open_emoji_picker(self):
        # Create a new window for the emoji picker
        emoji_window = Toplevel(self.root)
        emoji_window.title("Emoji Picker")
        emoji_window.geometry("200x150")

        emoji_list = ["😊", "😂", "😍", "😢", "😡", "👍", "👎"]
        for emoji in emoji_list:
            btn_emoji = Button(emoji_window, text=emoji, command=lambda e=emoji: self.insert_emoji(e))
            btn_emoji.pack(side='left', padx=5, pady=5)

    def insert_emoji(self, emoji):
        self.message_entry.insert(tk.END, emoji)

    def send_message(self): 
        message = self.message_entry.get()
        if message:  # Check if the message is not empty
            if message.startswith('/pm'):
                # Example: /pm recipient_username message
                parts = message.split(' ', 2)  # Split into parts
                if len(parts) < 3:
                    messagebox.showerror("Error", "Usage: /pm <username> <message>")
                    return
                recipient = parts[1]
                private_message = parts[2]
                # Prepare the private message format
                formatted_message = f"PM from {self.username} to {recipient}: {private_message}"
                # Send the private message to the server
                self.client_socket.send(f"/pm {recipient} {private_message}".encode('utf-8'))
                # Display the private message in the chat box
                self.chat_box.configure(state="normal")
                self.chat_box.insert(tk.END, f"You to {recipient}: {private_message}\n")
                self.chat_box.configure(state="disabled")
                self.chat_box.see(tk.END)  # Scroll to the end
            else:
                # Display the message in the chat box
                self.chat_box.configure(state="normal")
                self.chat_box.insert(tk.END, f"{self.username}: {message}\n")
                self.chat_box.configure(state="disabled")
                self.chat_box.see(tk.END)  # Scroll to the end
                # Send normal message to server
                self.client_socket.send(message.encode('utf-8'))

            self.message_entry.delete(0, tk.END)  # Clear the message entry


    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                self.chat_box.configure(state="normal")
                self.chat_box.insert(tk.END, message + "\n")
                self.chat_box.configure(state="disabled")
                self.chat_box.see(tk.END)  # Scroll to the end
            except:
                break


    def on_closing(self):
        self.client_socket.close()
        self.chat_window.destroy()
        self.login_window.quit()

if __name__ == "__main__":
    client = ChatClient()
