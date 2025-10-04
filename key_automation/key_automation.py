import tkinter as tk
from tkinter import ttk, messagebox, font
import threading
import time
import random
import string
import keyboard
import pyautogui
from pynput import keyboard as pynput_keyboard
from pynput.keyboard import Key, Listener
import json
import os

class KeyAutomationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Key Automation Tool - Entertainment Purposes")
        self.root.geometry("800x900")
        self.root.configure(bg='#2b2b2b')
        
        # Variables
        self.is_running = False
        self.is_toggle_mode = False
        self.toggle_state = False
        self.activation_key = 'f1'
        self.key_listener = None
        
        # Character generation settings
        self.use_letters = tk.BooleanVar(value=True)
        self.use_numbers = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=False)
        self.use_arrows = tk.BooleanVar(value=False)
        self.custom_chars = tk.StringVar(value="")
        self.exclude_chars = tk.StringVar(value="")
        
        # Spacing and formatting
        self.use_dashes = tk.BooleanVar(value=True)
        self.dash_frequency = tk.IntVar(value=4)
        self.dash_gap_count = tk.IntVar(value=3)  # How many gaps to create
        self.space_frequency = tk.IntVar(value=0)
        
        # Deletion settings
        self.auto_delete = tk.BooleanVar(value=True)
        self.delete_delay = tk.DoubleVar(value=0.5)
        self.use_word_delete = tk.BooleanVar(value=True)  # Default to word deletion
        self.word_delete_count = tk.IntVar(value=1)
        # Auto-calculated sequence length (no manual setting needed)
        
        # Timing settings
        self.key_delay = tk.DoubleVar(value=0.05)
        self.activation_delay = tk.DoubleVar(value=0.1)
        
        # Mode settings
        self.activation_mode = tk.StringVar(value="hold")  # "hold" or "toggle"
        
        self.setup_ui()
        self.start_key_listener()
        
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="Key Automation Tool", 
                              font=('Arial', 16, 'bold'), fg='#ffffff', bg='#2b2b2b')
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        # Character Settings Tab
        char_frame = ttk.Frame(notebook)
        notebook.add(char_frame, text="Character Settings")
        self.setup_character_tab(char_frame)
        
        # Formatting Tab
        format_frame = ttk.Frame(notebook)
        notebook.add(format_frame, text="Formatting")
        self.setup_formatting_tab(format_frame)
        
        # Deletion Tab
        delete_frame = ttk.Frame(notebook)
        notebook.add(delete_frame, text="Deletion & Timing")
        self.setup_deletion_tab(delete_frame)
        
        # Controls Tab
        control_frame = ttk.Frame(notebook)
        notebook.add(control_frame, text="Controls")
        self.setup_controls_tab(control_frame)
        
        # Instructions Tab
        instructions_frame = ttk.Frame(notebook)
        notebook.add(instructions_frame, text="How to Use")
        self.setup_instructions_tab(instructions_frame)
        
        # Status and main controls
        self.setup_status_controls(main_frame)
        
    def setup_character_tab(self, parent):
        # Character type selection
        char_group = ttk.LabelFrame(parent, text="Character Types", padding=10)
        char_group.pack(fill='x', padx=10, pady=5)
        
        ttk.Checkbutton(char_group, text="Letters (a-z, A-Z)", variable=self.use_letters).pack(anchor='w')
        ttk.Checkbutton(char_group, text="Numbers (0-9)", variable=self.use_numbers).pack(anchor='w')
        ttk.Checkbutton(char_group, text="Symbols (!@#$%^&*)", variable=self.use_symbols).pack(anchor='w')
        ttk.Checkbutton(char_group, text="Arrow Keys (↑↓←→)", variable=self.use_arrows).pack(anchor='w')
        
        # Custom characters
        custom_frame = ttk.Frame(char_group)
        custom_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Label(custom_frame, text="Custom Characters:").pack(anchor='w')
        ttk.Entry(custom_frame, textvariable=self.custom_chars, width=50).pack(fill='x', pady=(5, 0))
        
        ttk.Label(custom_frame, text="Exclude Characters:").pack(anchor='w', pady=(10, 0))
        ttk.Entry(custom_frame, textvariable=self.exclude_chars, width=50).pack(fill='x', pady=(5, 0))
        
    def setup_formatting_tab(self, parent):
        # Spacing options
        spacing_group = ttk.LabelFrame(parent, text="Spacing & Formatting", padding=10)
        spacing_group.pack(fill='x', padx=10, pady=5)
        
        ttk.Checkbutton(spacing_group, text="Use dashes (-)", variable=self.use_dashes).pack(anchor='w')
        
        dash_frame = ttk.Frame(spacing_group)
        dash_frame.pack(fill='x', pady=(5, 0))
        ttk.Label(dash_frame, text="Characters per gap:").pack(side='left')
        ttk.Spinbox(dash_frame, from_=2, to=10, textvariable=self.dash_frequency, width=5).pack(side='left', padx=(5, 5))
        
        gap_frame = ttk.Frame(spacing_group)
        gap_frame.pack(fill='x', pady=(5, 0))
        ttk.Label(gap_frame, text="Number of gaps:").pack(side='left')
        ttk.Spinbox(gap_frame, from_=1, to=10, textvariable=self.dash_gap_count, width=5).pack(side='left', padx=(5, 5))
        
        space_frame = ttk.Frame(spacing_group)
        space_frame.pack(fill='x', pady=(5, 0))
        ttk.Label(space_frame, text="Space every").pack(side='left')
        ttk.Spinbox(space_frame, from_=0, to=20, textvariable=self.space_frequency, width=5).pack(side='left', padx=(5, 5))
        ttk.Label(space_frame, text="characters (0 = no spaces)").pack(side='left')
        
    def setup_deletion_tab(self, parent):
        # Auto-deletion settings
        delete_group = ttk.LabelFrame(parent, text="Auto-Deletion Settings", padding=10)
        delete_group.pack(fill='x', padx=10, pady=5)
        
        ttk.Checkbutton(delete_group, text="Auto-delete after typing complete sequence", variable=self.auto_delete).pack(anchor='w')
        
        # Word deletion option
        ttk.Checkbutton(delete_group, text="Use Ctrl+Backspace (word deletion)", variable=self.use_word_delete).pack(anchor='w', pady=(10, 0))
        
        word_delete_frame = ttk.Frame(delete_group)
        word_delete_frame.pack(fill='x', pady=(5, 0))
        ttk.Label(word_delete_frame, text="Delete").pack(side='left')
        ttk.Spinbox(word_delete_frame, from_=1, to=20, textvariable=self.word_delete_count, width=5).pack(side='left', padx=(5, 5))
        ttk.Label(word_delete_frame, text="words").pack(side='left')
        
        # Auto-calculated info
        info_label = ttk.Label(delete_group, text="Sequence length is auto-calculated based on your settings", 
                              font=('Arial', 9), foreground='#666666')
        info_label.pack(anchor='w', pady=(10, 0))
        
        delay_frame = ttk.Frame(delete_group)
        delay_frame.pack(fill='x', pady=(5, 0))
        ttk.Label(delay_frame, text="Delete delay:").pack(side='left')
        ttk.Spinbox(delay_frame, from_=0.01, to=2.0, increment=0.01, textvariable=self.delete_delay, width=8).pack(side='left', padx=(5, 5))
        ttk.Label(delay_frame, text="seconds").pack(side='left')
        
        
        # Timing settings
        timing_group = ttk.LabelFrame(parent, text="Timing Settings", padding=10)
        timing_group.pack(fill='x', padx=10, pady=5)
        
        key_delay_frame = ttk.Frame(timing_group)
        key_delay_frame.pack(fill='x')
        ttk.Label(key_delay_frame, text="Key delay:").pack(side='left')
        ttk.Spinbox(key_delay_frame, from_=0.001, to=1.0, increment=0.001, textvariable=self.key_delay, width=8).pack(side='left', padx=(5, 5))
        ttk.Label(key_delay_frame, text="seconds").pack(side='left')
        
        activation_delay_frame = ttk.Frame(timing_group)
        activation_delay_frame.pack(fill='x', pady=(5, 0))
        ttk.Label(activation_delay_frame, text="Activation delay:").pack(side='left')
        ttk.Spinbox(activation_delay_frame, from_=0.01, to=2.0, increment=0.01, textvariable=self.activation_delay, width=8).pack(side='left', padx=(5, 5))
        ttk.Label(activation_delay_frame, text="seconds").pack(side='left')
        
    def setup_controls_tab(self, parent):
        # Activation mode
        mode_group = ttk.LabelFrame(parent, text="Activation Mode", padding=10)
        mode_group.pack(fill='x', padx=10, pady=5)
        
        ttk.Radiobutton(mode_group, text="Hold Mode (press and hold to activate)", 
                       variable=self.activation_mode, value="hold").pack(anchor='w')
        ttk.Radiobutton(mode_group, text="Toggle Mode (press once to start/stop)", 
                       variable=self.activation_mode, value="toggle").pack(anchor='w')
        
        # Key binding
        key_group = ttk.LabelFrame(parent, text="Key Binding", padding=10)
        key_group.pack(fill='x', padx=10, pady=5)
        
        key_frame = ttk.Frame(key_group)
        key_frame.pack(fill='x')
        ttk.Label(key_frame, text="Activation Key:").pack(side='left')
        key_combo = ttk.Combobox(key_frame, textvariable=tk.StringVar(value=self.activation_key), 
                                values=['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
                                       'insert', 'home', 'end', 'page_up', 'page_down', 'pause', 'print_screen'], width=10)
        key_combo.pack(side='left', padx=(5, 5))
        key_combo.bind('<<ComboboxSelected>>', lambda e: setattr(self, 'activation_key', key_combo.get()))
        
        # Keyboard layout button
        layout_btn = ttk.Button(key_group, text="Show Keyboard Layout", command=self.show_keyboard_layout)
        layout_btn.pack(pady=(10, 0))
    
    def setup_instructions_tab(self, parent):
        """Setup instructions tab with simple usage guide"""
        instructions_text = """
🎯 QUICK START GUIDE:

1. SETUP (First time only):
   • Go to "Character Settings" tab
   • Choose which characters to generate (letters, numbers, symbols)
   • Go to "Deletion & Timing" tab
   • Choose your activation key in "Controls" tab
   • Sequence length is auto-calculated!

2. HOW TO USE:
   • Press your activation key (default: F1) to start/stop
   • The tool will type a complete sequence, then delete it
   • Repeat this cycle automatically

3. MODES:
   • HOLD MODE: Hold the key to run, release to stop
   • TOGGLE MODE: Press once to start, press again to stop

4. WHAT IT DOES:
   • Types random characters (like: aB3-xY9!mK2...)
   • Auto-calculates how many characters to type
   • Waits a moment, then deletes everything
   • Starts typing again
   • Repeats this cycle

5. CUSTOMIZATION:
   • Add dashes every few characters
   • Use Ctrl+Backspace to delete whole words
   • Adjust timing and delays
   • Choose which characters to include/exclude

💡 TIP: Start with default settings, then customize as needed!
        """
        
        # Create scrollable text widget
        text_frame = tk.Frame(parent)
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap='word', font=('Arial', 10), 
                            bg='#f0f0f0', fg='#333333', padx=10, pady=10)
        text_widget.pack(fill='both', expand=True)
        text_widget.insert('1.0', instructions_text)
        text_widget.config(state='disabled')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
        scrollbar.pack(side='right', fill='y')
        text_widget.configure(yscrollcommand=scrollbar.set)
        
    def setup_status_controls(self, parent):
        # Status frame
        status_frame = tk.Frame(parent, bg='#2b2b2b')
        status_frame.pack(fill='x', pady=(10, 0))
        
        # Status label
        self.status_label = tk.Label(status_frame, text="Status: Ready", 
                                   font=('Arial', 12, 'bold'), fg='#00ff00', bg='#2b2b2b')
        self.status_label.pack(side='left')
        
        # Control buttons
        button_frame = tk.Frame(status_frame, bg='#2b2b2b')
        button_frame.pack(side='right')
        
        self.start_btn = tk.Button(button_frame, text="Start", command=self.start_automation,
                                 bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'))
        self.start_btn.pack(side='left', padx=(0, 5))
        
        self.stop_btn = tk.Button(button_frame, text="Stop", command=self.stop_automation,
                                bg='#f44336', fg='white', font=('Arial', 10, 'bold'), state='disabled')
        self.stop_btn.pack(side='left')
        
    def show_keyboard_layout(self):
        """Show keyboard layout window"""
        layout_window = tk.Toplevel(self.root)
        layout_window.title("Keyboard Layout")
        layout_window.geometry("800x300")
        layout_window.configure(bg='#1e1e1e')
        
        # Keyboard layout
        keyboard_frame = tk.Frame(layout_window, bg='#1e1e1e')
        keyboard_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Create keyboard layout
        self.create_keyboard_layout(keyboard_frame)
        
    def create_keyboard_layout(self, parent):
        """Create visual keyboard layout"""
        # Row 1: Numbers
        row1 = tk.Frame(parent, bg='#1e1e1e')
        row1.pack(pady=5)
        
        for i in range(10):
            btn = tk.Button(row1, text=str(i), width=3, height=2, 
                          bg='#404040', fg='white', font=('Arial', 10))
            btn.pack(side='left', padx=2)
        
        # Row 2: QWERTY
        row2 = tk.Frame(parent, bg='#1e1e1e')
        row2.pack(pady=5)
        
        qwerty = "QWERTYUIOP"
        for char in qwerty:
            btn = tk.Button(row2, text=char, width=3, height=2,
                          bg='#404040', fg='white', font=('Arial', 10))
            btn.pack(side='left', padx=2)
        
        # Row 3: ASDF
        row3 = tk.Frame(parent, bg='#1e1e1e')
        row3.pack(pady=5)
        
        asdf = "ASDFGHJKL"
        for char in asdf:
            btn = tk.Button(row3, text=char, width=3, height=2,
                          bg='#404040', fg='white', font=('Arial', 10))
            btn.pack(side='left', padx=2)
        
        # Row 4: ZXCV
        row4 = tk.Frame(parent, bg='#1e1e1e')
        row4.pack(pady=5)
        
        zxcv = "ZXCVBNM"
        for char in zxcv:
            btn = tk.Button(row4, text=char, width=3, height=2,
                          bg='#404040', fg='white', font=('Arial', 10))
            btn.pack(side='left', padx=2)
        
        # Special keys
        special_frame = tk.Frame(parent, bg='#1e1e1e')
        special_frame.pack(pady=5)
        
        special_keys = ["SPACE", "ENTER", "TAB", "SHIFT", "CTRL", "ALT"]
        for key in special_keys:
            btn = tk.Button(special_frame, text=key, width=8, height=2,
                          bg='#606060', fg='white', font=('Arial', 9))
            btn.pack(side='left', padx=2)
        
        # Arrow keys
        arrow_frame = tk.Frame(parent, bg='#1e1e1e')
        arrow_frame.pack(pady=5)
        
        arrows = ["↑", "↓", "←", "→"]
        for arrow in arrows:
            btn = tk.Button(arrow_frame, text=arrow, width=3, height=2,
                          bg='#505050', fg='white', font=('Arial', 12))
            btn.pack(side='left', padx=2)
    
    def start_key_listener(self):
        """Start listening for activation key"""
        def on_press(key):
            try:
                if hasattr(key, 'name'):
                    key_name = key.name
                else:
                    key_name = key.char
                
                # Ignore modifier keys and special keys that shouldn't trigger activation
                ignore_keys = ['shift', 'ctrl', 'alt', 'cmd', 'win', 'menu', 'caps_lock', 'num_lock', 'scroll_lock']
                
                if key_name in ignore_keys:
                    return
                
                if key_name == self.activation_key:
                    if self.activation_mode.get() == "hold":
                        if not self.is_running:
                            self.start_automation()
                    elif self.activation_mode.get() == "toggle":
                        if not self.is_running:
                            self.start_automation()
                        else:
                            self.stop_automation()
                            
            except AttributeError:
                pass
        
        def on_release(key):
            try:
                if hasattr(key, 'name'):
                    key_name = key.name
                else:
                    key_name = key.char
                
                # Ignore modifier keys and special keys that shouldn't trigger activation
                ignore_keys = ['shift', 'ctrl', 'alt', 'cmd', 'win', 'menu', 'caps_lock', 'num_lock', 'scroll_lock']
                
                if key_name in ignore_keys:
                    return
                
                if key_name == self.activation_key and self.activation_mode.get() == "hold" and self.is_running:
                    self.stop_automation()
                    
            except AttributeError:
                pass
        
        self.key_listener = Listener(on_press=on_press, on_release=on_release)
        self.key_listener.start()
    
    def generate_character(self):
        """Generate a random character based on settings"""
        chars = []
        
        if self.use_letters.get():
            chars.extend(string.ascii_letters)
        
        if self.use_numbers.get():
            chars.extend(string.digits)
        
        if self.use_symbols.get():
            chars.extend("!@#$%^&*()_+-=[]{}|;':\",./<>?")
        
        if self.use_arrows.get():
            chars.extend(['up', 'down', 'left', 'right'])
        
        if self.custom_chars.get():
            chars.extend(list(self.custom_chars.get()))
        
        # Remove excluded characters
        if self.exclude_chars.get():
            for char in self.exclude_chars.get():
                if char in chars:
                    chars.remove(char)
        
        if not chars:
            return 'a'  # Default fallback
        
        return random.choice(chars)
    
    def type_character(self, char):
        """Type a character with proper handling"""
        if char in ['up', 'down', 'left', 'right']:
            pyautogui.press(char)
        else:
            pyautogui.write(char)
    
    def automation_loop(self):
        """Main automation loop"""
        while self.is_running:
            try:
                # First phase: Type a complete sequence
                sequence_length = self.get_sequence_length()
                typed_chars = 0
                
                # Type the complete sequence first
                if self.use_dashes.get():
                    # Type with dashes: create exact number of gaps
                    chars_per_gap = self.dash_frequency.get()
                    num_gaps = self.dash_gap_count.get()
                    
                    for gap_num in range(num_gaps):
                        if not self.is_running:
                            break
                        # Type characters for this gap
                        for char_num in range(chars_per_gap):
                            if not self.is_running:
                                break
                            char = self.generate_character()
                            self.type_character(char)
                            time.sleep(self.key_delay.get())
                        
                        # Add dash after each gap (except the last one)
                        if gap_num < num_gaps - 1:
                            pyautogui.write('-')
                            time.sleep(self.key_delay.get())
                else:
                    # Type without dashes: just random characters for the full length
                    for i in range(sequence_length):
                        if not self.is_running:
                            break
                        char = self.generate_character()
                        self.type_character(char)
                        
                        # Add spaces if enabled
                        if self.space_frequency.get() > 0 and (i + 1) % self.space_frequency.get() == 0:
                            pyautogui.write(' ')
                        
                        time.sleep(self.key_delay.get())
                
                # Second phase: Delete everything if auto-delete is enabled
                if self.auto_delete.get() and self.is_running:
                    time.sleep(self.delete_delay.get())  # Pause before deleting
                    
                    # Use Ctrl+Backspace for word deletion (more reliable)
                    for _ in range(self.word_delete_count.get()):
                        if not self.is_running:
                            break
                        pyautogui.hotkey('ctrl', 'backspace')
                        time.sleep(0.01)
                
                # Simple pause before next cycle
                time.sleep(self.activation_delay.get())
                
            except Exception as e:
                print(f"Error in automation loop: {e}")
                break
    
    def get_sequence_length(self):
        """Auto-calculate sequence length based on settings"""
        if self.use_dashes.get():
            chars_per_gap = self.dash_frequency.get()
            num_gaps = self.dash_gap_count.get()
            # Calculate: (chars_per_gap * num_gaps) + (num_gaps - 1 dashes)
            return (chars_per_gap * num_gaps) + (num_gaps - 1)
        else:
            # When no dashes, use the same calculation but without dashes
            chars_per_gap = self.dash_frequency.get()
            num_gaps = self.dash_gap_count.get()
            # Just characters, no dashes: chars_per_gap * num_gaps
            return chars_per_gap * num_gaps
    
    def start_automation(self):
        """Start the automation"""
        if not self.is_running:
            self.is_running = True
            self.char_count = 0
            self.space_count = 0
            
            self.status_label.config(text="Status: Running", fg='#00ff00')
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            
            # Start automation in separate thread
            self.automation_thread = threading.Thread(target=self.automation_loop, daemon=True)
            self.automation_thread.start()
    
    def stop_automation(self):
        """Stop the automation"""
        self.is_running = False
        self.status_label.config(text="Status: Stopped", fg='#ff0000')
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
    
    def on_closing(self):
        """Handle application closing"""
        self.is_running = False
        if self.key_listener:
            self.key_listener.stop()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = KeyAutomationApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
