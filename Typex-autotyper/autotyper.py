import pyautogui
import time
import keyboard
import threading
import json
import os
import random
import customtkinter as ctk
from tkinter import messagebox

# Configuration & Persistence
CONFIG_FILE = "typex_config.json"

class AutoTyperPro:
    def __init__(self, root):
        self.root = root
        self.root.title("TYPEX PRO - Tactical Typing Engine")
        self.root.geometry("1000x780")
        
        # --- PREMMIUM THEME CONFIG ---
        self.bg_color = "#0B0C10"        # Deep Space
        self.card_color = "#1F2833"      # Slate Card
        self.accent_color = "#66FCF1"    # Neon Cyan
        self.text_main = "#C5C6C7"       # Soft White
        self.text_dim = "#45A29E"        # Teal Dim
        self.danger = "#FF4C4C"
        
        ctk.set_appearance_mode("dark")
        self.root.configure(fg_color=self.bg_color)
        
        self.is_running = False
        self.placeholder_active = True
        self.placeholder_text = "// PASTE YOUR CODE OR TEXT HERE...\n// PRESS 'INITIALIZE' TO START"
        
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self.root, width=280, corner_radius=0, fg_color="#121417", border_width=1, border_color="#1F2833")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(12, weight=1)

        ctk.CTkLabel(self.sidebar, text="TYPEX", font=ctk.CTkFont(size=28, weight="bold", family="Orbitron"), text_color=self.accent_color).grid(row=0, column=0, padx=25, pady=(30, 5))
        ctk.CTkLabel(self.sidebar, text="PRO EDITION", font=ctk.CTkFont(size=10, weight="bold"), text_color=self.text_dim).grid(row=1, column=0, padx=25, pady=(0, 25))

        self.create_label(self.sidebar, "ENGINE CONFIG", 12, "bold").grid(row=2, column=0, padx=25, pady=(10, 5), sticky="w")
        
        # Delay
        self.create_label(self.sidebar, "Start Delay (Seconds)", 11).grid(row=3, column=0, padx=25, pady=(10, 0), sticky="w")
        self.delay_var = ctk.StringVar(value="5")
        self.delay_entry = ctk.CTkEntry(self.sidebar, textvariable=self.delay_var, height=35, fg_color=self.bg_color, border_color=self.card_color)
        self.delay_entry.grid(row=4, column=0, padx=25, pady=(5, 10), sticky="ew")

        # Speed + Dynamic Label
        speed_header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        speed_header.grid(row=5, column=0, padx=25, pady=(5, 0), sticky="ew")
        self.create_label(speed_header, "Typing Speed", 11).pack(side="left")
        self.speed_val_lbl = ctk.CTkLabel(speed_header, text="0.050s", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.accent_color)
        self.speed_val_lbl.pack(side="right")

        self.speed_slider = ctk.CTkSlider(self.sidebar, from_=0.001, to=0.3, number_of_steps=299, 
                                          button_color=self.accent_color, button_hover_color=self.text_dim,
                                          command=self.update_speed_label)
        self.speed_slider.grid(row=6, column=0, padx=25, pady=(5, 15), sticky="ew")

        # Modes
        self.create_label(self.sidebar, "Operational Mode", 11).grid(row=7, column=0, padx=25, pady=(5, 0), sticky="w")
        self.mode_var = ctk.StringVar(value="Natural")
        self.mode_menu = ctk.CTkOptionMenu(self.sidebar, values=["Turbo", "Natural", "Stealth"], variable=self.mode_var, fg_color=self.card_color, button_color=self.card_color, dropdown_hover_color=self.text_dim)
        self.mode_menu.grid(row=8, column=0, padx=25, pady=(5, 15), sticky="ew")

        # Toggles
        self.ontop_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(self.sidebar, text="Keep on Top", variable=self.ontop_var, command=self.toggle_ontop, progress_color=self.accent_color).grid(row=9, column=0, padx=25, pady=10, sticky="w")

        self.smart_indent_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(self.sidebar, text="Auto-Indent", variable=self.smart_indent_var, progress_color=self.accent_color).grid(row=10, column=0, padx=25, pady=10, sticky="w")

        # --- MAIN PANEL ---
        self.main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Status Bar
        self.status_bar = ctk.CTkFrame(self.main_container, height=50, fg_color=self.card_color, corner_radius=10)
        self.status_bar.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.status_lbl = ctk.CTkLabel(self.status_bar, text="● SYSTEM STANDBY", text_color=self.accent_color, font=ctk.CTkFont(size=12, weight="bold", family="Inter"))
        self.status_lbl.pack(side="left", padx=20)

        # Editor with Placeholder Logic
        self.code_box = ctk.CTkTextbox(self.main_container, font=("Consolas", 12), border_width=1, border_color=self.card_color, fg_color="#0D1117", text_color="#E6EDF3", padx=15, pady=15)
        self.code_box.grid(row=1, column=0, sticky="nsew")
        self.code_box.bind("<FocusIn>", self.clear_placeholder)
        self.code_box.bind("<FocusOut>", self.add_placeholder)

        # Footer Actions
        self.footer = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.footer.grid(row=2, column=0, sticky="ew", pady=(25, 0))

        self.progress_bar = ctk.CTkProgressBar(self.footer, height=6, progress_color=self.accent_color, fg_color=self.card_color)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=(0, 20))

        self.start_btn = ctk.CTkButton(self.footer, text="INITIALIZE TYPING SEQUENCE", font=ctk.CTkFont(size=14, weight="bold"), height=55, corner_radius=12, fg_color=self.accent_color, text_color=self.bg_color, hover_color=self.text_dim, command=self.start_typing)
        self.start_btn.pack(side="left", expand=True, fill="x")

        self.stop_info = ctk.CTkLabel(self.footer, text="EMERGENCY ABORT: ESC", text_color=self.danger, font=ctk.CTkFont(size=10, weight="bold"))
        self.stop_info.pack(side="right", padx=(20, 0))

    def create_label(self, parent, text, size, weight="normal"):
        return ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=size, weight=weight, family="Inter"), text_color=self.text_main)

    def update_speed_label(self, value):
        self.speed_val_lbl.configure(text=f"{value:.3f}s")

    def clear_placeholder(self, event):
        if self.placeholder_active:
            self.code_box.delete("1.0", "end")
            self.code_box.configure(text_color="#E6EDF3")
            self.placeholder_active = False

    def add_placeholder(self, event):
        content = self.code_box.get("1.0", "end-1c")
        if not content.strip():
            self.code_box.insert("1.0", self.placeholder_text)
            self.code_box.configure(text_color=self.text_dim)
            self.placeholder_active = True

    def toggle_ontop(self):
        self.root.attributes("-topmost", self.ontop_var.get())

    def update_status(self, text, color=None):
        if not color: color = self.accent_color
        self.status_lbl.configure(text=f"● {text.upper()}", text_color=color)

    def start_typing(self):
        if self.placeholder_active: return
        code = self.code_box.get("1.0", "end-1c")
        if not code.strip(): return
        
        self.save_settings()
        self.start_btn.configure(state="disabled", text="SEQUENCE IN PROGRESS...")
        threading.Thread(target=self.typing_logic, args=(code,), daemon=True).start()

    def typing_logic(self, code):
        try: delay = int(self.delay_var.get())
        except: delay = 5
        
        base_speed = self.speed_slider.get()
        mode = self.mode_var.get()
        smart_indent = self.smart_indent_var.get()

        for i in range(delay, 0, -1):
            self.update_status(f"INITIALIZING IN {i}S", self.danger)
            time.sleep(1)

        self.update_status("SEQUENCE ACTIVE", "#4ADE80")
        lines = code.split('\n')
        total = len(lines)
        
        for idx, line in enumerate(lines):
            if keyboard.is_pressed("esc"): break
            content = line.lstrip() if smart_indent else line
            
            for char in content:
                if keyboard.is_pressed("esc"): break
                pyautogui.write(char)
                if mode == "Natural":
                    time.sleep(base_speed + random.uniform(0, 0.04))
                    if char in ".,:;": time.sleep(random.uniform(0.15, 0.4))
                elif mode == "Stealth":
                    time.sleep(base_speed + random.uniform(0.08, 0.2))
                else:
                    if base_speed > 0: time.sleep(base_speed)

            pyautogui.press("enter")
            self.progress_bar.set((idx + 1) / total)
            
        self.update_status("SYSTEM STANDBY", self.accent_color)
        self.start_btn.configure(state="normal", text="INITIALIZE TYPING SEQUENCE")
        self.progress_bar.set(0)

    def save_settings(self):
        settings = {
            "delay": self.delay_var.get(),
            "speed": self.speed_slider.get(),
            "mode": self.mode_var.get(),
            "code": "" if self.placeholder_active else self.code_box.get("1.0", "end-1c"),
            "ontop": self.ontop_var.get()
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(settings, f)

    def load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    s = json.load(f)
                    self.delay_var.set(s.get("delay", "5"))
                    self.speed_slider.set(s.get("speed", 0.05))
                    self.update_speed_label(s.get("speed", 0.05))
                    self.mode_var.set(s.get("mode", "Natural"))
                    code = s.get("code", "")
                    if code:
                        self.code_box.insert("1.0", code)
                        self.placeholder_active = False
                    else:
                        self.add_placeholder(None)
                    self.ontop_var.set(s.get("ontop", False))
                    self.toggle_ontop()
            except: self.add_placeholder(None)
        else:
            self.add_placeholder(None)

if __name__ == "__main__":
    root = ctk.CTk()
    app = AutoTyperPro(root)
    root.mainloop()
