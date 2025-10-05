import tkinter as tk
from tkinter import ttk, messagebox, font
import threading
import time
import random
import string
import math
import keyboard
import pyautogui
from pynput import keyboard as pynput_keyboard
from pynput.keyboard import Key, Listener
import json
import os

class KeyAutomationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Key Automation Tool")
        # smaller, more compact default size
        self.root.geometry("620x640")
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
        # Press Enter option
        self.press_enter_after = tk.BooleanVar(value=False)
        # Auto-calculated sequence length (no manual setting needed)
        
        # Timing settings
        # key_delay is the per-key delay in seconds. Provide a UI scale for chars/sec
        self.key_delay = tk.DoubleVar(value=0.05)
        # Typing speed in characters per second (derived UI control)
        self.typing_speed = tk.DoubleVar(value=20.0)  # chars/sec (convenience)
        # max allowed CPS (keep one source of truth)
        self.MAX_CPS = 10000.0
        # min allowed CPS (for logarithmic slider mapping)
        self.MIN_CPS = 0.1

        # Slider backing value (0.0..1.0) mapped logarithmically to CPS for smooth feel
        self.typing_speed_slider = tk.DoubleVar(value=0.5)
        try:
            # initialize slider position based on current typing_speed
            cps = float(self.typing_speed.get())
            t = (math.log(max(self.MIN_CPS, cps)) - math.log(self.MIN_CPS)) / (math.log(self.MAX_CPS) - math.log(self.MIN_CPS))
            self.typing_speed_slider.set(max(0.0, min(1.0, t)))
        except Exception:
            pass
        # Pause between full cycles (previously "activation_delay")
        self.pause_between_cycles = tk.DoubleVar(value=0.1)
        # Pause after pressing Enter (if enabled)
        self.post_enter_delay = tk.DoubleVar(value=0.05)
        
        # Mode settings
        self.activation_mode = tk.StringVar(value="hold")  # "hold" or "toggle"
        # internal guard to prevent recursion when syncing speed vars
        self._speed_update_in_progress = False

        self.setup_ui()
        # attach variable traces that rely on widgets created in setup_ui
        self._attach_var_traces()

        self.start_key_listener()
        # Speed up pyautogui internal pause so high CPS possible
        try:
            pyautogui.PAUSE = 0
        except Exception:
            pass
        
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Title (smaller)
        title_label = tk.Label(main_frame, text="Key Automation Tool",
                              font=('Arial', 13, 'bold'), fg='#ffffff', bg='#2b2b2b')
        title_label.pack(pady=(0, 12))

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
        notebook.add(delete_frame, text="Deletion")
        self.setup_deletion_tab(delete_frame)

        # Timing Tab
        timing_frame = ttk.Frame(notebook)
        notebook.add(timing_frame, text="Timing")
        self.setup_timing_tab(timing_frame)

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

    # Press Enter option was moved to the Deletion tab to group with Auto-delete
        
    def setup_deletion_tab(self, parent):
        # Auto-deletion settings
        delete_group = ttk.LabelFrame(parent, text="Auto-Deletion Settings", padding=10)
        delete_group.pack(fill='x', padx=10, pady=5)
        # Place Press Enter and Auto-delete side-by-side with a hint label
        action_frame = ttk.Frame(delete_group)
        action_frame.pack(fill='x', pady=(2,6))

        self.press_enter_cb = ttk.Checkbutton(action_frame, text="Press Enter", variable=self.press_enter_after)
        self.press_enter_cb.pack(side='left', padx=(0,10))

        self.auto_delete_cb = ttk.Checkbutton(action_frame, text="Auto-delete", variable=self.auto_delete)
        self.auto_delete_cb.pack(side='left')

        # Hint label describing mutual exclusion
        self.action_hint = ttk.Label(delete_group, text="Enable 'Press Enter' to disable Auto-delete (or vice versa)", font=('Arial', 8), foreground='#888888')
        self.action_hint.pack(anchor='w', pady=(4,0))
        
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
        ttk.Spinbox(delay_frame, from_=0.01, to=5.0, increment=0.01, textvariable=self.delete_delay, width=8).pack(side='left', padx=(5, 5))
        ttk.Label(delay_frame, text="seconds").pack(side='left')
        
        
    # Timing settings were moved to the Timing tab for clarity
        
    def setup_controls_tab(self, parent):
        # Activation mode
        mode_group = ttk.LabelFrame(parent, text="Activation Mode", padding=10)
        mode_group.pack(fill='x', padx=10, pady=5)
        
        ttk.Radiobutton(mode_group, text="Hold Mode (press and hold to activate)", 
                       variable=self.activation_mode, value="hold").pack(anchor='w')
        ttk.Radiobutton(mode_group, text="Toggle Mode (press once to start/stop)", 
                       variable=self.activation_mode, value="toggle").pack(anchor='w')
        ttk.Radiobutton(mode_group, text="Single Mode (press once to type one sequence)",
                       variable=self.activation_mode, value="single").pack(anchor='w')
        
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
        
    # (keyboard layout feature removed)

        # Compact note
        ttk.Label(parent, text="Tip: Use Hold mode for momentary typing, Toggle for continuous.", font=('Arial', 8)).pack(padx=10, pady=(8,0))
    
    def setup_instructions_tab(self, parent):
        """Setup instructions tab with simple usage guide"""
        instructions_text = """
🎯 QUICK START GUIDE:

1. SETUP:
    • Character Settings: pick letters, numbers, symbols, or add custom characters.
    • Formatting: add dashes or spaces every N characters.
    • Deletion tab: choose whether to auto-delete or press Enter after typing (these are mutually exclusive).
    • Timing tab: adjust per-key delay or use the Typing Speed slider (chars/sec, smooth logarithmic scale).
    • Controls: pick activation key and mode (Hold / Toggle / Single).

2. HOW TO USE:
    • Press your activation key (default: F1).
    • Hold mode: run while the key is held.
    • Toggle mode: press once to start, press again to stop.
    • Single mode: press once to type a single sequence (auto-delete is disabled for single runs).

3. BEHAVIOR NOTES:
    • If 'Press Enter' is enabled the tool will press Enter after typing and auto-delete will be disabled.
    • If 'Auto-delete' is enabled the tool will delete the typed text instead of sending Enter.
    • Typing Speed slider uses a smooth logarithmic scale up to 10,000 cps — lower values are easier to observe; very high speeds may be limited by the OS and target application.
    • Pause between cycles and post-Enter delay are configurable in the Timing tab.

4. TIPS:
    • Start with a moderate typing speed and small delete delay while you test.
    • Use Ctrl+Backspace option to delete words instead of characters.
    • Single mode is useful for previewing output without deleting it.

Enjoy and be careful — the automation will send keystrokes to whichever window is focused.
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
        # Status frame (compact)
        status_frame = tk.Frame(parent, bg='#2b2b2b')
        status_frame.pack(fill='x', pady=(6, 0))

        # Status label
        self.status_label = tk.Label(status_frame, text="Status: Ready",
                                     font=('Arial', 10, 'bold'), fg='#00ff00', bg='#2b2b2b')
        self.status_label.pack(side='left')

        # Control buttons
        button_frame = tk.Frame(status_frame, bg='#2b2b2b')
        button_frame.pack(side='right')

        self.start_btn = tk.Button(button_frame, text="Start", command=self.start_automation,
                                   bg='#4CAF50', fg='white', font=('Arial', 9, 'bold'))
        self.start_btn.pack(side='left', padx=(0, 5))

        self.stop_btn = tk.Button(button_frame, text="Stop", command=self.stop_automation,
                                  bg='#f44336', fg='white', font=('Arial', 9, 'bold'), state='disabled')
        self.stop_btn.pack(side='left')
        
    # keyboard layout feature removed

    def setup_timing_tab(self, parent):
        """Create a separate timing tab to simplify timing controls."""
        timing_group = ttk.LabelFrame(parent, text="Timing Controls", padding=10)
        timing_group.pack(fill='x', padx=10, pady=10)

        # Key delay
        kd_frame = ttk.Frame(timing_group)
        kd_frame.pack(fill='x', pady=(2,6))
        ttk.Label(kd_frame, text="Key delay (s):").pack(side='left')
        self.key_delay_spin = ttk.Spinbox(kd_frame, from_=0.00001, to=1.0, increment=0.00001, textvariable=self.key_delay, width=10)
        self.key_delay_spin.pack(side='left', padx=(6,6))
        ttk.Label(kd_frame, text="seconds (very small = faster)").pack(side='left')

        # Typing speed slider (logarithmic mapping 0..1 -> MIN_CPS..MAX_CPS for smooth feel)
        speed_frame = ttk.Frame(timing_group)
        speed_frame.pack(fill='x', pady=(2,6))
        ttk.Label(speed_frame, text="Typing speed (chars/sec):").pack(side='left')
        # Use tk.Scale instead of ttk.Scale so we can specify a fine resolution for smooth movement
        speed_scale = tk.Scale(speed_frame, from_=0.0, to=1.0, variable=self.typing_speed_slider,
                               orient='horizontal', command=self.on_slider_change,
                               resolution=0.0001, showvalue=False, length=360)
        speed_scale.pack(side='left', fill='x', expand=True, padx=(6,6))
        self.speed_label = ttk.Label(speed_frame, text=f"{self.typing_speed.get():.0f} cps")
        self.speed_label.pack(side='left')

        # Pause between cycles
        pbc_frame = ttk.Frame(timing_group)
        pbc_frame.pack(fill='x', pady=(2,6))
        ttk.Label(pbc_frame, text="Pause between cycles:").pack(side='left')
        ttk.Spinbox(pbc_frame, from_=0.0, to=10.0, increment=0.01, textvariable=self.pause_between_cycles, width=8).pack(side='left', padx=(6,6))
        ttk.Label(pbc_frame, text="seconds").pack(side='left')

        # Post-enter delay
        ped_frame = ttk.Frame(timing_group)
        ped_frame.pack(fill='x', pady=(2,6))
        ttk.Label(ped_frame, text="Post-Enter delay:").pack(side='left')
        ttk.Spinbox(ped_frame, from_=0.0, to=5.0, increment=0.01, textvariable=self.post_enter_delay, width=8).pack(side='left', padx=(6,6))
        ttk.Label(ped_frame, text="seconds (delay after pressing Enter)").pack(side='left')
    
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
                    mode = self.activation_mode.get()
                    if mode == "hold":
                        if not self.is_running:
                            self.start_automation()
                    elif mode == "toggle":
                        if not self.is_running:
                            self.start_automation()
                        else:
                            self.stop_automation()
                    elif mode == "single":
                        # run a single sequence in background; disable auto-delete for single runs
                        threading.Thread(target=lambda: self.perform_sequence_once(disable_auto_delete=True), daemon=True).start()
                            
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
                # Perform a single sequence (typing + optional enter + optional delete)
                self.perform_sequence_once()

                # Simple pause before next cycle
                time.sleep(self.pause_between_cycles.get())
                
            except Exception as e:
                print(f"Error in automation loop: {e}")
                break

    def perform_sequence_once(self, disable_auto_delete: bool = False):
        """Type one sequence, optionally press Enter, then optionally delete.

        disable_auto_delete: when True, skip auto-deletion even if the UI checkbox is set.
        """
        try:
            # Build buffer text to type to speed things up (use keyboard.write which is faster for bulk)
            out = []
            if self.use_dashes.get():
                chars_per_gap = self.dash_frequency.get()
                num_gaps = self.dash_gap_count.get()
                for gap_num in range(num_gaps):
                    for _ in range(chars_per_gap):
                        out.append(self.generate_character())
                    if gap_num < num_gaps - 1:
                        out.append('-')
            else:
                seq_len = self.get_sequence_length()
                for i in range(seq_len):
                    out.append(self.generate_character())
                    if self.space_frequency.get() > 0 and (i + 1) % self.space_frequency.get() == 0:
                        out.append(' ')

            # convert to string, writing keys via keyboard for speed
            text_to_type = ''.join(out)
            if text_to_type:
                try:
                    # keyboard.write tends to be faster than pyautogui.write for bulk
                    keyboard.write(text_to_type, delay=self.key_delay.get())
                except Exception:
                    # fallback to pyautogui
                    pyautogui.write(text_to_type)

            # Optionally press Enter
            if self.press_enter_after.get():
                time.sleep(self.post_enter_delay.get())
                pyautogui.press('enter')

            # Optionally delete (unless disabled for single-mode preview)
            if not disable_auto_delete and self.auto_delete.get():
                time.sleep(self.delete_delay.get())
                for _ in range(self.word_delete_count.get()):
                    pyautogui.hotkey('ctrl', 'backspace')
                    time.sleep(0.01)
        except Exception as e:
            print(f"Error during single sequence: {e}")
    
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

    def on_speed_change(self, value):
        """Update key_delay when typing speed slider changes.

        The slider is in characters-per-second; convert to delay per key.
        """
        try:
            cps = float(value)
            # clamp and avoid division by zero
            cps = max(0.1, min(self.MAX_CPS, cps))
            delay = 1.0 / cps
            # update key_delay without triggering recursion
            self.key_delay.set(round(delay, 4))
            # update label
            if hasattr(self, 'speed_label'):
                self.speed_label.config(text=f"{cps:.0f} cps")
        except Exception:
            pass

    def on_slider_change(self, value):
        """Map the 0..1 slider value to a logarithmic CPS scale and update typing_speed/key_delay."""
        try:
            t = float(value)
            # map t in [0,1] to cps in [MIN_CPS, MAX_CPS] logarithmically
            min_log = math.log(self.MIN_CPS)
            max_log = math.log(self.MAX_CPS)
            log_cps = min_log + t * (max_log - min_log)
            cps = math.exp(log_cps)
            # clamp and update
            cps = max(self.MIN_CPS, min(self.MAX_CPS, cps))
            self.typing_speed.set(round(cps, 2))
            # compute per-key delay
            delay = 1.0 / cps if cps > 0 else 0.0001
            self.key_delay.set(round(delay, 6))
            if hasattr(self, 'speed_label'):
                self.speed_label.config(text=f"{cps:.0f} cps")
        except Exception:
            pass

    def _attach_var_traces(self):
        """Attach traces to variables for two-way sync and mutual exclusion."""
        try:
            # typing_speed <-> key_delay two-way sync
            self.typing_speed.trace_add('write', lambda *a: self._on_typing_speed_var())
            self.key_delay.trace_add('write', lambda *a: self._on_key_delay_var())

            # mutual exclusion between press_enter_after and auto_delete
            self.press_enter_after.trace_add('write', lambda *a: self._on_press_enter_toggle())
            self.auto_delete.trace_add('write', lambda *a: self._on_auto_delete_toggle())

            # Run initial handlers to sync UI state
            self._on_typing_speed_var()
            self._on_auto_delete_toggle()
            self._on_press_enter_toggle()
        except Exception:
            pass

    def _on_typing_speed_var(self):
        if self._speed_update_in_progress:
            return
        try:
            self._speed_update_in_progress = True
            cps = float(self.typing_speed.get())
            cps = max(0.1, min(self.MAX_CPS, cps))
            delay = 1.0 / cps
            self.key_delay.set(round(delay, 6))
            if hasattr(self, 'speed_label'):
                self.speed_label.config(text=f"{cps:.0f} cps")
        except Exception:
            pass
        finally:
            self._speed_update_in_progress = False

    def _on_key_delay_var(self):
        if self._speed_update_in_progress:
            return
        try:
            self._speed_update_in_progress = True
            delay = float(self.key_delay.get())
            if delay <= 0:
                delay = 0.0001
            cps = 1.0 / delay
            cps = max(0.1, min(self.MAX_CPS, cps))
            self.typing_speed.set(round(cps, 2))
            if hasattr(self, 'speed_label'):
                self.speed_label.config(text=f"{cps:.0f} cps")
        except Exception:
            pass
        finally:
            self._speed_update_in_progress = False

    def _on_press_enter_toggle(self):
        # If press-enter is enabled, force auto-delete off and disable its checkbox
        try:
            if self.press_enter_after.get():
                # turn off auto delete and disable control
                self.auto_delete.set(False)
                if hasattr(self, 'auto_delete_cb'):
                    self.auto_delete_cb.config(state='disabled')
            else:
                if hasattr(self, 'auto_delete_cb'):
                    self.auto_delete_cb.config(state='normal')
        except Exception:
            pass

    def _on_auto_delete_toggle(self):
        # If auto-delete is enabled, turn off press-enter and disable its checkbox
        try:
            if self.auto_delete.get():
                self.press_enter_after.set(False)
                if hasattr(self, 'press_enter_cb'):
                    self.press_enter_cb.config(state='disabled')
            else:
                if hasattr(self, 'press_enter_cb'):
                    self.press_enter_cb.config(state='normal')
        except Exception:
            pass
    
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
