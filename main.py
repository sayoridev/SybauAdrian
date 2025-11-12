import customtkinter as ctk
import tkinter as tk
import threading
import ctypes
import time
from pynput import keyboard
from winotify import Notification, audio
from PIL import Image, ImageTk
from pathlib import Path
import winsound
import sys
from tkinter import filedialog
import pystray

def show_toast(title, msg):
    icon_path = Path("settings.ico")
    toast = Notification(
        app_id="Microsoft.Windows.Explorer", 
        title=title,
        msg=msg,
        icon=str(icon_path) if icon_path.exists() else None
    )
    toast.set_audio(audio.Default, loop=False)
    toast.show()

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) / relative_path
    return Path(relative_path)

def set_taskbar_icon(root, ico_filename):
    ico_path = Path(ico_filename)
    if ico_path.exists():
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        hicon = ctypes.windll.user32.LoadImageW(0, str(ico_path), 1, 0, 0, 0x00000010 | 0x00000080)
        ctypes.windll.user32.SendMessageW(hwnd, 0x80, 0, hicon)
        ctypes.windll.user32.SendMessageW(hwnd, 0x80, 1, hicon)

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
    icon_path = resource_path("settings.ico")
    toast = Notification(
        app_id="Adrian Sybau",
        title=title,
        msg=msg,
        icon=str(icon_path) if icon_path.exists() else None
    )
    toast.set_audio(audio.Default, loop=False)
    toast.show()



