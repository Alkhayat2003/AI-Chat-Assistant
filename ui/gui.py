#!/usr/bin/env python3
"""
GUI Module — Graphical User Interface using Tkinter.
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, filedialog, font
import threading
import time
from datetime import datetime
from ai_model.model import LLMModel
from config import ConfigLoader


class ChatGUI:
    """Graphical chat interface."""

    def __init__(self, root=None):
        self.config = ConfigLoader()
        self.model = LLMModel(self.config)

        if root is None:
            self.root = tk.Tk()
        else:
            self.root = root

        self.setup_styles()
        self.setup_ui()
        self.conversation_history = []

    def setup_styles(self):
        """Setup custom styles for better appearance."""
        # Configure ttk styles
        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TCombobox", font=("Segoe UI", 10))

        # Accent button style
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"),
                       background="#2196F3", foreground="white", padding=8)
        style.map("Accent.TButton",
                 background=[("active", "#1976D2"), ("pressed", "#0D47A1")])

        # Custom colors
        self.colors = {
            'user_bg': '#E3F2FD',  # Light blue
            'ai_bg': '#F1F8E9',    # Light green
            'error_bg': '#FFEBEE', # Light red
            'text_user': '#1565C0', # Dark blue
            'text_ai': '#2E7D32',   # Dark green
            'text_error': '#C62828', # Dark red
            'timestamp': '#666666'   # Gray
        }

    def setup_ui(self):
        """Setup the GUI components."""
        self.root.title("🤖 AI Chat Assistant")
        self.root.geometry("900x700")
        self.root.configure(bg='#F5F5F5')

        # Menu bar
        self.create_menu()

        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Top panel - Model and controls
        self.create_top_panel(main_frame)

        # Chat display area
        self.create_chat_area(main_frame)

        # Input area
        self.create_input_area(main_frame)

        # Status bar
        self.create_status_bar()

        # Configure tags for text styling
        self.setup_text_tags()

    def create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Conversation", command=self.save_conversation, accelerator="Ctrl+S")
        file_menu.add_command(label="Load Conversation", command=self.load_conversation, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Clear Chat", command=self.clear_chat, accelerator="Ctrl+L")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app, accelerator="Ctrl+Q")

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Copy", command=self.copy_text, accelerator="Ctrl+C")
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

        # Keyboard shortcuts
        self.root.bind('<Control-s>', lambda e: self.save_conversation())
        self.root.bind('<Control-o>', lambda e: self.load_conversation())
        self.root.bind('<Control-l>', lambda e: self.clear_chat())
        self.root.bind('<Control-q>', lambda e: self.exit_app())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.root.bind('<Control-c>', lambda e: self.copy_text())

    def create_top_panel(self, parent):
        """Create top panel with model selection and controls."""
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        # Model selection
        model_frame = ttk.LabelFrame(top_frame, text="Model Selection", padding=10)
        model_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Label(model_frame, text="AI Model:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.model_var = tk.StringVar(value=self.model.model)
        self.model_combo = ttk.Combobox(model_frame, textvariable=self.model_var,
                                       values=self.model.get_available_models(),
                                       state="readonly", width=20)
        self.model_combo.grid(row=0, column=1, padx=(5, 0), pady=2)
        self.model_combo.bind('<<ComboboxSelected>>', self.change_model)

        # Quick actions
        actions_frame = ttk.LabelFrame(top_frame, text="Quick Actions", padding=10)
        actions_frame.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Button(actions_frame, text="💾 Save", command=self.save_conversation).grid(row=0, column=0, padx=2)
        ttk.Button(actions_frame, text="📂 Load", command=self.load_conversation).grid(row=0, column=1, padx=2)
        ttk.Button(actions_frame, text="🗑️ Clear", command=self.clear_chat).grid(row=0, column=2, padx=2)

    def create_chat_area(self, parent):
        """Create chat display area."""
        chat_frame = ttk.LabelFrame(parent, text="Chat History", padding=10)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Chat display with custom styling
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            height=20,
            font=("Segoe UI", 10),
            bg='white',
            relief=tk.FLAT,
            borderwidth=1
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)

        # Progress bar for typing effect
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(chat_frame, variable=self.progress_var, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        self.progress_bar.pack_forget()  # Hide initially

    def create_input_area(self, parent):
        """Create input area."""
        input_frame = ttk.LabelFrame(parent, text="Your Message", padding=10)
        input_frame.pack(fill=tk.X)

        # Input field
        self.input_entry = tk.Text(
            input_frame,
            height=3,
            font=("Segoe UI", 10),
            wrap=tk.WORD,
            relief=tk.FLAT,
            borderwidth=1
        )
        self.input_entry.pack(fill=tk.X, pady=(0, 10))
        self.input_entry.bind("<Return>", self.send_message)
        self.input_entry.bind("<Shift-Return>", lambda e: None)  # Allow multiline

        # Button frame
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X)

        self.send_button = ttk.Button(button_frame, text="📤 Send Message",
                                    command=self.send_message, style="Accent.TButton")
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Button(button_frame, text="❌ Clear Input", command=self.clear_input).pack(side=tk.RIGHT)

        # Character counter
        self.char_count_var = tk.StringVar(value="0 characters")
        char_label = ttk.Label(button_frame, textvariable=self.char_count_var, font=("Segoe UI", 8))
        char_label.pack(side=tk.LEFT)

        # Bind character count update
        self.input_entry.bind('<KeyRelease>', self.update_char_count)

    def create_status_bar(self):
        """Create status bar."""
        self.status_var = tk.StringVar(value="Ready - Choose a model and start chatting!")
        status_bar = ttk.Label(self.root, textvariable=self.status_var,
                             relief=tk.SUNKEN, padding=5, font=("Segoe UI", 9))
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def setup_text_tags(self):
        """Setup text tags for styling messages."""
        self.chat_display.tag_configure("user", background=self.colors['user_bg'],
                                      foreground=self.colors['text_user'],
                                      lmargin1=10, lmargin2=10, rmargin=10)
        self.chat_display.tag_configure("ai", background=self.colors['ai_bg'],
                                      foreground=self.colors['text_ai'],
                                      lmargin1=10, lmargin2=10, rmargin=10)
        self.chat_display.tag_configure("error", background=self.colors['error_bg'],
                                      foreground=self.colors['text_error'],
                                      lmargin1=10, lmargin2=10, rmargin=10)
        self.chat_display.tag_configure("timestamp", foreground=self.colors['timestamp'],
                                      font=("Segoe UI", 8))

    def update_char_count(self, event=None):
        """Update character count display."""
        text = self.input_entry.get("1.0", tk.END).strip()
        count = len(text)
        max_length = self.config.get('security.max_message_length', 1000)
        self.char_count_var.set(f"{count}/{max_length} characters")
        if count > max_length:
            self.char_count_var.set(f"⚠️ {count}/{max_length} characters (too long!)")

    def clear_input(self):
        """Clear input field."""
        self.input_entry.delete("1.0", tk.END)
        self.update_char_count()

    def copy_text(self):
        """Copy selected text."""
        try:
            selected_text = self.chat_display.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
        except tk.TclError:
            pass  # No selection

    def select_all(self):
        """Select all text in chat display."""
        self.chat_display.tag_add(tk.SEL, "1.0", tk.END)
        self.chat_display.mark_set(tk.INSERT, tk.END)
        self.chat_display.see(tk.END)

    def show_about(self):
        """Show about dialog."""
        about_text = """🤖 AI Chat Assistant

