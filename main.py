import customtkinter as ctk
import tkinter as tk
import threading
import ctypes
import time
from pynput import keyboard
from winotify import Notification, audio
from PIL import Image, ImageTk

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

MOUSEEVENT_LEFTDOWN = 0x0002
MOUSEEVENT_LEFTUP = 0x0004
MOUSEEVENT_RIGHTDOWN = 0x0008
MOUSEEVENT_RIGHTUP = 0x0010
MOUSEEVENT_MIDDLEDOWN = 0x0020
MOUSEEVENT_MIDDLEUP = 0x0040
SendInput = ctypes.windll.user32.mouse_event

def show_toast(title, msg):
    toast = Notification(
        app_id="Adrian Sybau",
        title=title,
        msg=msg
    )
    toast.set_audio(audio.Default, loop=False)
    toast.show()

class AutoClicker:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Adrian Sybau")
        self.root.geometry("350x250")
        self.root.resizable(False, False)
        self.root.attributes("-alpha", 0.95)

        # Sfondo immagine
        image = Image.open("sfondo.png").resize((350, 250))
        self.bg_image = ImageTk.PhotoImage(image)
        bg_label = ctk.CTkLabel(self.root, image=self.bg_image, text="")
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.click_delay = ctk.DoubleVar(value=0.033)
        self.mouse_button = ctk.StringVar(value="comunista")
        self.hotkey = ctk.StringVar(value="f6")
        self.running = False
        self.listener = None

        menubar = tk.Menu(self.root, bg="#1e1e1e", fg="white", activebackground="#444", activeforeground="white")
        settings_menu = tk.Menu(menubar, tearoff=0, bg="#1e1e1e", fg="white", activebackground="#444", activeforeground="white")
        settings_menu.add_command(label="Impstz", command=self.open_settings)
        settings_menu.add_separator()
        settings_menu.add_command(label="kys", command=self.root.quit)
        menubar.add_cascade(label="File", menu=settings_menu)
        self.root.config(menu=menubar)

        ctk.CTkLabel(self.root, text="Premi la hotkey per avviarmi UwU").pack(pady=10)
        ctk.CTkLabel(self.root, text="Intervallo click").pack()
        ctk.CTkEntry(self.root, textvariable=self.click_delay, width=80, justify="center").pack(pady=5)

        self.status_label = ctk.CTkLabel(self.root, text="uff :(", text_color="red")
        self.status_label.pack(pady=10)

        self.start_hotkey_listener()

    def click_loop(self):
        button_map = {
            "comunista": (MOUSEEVENT_LEFTDOWN, MOUSEEVENT_LEFTUP),
            "zack": (MOUSEEVENT_RIGHTDOWN, MOUSEEVENT_RIGHTUP),
            "nga": (MOUSEEVENT_MIDDLEDOWN, MOUSEEVENT_MIDDLEUP)
        }
        while self.running:
            down, up = button_map.get(self.mouse_button.get(), (MOUSEEVENT_LEFTDOWN, MOUSEEVENT_LEFTUP))
            SendInput(down, 0, 0, 0, 0)
            SendInput(up, 0, 0, 0, 0)
            delay = max(self.click_delay.get(), 0.033)
            time.sleep(delay)

    def toggle_clicking(self):
        if not self.running:
            self.running = True
            self.status_label.configure(text="YAYYAY:3", text_color="pink")
            threading.Thread(target=self.click_loop, daemon=True).start()
            show_toast("Adrian Sybau", "Clicker avviato")
        else:
            self.running = False
            self.status_label.configure(text="uffa :(", text_color="red")
            show_toast("Adrian Sybau", "Clicker fermato")

    def start_hotkey_listener(self):
        if self.listener:
            self.listener.stop()
        target = self.hotkey.get().lower()
        def on_press(key):
            try:
                if hasattr(key, 'char') and key.char and key.char.lower() == target:
                    self.toggle_clicking()
                elif hasattr(key, 'name') and key.name.lower() == target:
                    self.toggle_clicking()
                elif str(key).replace("Key.", "").lower() == target:
                    self.toggle_clicking()
            except:
                pass
        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()

    def open_settings(self):
        win = ctk.CTkToplevel(self.root)
        win.title("Impstz")
        win.geometry("300x200")

        ctk.CTkLabel(win, text="impstz", font=("Segoe UI", 10, "bold")).pack(pady=10)

        ctk.CTkLabel(win, text="tasto mouse").pack()
        ctk.CTkComboBox(win, variable=self.mouse_button, values=["comunista", "zack", "nga"]).pack(pady=5)

        ctk.CTkLabel(win, text="tasto da usà:").pack(pady=5)
        entry_hotkey = ctk.CTkEntry(win, textvariable=self.hotkey, width=80, justify="center")
        entry_hotkey.pack(pady=5)

        def on_focus(event):
            entry_hotkey.delete(0, ctk.END)
            entry_hotkey.insert(0, "Premi un tasto...")
            listener = None
            def on_key_press(key):
                nonlocal listener
                try:
                    key_name = key.char if hasattr(key, "char") and key.char else key.name
                    self.hotkey.set(key_name.lower())
                    entry_hotkey.delete(0, ctk.END)
                    entry_hotkey.insert(0, key_name)
                    self.start_hotkey_listener()
                    if listener:
                        listener.stop()
                except:
                    pass
            listener = keyboard.Listener(on_press=on_key_press)
            listener.start()

        entry_hotkey.bind("<FocusIn>", on_focus)
        ctk.CTkButton(win, text="Chiudi", command=win.destroy).pack(pady=10)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AutoClicker()
    app.run()
