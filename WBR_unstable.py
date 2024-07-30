import tkinter as tk
from tkinter import messagebox
import requests
import pyautogui
import threading
import time
import keyboard

class WordViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UNSTABLE")
        self.root.geometry("300x150")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)

        self.root.bind("<Button-1>", self.on_start_drag)
        self.root.bind("<B1-Motion>", self.on_drag)

        self.status_label = tk.Label(root, text="Press '`' to start/stop script")
        self.status_label.pack(pady=10)

        self.start_stop_button = tk.Button(root, text="Start", command=self.toggle_script)
        self.start_stop_button.pack(pady=5)

        self.words = []
        self.current_index = 0
        self.is_running = False
        self.line_count = 0
        self.base_delay = 2.0
        self.additional_delay = 0.75

        self.load_text_from_url()

        self.listener_thread = threading.Thread(target=self.listen_for_keypress)
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def on_start_drag(self, event):
        self.x = event.x
        self.y = event.y

    def on_drag(self, event):
        delta_x = event.x - self.x
        delta_y = event.y - self.y
        new_x = self.root.winfo_x() + delta_x
        new_y = self.root.winfo_y() + delta_y
        self.root.geometry(f"+{new_x}+{new_y}")

    def load_text_from_url(self):
        url = "https://raw.githubusercontent.com/ashertenenbaum/whatbeatsrock-automation/main/unstable_wordlist"
        try:
            response = requests.get(url)
            response.raise_for_status()
            self.words = [line.strip() for line in response.text.splitlines() if line.strip()]
            self.current_index = 0
            self.line_count = 0
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to load text from URL: {e}")

    def show_next_word(self):
        if self.words:
            if self.current_index < len(self.words):
                word = self.words[self.current_index]
                self.current_index += 1
                self.line_count += 1

                pyautogui.typewrite(word, interval=0.05)
                pyautogui.press('enter')

                if self.line_count % 35 == 0:
                    delay = self.base_delay + self.additional_delay
                else:
                    delay = self.base_delay

                time.sleep(delay)
                pyautogui.click()

            if self.current_index >= len(self.words):
                self.is_running = False
                self.status_label.config(text="Stopped")
                self.start_stop_button.config(text="Start")

    def listen_for_keypress(self):
        while True:
            if keyboard.is_pressed('`'):
                self.toggle_script()
                while keyboard.is_pressed('`'):
                    time.sleep(0.1)
            time.sleep(0.1)

    def toggle_script(self):
        if self.is_running:
            self.is_running = False
            self.status_label.config(text="Stopped")
            self.start_stop_button.config(text="Start")
        else:
            self.is_running = True
            self.status_label.config(text="Running")
            self.start_stop_button.config(text="Stop")
            threading.Thread(target=self.run_script).start()

    def run_script(self):
        while self.is_running:
            self.show_next_word()
            time.sleep(0.1)

    def on_closing(self):
        self.is_running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = WordViewerApp(root)
    root.mainloop()