class AutoClicker:
    def __init__(self):
        self.logs = []
        self.root = ctk.CTk()
        self.root.title("Adrian Sybau")
        self.root.geometry("350x250")
        self.root.resizable(False, False)
        self.root.attributes("-alpha", 0.95)

        icon_path = resource_path("settings.ico")
        if icon_path.exists():
            self.root.iconbitmap(str(icon_path))
            set_taskbar_icon(self.root, icon_path)

        bg_path = resource_path("sfondo.png")
        if bg_path.exists():
            image = Image.open(bg_path).resize((350, 250))
            self.bg_image = ImageTk.PhotoImage(image)
            bg_label = ctk.CTkLabel(self.root, image=self.bg_image, text="")
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.click_delay = ctk.DoubleVar(value=0.033)
        self.mouse_button = ctk.StringVar(value="comunista")
        self.hotkey = ctk.StringVar(value="f6")
        self.running = False
        self.listener = None

        menubar = tk.Menu(self.root, bg="#1e1e1e", fg="white",
                          activebackground="#444", activeforeground="white")
        settings_menu = tk.Menu(menubar, tearoff=0, bg="#1e1e1e", fg="white",
                                activebackground="#444", activeforeground="white")
        settings_menu.add_command(label="Impstz", command=self.open_settings)
        settings_menu.add_command(label="Log", command=self.open_log_window)
        settings_menu.add_separator()
        settings_menu.add_command(label="Esci", command=self.root.quit)
        menubar.add_cascade(label="File", menu=settings_menu)
        self.root.config(menu=menubar)

        ctk.CTkLabel(self.root, text="Premi la hotkey (default f6) per avviarmi UwU").pack(pady=10)
        ctk.CTkLabel(self.root, text="Intervallo click").pack()
        ctk.CTkEntry(self.root, textvariable=self.click_delay, width=80, justify="center").pack(pady=5)

        self.status_label = ctk.CTkLabel(self.root, text="Inattivo", text_color="red")
        self.status_label.pack(pady=10)

        self.start_hotkey_listener()
        self.start_tray()

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
            time.sleep(max(self.click_delay.get(), 0.033))

    def toggle_clicking(self):
        sound_path = resource_path("sound.wav")
        if not self.running:
            self.running = True
            self.status_label.configure(text="Attivo", text_color="pink")
            threading.Thread(target=self.click_loop, daemon=True).start()
            show_toast("Adrian Sybau", "vai a farmare sybau adrian")
            self.add_log("Clicker Avviato")
            if sound_path.exists():
                winsound.PlaySound(str(sound_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            self.running = False
            self.status_label.configure(text="Inattivo", text_color="red")
            show_toast("Adrian Sybau", "gnegne porcodio")
            self.add_log("Clicker Fermato")
            if sound_path.exists():
                winsound.PlaySound(str(sound_path), winsound.SND_FILENAME | winsound.SND_ASYNC)

    def add_log(self, msg):
        timestamp = time.strftime("%H:%M:%S")
        entry = f"[{timestamp}] {msg}"
        self.logs.append(entry)

        if hasattr(self, "log_text") and self.log_text.winfo_exists():
            self.log_text.configure(state="normal")
            self.log_text.insert(tk.END, entry + "\n")
            self.log_text.configure(state="disabled")
            self.log_text.see(tk.END)

    def start_tray(self):
        icon_path = resource_path("settings.ico")
        if icon_path.exists():
            icon_image = Image.open(icon_path)
        else:
            icon_image = Image.new("RGB", (64, 64), color="white") #fallbac

        menu = pystray.Menu(
            pystray.MenuItem("Avvia/stoppa clicker", lambda: self.root.after(0, self.toggle_clicking)),
            pystray.MenuItem("Apri app pls", lambda: self.root.after(0, self.root.deiconify)),
            pystray.MenuItem("kys", lambda: self.root.after(0, self.root.quit))
        )

        self.tray_icon = pystray.Icon("AdrianSybau", icon_image, "Adrian Sybau", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def open_log_window(self):
        win = ctk.CTkToplevel(self.root)
        win.title("Log")
        win.geometry("400x300")
        win.attributes("-alpha", 0.95)

        self.log_text = tk.Text(win, state="disabled", wrap="word")
        self.log_text.pack(expand=True, fill="both", padx=5, pady=5)

        for line in self.logs:
            self.log_text.configure(state="normal")
            self.log_text.insert(tk.END, line + "\n")
            self.log_text.configure(state="disabled")

        def save_logs():
            path = filedialog.asksaveasfile(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if path:
                with open(path.name, "w", encoding="utf-8") as f:
                    f.write("\n".join(self.logs))

        ctk.CTkButton(win, text="Salva in .txt", command=save_logs).pack(pady=5)

    def start_hotkey_listener(self):
        if self.listener:
            self.listener.stop()
        self.listener = keyboard.Listener(on_press=self.on_hotkey_press)
        self.listener.daemon = True
        self.listener.start()

    def on_hotkey_press(self, key):
        try:
            if hasattr(key, "char") and key.char:
                key_name = key.char.lower()
            elif hasattr(key, "name") and key.name:
                key_name = key.name.lower()
            else:
                return
            if key_name == self.hotkey.get().lower():
                self.root.after(0, self.toggle_clicking)
        except:
            pass

    def open_settings(self):
        win = ctk.CTkToplevel(self.root)
        win.title("Impostazioni")
        win.geometry("300x200")
        win.attributes("-alpha", 0.95)

        icon_path = resource_path("settings.ico")
        if icon_path.exists():
            win.iconbitmap(str(icon_path))

        ctk.CTkLabel(win, text="Tasto mouse").pack(pady=5)
        ctk.CTkComboBox(win, variable=self.mouse_button, values=["comunista", "zack", "nga"]).pack(pady=5)
        ctk.CTkLabel(win, text="Hotkey").pack(pady=5)
        entry_hotkey = ctk.CTkEntry(win, textvariable=self.hotkey, width=80, justify="center")
        entry_hotkey.pack(pady=5)

        def on_focus(event):
            entry_hotkey.delete(0, ctk.END)
            entry_hotkey.insert(0, "Premi un tasto...")

            def on_key_press(key):
                try:
                    key_name = key.char if hasattr(key, "char") and key.char else key.name
                    self.hotkey.set(key_name.lower())
                    entry_hotkey.delete(0, ctk.END)
                    entry_hotkey.insert(0, key_name)
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