A professional AI chat interface with multi-model support.

Features:
• Multiple AI models
• Conversation persistence
• Real-time typing effects
• Secure input validation
• Rate limiting protection

Version: 2.0
Built with Tkinter & Python"""
        messagebox.showinfo("About", about_text)

    def load_conversation(self):
        """Load conversation from file."""
        filename = filedialog.askopenfilename(
            title="Load Conversation",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                messages = self.model.load_conversation(filename)
                self.refresh_chat_display()
                self.status_var.set(f"Loaded {messages} messages from {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load: {e}")

    def refresh_chat_display(self):
        """Refresh the chat display with current conversation."""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)

        for msg in self.model.conversation:
            timestamp = datetime.now().strftime("%H:%M:%S")
            if msg['role'] == 'user':
                self.chat_display.insert(tk.END, f"[{timestamp}] You: {msg['content']}\n", "user")
            else:
                self.chat_display.insert(tk.END, f"[{timestamp}] AI: {msg['content']}\n\n", "ai")

        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def change_model(self, event=None):
        """Change the active model."""
        new_model = self.model_var.get()
        if self.model.set_model(new_model):
            self.status_var.set(f"✅ Model changed to: {new_model}")
            self.root.after(2000, lambda: self.status_var.set("Ready"))
        else:
            messagebox.showerror("Error", f"Model '{new_model}' not available")
            self.model_var.set(self.model.model)

    def send_message(self, event=None):
        """Send message to AI."""
        # Check if Shift+Enter (allow multiline)
        if event and event.state & 0x1:  # Shift key pressed
            return

        user_message = self.input_entry.get("1.0", tk.END).strip()
        if not user_message:
            return

        # Check length
        max_length = self.config.get('security.max_message_length', 1000)
        if len(user_message) > max_length:
            messagebox.showwarning("Warning", f"Message too long! Maximum {max_length} characters.")
            return

        self.input_entry.delete("1.0", tk.END)
        self.update_char_count()

        timestamp = datetime.now().strftime("%H:%M:%S")
        self.display_message(f"[{timestamp}] You: {user_message}", "user")

        # Disable input while processing
        self.input_entry.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)
        self.status_var.set("🤔 Thinking...")

        # Process in background thread
        threading.Thread(target=self.process_message, args=(user_message,), daemon=True).start()

    def process_message(self, user_message):
        """Process message in background thread."""
        try:
            response = self.model.send_message(user_message)
            self.root.after(0, lambda: self.display_response(response))
        except Exception as e:
            self.root.after(0, lambda: self.show_error(str(e)))

    def display_response(self, response):
        """Display AI response with typing effect."""
        self.status_var.set("✍️ AI is typing...")
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        self.progress_var.set(0)

        # Simulate typing effect
        typing_speed = self.config.get('ui.typing_speed', 0.02)
        timestamp = datetime.now().strftime("%H:%M:%S")
        ai_message = f"[{timestamp}] AI: "

        def type_char(index=0):
            if index < len(response):
                progress = (index + 1) / len(response) * 100
                self.progress_var.set(progress)

                ai_message_char = ai_message + response[:index + 1]
                self.chat_display.config(state=tk.NORMAL)
                if index == 0:
                    self.chat_display.insert(tk.END, f"{ai_message_char}")
                else:
                    # Replace last line
                    lines = self.chat_display.get("1.0", tk.END).strip().split("\n")
                    if lines:
                        lines[-1] = ai_message_char
                        self.chat_display.delete("1.0", tk.END)
                        self.chat_display.insert("1.0", "\n".join(lines))
                self.chat_display.config(state=tk.DISABLED)
                self.chat_display.see(tk.END)
                self.root.after(int(typing_speed * 1000), lambda: type_char(index + 1))
            else:
                self.chat_display.config(state=tk.NORMAL)
                self.chat_display.insert(tk.END, "\n\n")
                self.chat_display.config(state=tk.DISABLED)
                self.progress_bar.pack_forget()
                self.finish_response()

        type_char()

    def display_message(self, message, tag):
        """Display a message in the chat."""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{message}\n", tag)
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def show_error(self, error_msg):
        """Show error message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.display_message(f"[{timestamp}] ❌ Error: {error_msg}", "error")
        messagebox.showerror("Error", error_msg)
        self.progress_bar.pack_forget()
        self.finish_response()

    def finish_response(self):
        """Re-enable input after response."""
        self.input_entry.config(state=tk.NORMAL)
        self.send_button.config(state=tk.NORMAL)
        self.status_var.set("✅ Ready - Type your message!")
        self.input_entry.focus()

    def save_conversation(self):
        """Save conversation to file."""
        try:
            filename = self.model.save_conversation()
            self.status_var.set(f"💾 Conversation saved to {filename}")
            self.root.after(3000, lambda: self.status_var.set("Ready"))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def clear_chat(self):
        """Clear the chat display."""
        if messagebox.askyesno("Clear Chat", "Are you sure you want to clear the chat history?"):
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self.model.clear_conversation()
            self.status_var.set("🗑️ Chat cleared")
            self.root.after(2000, lambda: self.status_var.set("Ready"))

    def exit_app(self):
        """Exit the application."""
        if messagebox.askyesno("Exit", "Save conversation before exiting?"):
            self.save_conversation()
        self.root.quit()

    def run(self):
        """Start the GUI."""
        self.root.mainloop()


if __name__ == "__main__":
    gui = ChatGUI()
    gui.run()