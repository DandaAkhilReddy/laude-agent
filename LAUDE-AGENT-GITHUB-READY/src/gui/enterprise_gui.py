#!/usr/bin/env python3
"""
Enterprise GUI for Laude Agent with Authentication
Professional login system with OTP verification
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import webbrowser

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth_system import EnterpriseAuth
from generate_professional_email import generate_professional_email

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnterpriseLoginGUI:
    """Enterprise-grade login interface for Laude Agent"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Laude Agent Enterprise - Login")
        self.root.geometry("800x600")
        self.root.configure(bg='#f8f9fa')
        self.root.resizable(False, False)
        
        # Initialize authentication system
        self.auth = EnterpriseAuth()
        
        # Session management
        self.session_token = None
        self.user_data = None
        self.session_check_job = None
        
        # UI state
        self.current_step = "email"  # email -> otp -> main_app
        
        self.setup_styles()
        self.create_login_interface()
        self.center_window()
        
    def setup_styles(self):
        """Setup professional styling"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 18, 'bold'),
                       foreground='#1f4e79',
                       background='#f8f9fa')
        
        style.configure('Subtitle.TLabel',
                       font=('Segoe UI', 11),
                       foreground='#6c757d',
                       background='#f8f9fa')
        
        style.configure('Enterprise.TButton',
                       font=('Segoe UI', 11, 'bold'),
                       padding=(20, 10))
        
        style.configure('Success.TLabel',
                       font=('Segoe UI', 10),
                       foreground='#28a745',
                       background='#f8f9fa')
        
        style.configure('Error.TLabel',
                       font=('Segoe UI', 10),
                       foreground='#dc3545',
                       background='#f8f9fa')
    
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def create_login_interface(self):
        """Create the main login interface"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#ffffff', relief='solid', bd=1)
        main_frame.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Header section
        header_frame = tk.Frame(main_frame, bg='#1f4e79', height=100)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Logo and title
        title_label = tk.Label(header_frame, text="🎙️ Laude Agent", 
                              font=('Segoe UI', 24, 'bold'), 
                              fg='white', bg='#1f4e79')
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(header_frame, text="Enterprise Voice-to-Email Platform", 
                                 font=('Segoe UI', 12), 
                                 fg='#e8f4fd', bg='#1f4e79')
        subtitle_label.pack()
        
        # Content area
        content_frame = tk.Frame(main_frame, bg='#ffffff')
        content_frame.pack(fill='both', expand=True, padx=40, pady=40)
        
        if self.current_step == "email":
            self.create_email_step(content_frame)
        elif self.current_step == "register":
            self.create_registration_step(content_frame)
        elif self.current_step == "otp":
            self.create_otp_step(content_frame)
        elif self.current_step == "main_app":
            self.create_main_app(content_frame)
    
    def create_email_step(self, parent):
        """Create email input step"""
        # Welcome message
        welcome_label = ttk.Label(parent, text="Welcome to Laude Agent Enterprise", 
                                 style='Title.TLabel')
        welcome_label.pack(pady=(0, 10))
        
        desc_label = ttk.Label(parent, 
                              text="Secure access for HHA Medicine and HSS Medicine employees", 
                              style='Subtitle.TLabel')
        desc_label.pack(pady=(0, 30))
        
        # Email input section
        email_frame = tk.Frame(parent, bg='#ffffff')
        email_frame.pack(pady=20)
        
        tk.Label(email_frame, text="Corporate Email Address", 
                font=('Segoe UI', 12, 'bold'), fg='#495057', bg='#ffffff').pack(anchor='w')
        
        self.email_var = tk.StringVar()
        email_entry = tk.Entry(email_frame, textvariable=self.email_var, 
                              font=('Segoe UI', 12), width=35, relief='solid', bd=1)
        email_entry.pack(pady=(5, 10), ipady=8)
        email_entry.focus()
        
        # Domain restriction info
        info_frame = tk.Frame(parent, bg='#e7f3ff', relief='solid', bd=1)
        info_frame.pack(fill='x', pady=20)
        
        tk.Label(info_frame, text="ℹ️  Access Restricted", 
                font=('Segoe UI', 11, 'bold'), fg='#1f4e79', bg='#e7f3ff').pack(anchor='w', padx=15, pady=(10, 5))
        
        tk.Label(info_frame, text="• Only @hhamedicine.com and @hssmedicine.com emails allowed", 
                font=('Segoe UI', 10), fg='#495057', bg='#e7f3ff').pack(anchor='w', padx=15)
        
        tk.Label(info_frame, text="• OTP verification required for secure access", 
                font=('Segoe UI', 10), fg='#495057', bg='#e7f3ff').pack(anchor='w', padx=15, pady=(0, 10))
        
        # Buttons
        button_frame = tk.Frame(parent, bg='#ffffff')
        button_frame.pack(pady=30)
        
        # Continue button
        continue_btn = tk.Button(button_frame, text="Continue with Email", 
                               font=('Segoe UI', 12, 'bold'),
                               bg='#1f4e79', fg='white', 
                               command=self.process_email_step,
                               width=20, height=2, relief='flat')
        continue_btn.pack(side='left', padx=10)
        
        # New user button
        register_btn = tk.Button(button_frame, text="New User? Register", 
                               font=('Segoe UI', 11),
                               bg='#6c757d', fg='white',
                               command=self.show_registration_step,
                               width=18, height=2, relief='flat')
        register_btn.pack(side='left', padx=10)
        
        # Bind Enter key
        email_entry.bind('<Return>', lambda e: self.process_email_step())
        
        # Status label
        self.status_label = ttk.Label(parent, text="", style='Subtitle.TLabel')
        self.status_label.pack(pady=10)
    
    def create_registration_step(self, parent):
        """Create user registration step"""
        # Registration form
        reg_label = ttk.Label(parent, text="New User Registration", style='Title.TLabel')
        reg_label.pack(pady=(0, 20))
        
        # Form frame
        form_frame = tk.Frame(parent, bg='#ffffff')
        form_frame.pack(pady=20)
        
        # Email field
        tk.Label(form_frame, text="Corporate Email *", 
                font=('Segoe UI', 11, 'bold'), fg='#495057', bg='#ffffff').grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        self.reg_email_var = tk.StringVar()
        email_entry = tk.Entry(form_frame, textvariable=self.reg_email_var, 
                              font=('Segoe UI', 11), width=35, relief='solid', bd=1)
        email_entry.grid(row=1, column=0, pady=(0, 15), ipady=6)
        
        # Full name field
        tk.Label(form_frame, text="Full Name *", 
                font=('Segoe UI', 11, 'bold'), fg='#495057', bg='#ffffff').grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        self.reg_name_var = tk.StringVar()
        name_entry = tk.Entry(form_frame, textvariable=self.reg_name_var, 
                             font=('Segoe UI', 11), width=35, relief='solid', bd=1)
        name_entry.grid(row=3, column=0, pady=(0, 15), ipady=6)
        
        # Department field
        tk.Label(form_frame, text="Department/Role *", 
                font=('Segoe UI', 11, 'bold'), fg='#495057', bg='#ffffff').grid(row=4, column=0, sticky='w', pady=(0, 5))
        
        self.reg_dept_var = tk.StringVar()
        dept_entry = tk.Entry(form_frame, textvariable=self.reg_dept_var, 
                             font=('Segoe UI', 11), width=35, relief='solid', bd=1)
        dept_entry.grid(row=5, column=0, pady=(0, 20), ipady=6)
        
        # Buttons
        button_frame = tk.Frame(parent, bg='#ffffff')
        button_frame.pack(pady=20)
        
        register_btn = tk.Button(button_frame, text="Register Account", 
                               font=('Segoe UI', 12, 'bold'),
                               bg='#28a745', fg='white',
                               command=self.process_registration,
                               width=18, height=2, relief='flat')
        register_btn.pack(side='left', padx=10)
        
        back_btn = tk.Button(button_frame, text="Back to Login", 
                           font=('Segoe UI', 11),
                           bg='#6c757d', fg='white',
                           command=self.show_email_step,
                           width=15, height=2, relief='flat')
        back_btn.pack(side='left', padx=10)
        
        # Status
        self.reg_status_label = ttk.Label(parent, text="", style='Subtitle.TLabel')
        self.reg_status_label.pack(pady=10)
    
    def create_otp_step(self, parent):
        """Create OTP verification step"""
        # OTP verification
        otp_label = ttk.Label(parent, text="Email Verification", style='Title.TLabel')
        otp_label.pack(pady=(0, 10))
        
        desc_label = ttk.Label(parent, 
                              text=f"Enter the 6-digit code sent to {getattr(self, 'current_email', 'your email')}", 
                              style='Subtitle.TLabel')
        desc_label.pack(pady=(0, 30))
        
        # OTP input
        otp_frame = tk.Frame(parent, bg='#ffffff')
        otp_frame.pack(pady=20)
        
        tk.Label(otp_frame, text="Verification Code", 
                font=('Segoe UI', 12, 'bold'), fg='#495057', bg='#ffffff').pack()
        
        self.otp_var = tk.StringVar()
        otp_entry = tk.Entry(otp_frame, textvariable=self.otp_var, 
                            font=('Segoe UI', 16, 'bold'), width=15, 
                            relief='solid', bd=2, justify='center')
        otp_entry.pack(pady=(10, 20), ipady=10)
        otp_entry.focus()
        
        # Timer display
        self.timer_label = ttk.Label(parent, text="", style='Subtitle.TLabel')
        self.timer_label.pack()
        
        # Start countdown timer
        self.start_otp_timer()
        
        # Buttons
        button_frame = tk.Frame(parent, bg='#ffffff')
        button_frame.pack(pady=30)
        
        verify_btn = tk.Button(button_frame, text="Verify & Login", 
                              font=('Segoe UI', 12, 'bold'),
                              bg='#28a745', fg='white',
                              command=self.verify_otp,
                              width=15, height=2, relief='flat')
        verify_btn.pack(side='left', padx=10)
        
        resend_btn = tk.Button(button_frame, text="Resend Code", 
                              font=('Segoe UI', 11),
                              bg='#17a2b8', fg='white',
                              command=self.resend_otp,
                              width=12, height=2, relief='flat')
        resend_btn.pack(side='left', padx=10)
        
        back_btn = tk.Button(button_frame, text="Back", 
                           font=('Segoe UI', 11),
                           bg='#6c757d', fg='white',
                           command=self.show_email_step,
                           width=8, height=2, relief='flat')
        back_btn.pack(side='left', padx=10)
        
        # Bind Enter key
        otp_entry.bind('<Return>', lambda e: self.verify_otp())
        
        # Status
        self.otp_status_label = ttk.Label(parent, text="", style='Subtitle.TLabel')
        self.otp_status_label.pack(pady=10)
    
    def create_main_app(self, parent):
        """Create main application interface after login"""
        # Welcome header
        welcome_frame = tk.Frame(parent, bg='#e8f4fd', relief='solid', bd=1)
        welcome_frame.pack(fill='x', pady=(0, 20))
        
        welcome_text = f"Welcome back, {self.user_data.get('full_name', 'User')}!"
        welcome_label = tk.Label(welcome_frame, text=welcome_text, 
                                font=('Segoe UI', 16, 'bold'), 
                                fg='#1f4e79', bg='#e8f4fd')
        welcome_label.pack(pady=15)
        
        company_info = f"{self.user_data.get('department', 'Department')} • {self.user_data.get('company_domain', 'Company').upper()}"
        company_label = tk.Label(welcome_frame, text=company_info, 
                                font=('Segoe UI', 11), 
                                fg='#6c757d', bg='#e8f4fd')
        company_label.pack(pady=(0, 15))
        
        # Main features
        features_frame = tk.Frame(parent, bg='#ffffff')
        features_frame.pack(fill='both', expand=True, pady=20)
        
        # Feature buttons
        btn_frame = tk.Frame(features_frame, bg='#ffffff')
        btn_frame.pack(pady=30)
        
        # Voice Recording button
        record_btn = tk.Button(btn_frame, text="🎙️ Start Voice Recording", 
                              font=('Segoe UI', 14, 'bold'),
                              bg='#1f4e79', fg='white',
                              command=self.start_voice_recording,
                              width=25, height=3, relief='flat')
        record_btn.pack(pady=10)
        
        # Quick Email button
        quick_btn = tk.Button(btn_frame, text="📧 Generate Quick Email", 
                             font=('Segoe UI', 12),
                             bg='#28a745', fg='white',
                             command=self.generate_quick_email,
                             width=25, height=2, relief='flat')
        quick_btn.pack(pady=10)
        
        # User settings button
        settings_btn = tk.Button(btn_frame, text="⚙️ User Settings", 
                               font=('Segoe UI', 12),
                               bg='#6c757d', fg='white',
                               command=self.show_user_settings,
                               width=25, height=2, relief='flat')
        settings_btn.pack(pady=10)
        
        # Status area
        status_frame = tk.LabelFrame(features_frame, text="System Status", 
                                   font=('Segoe UI', 11, 'bold'),
                                   bg='#ffffff', fg='#1f4e79')
        status_frame.pack(fill='x', pady=20)
        
        self.main_status_label = tk.Label(status_frame, text="System ready. Click 'Start Voice Recording' to begin.", 
                                         font=('Segoe UI', 10), 
                                         fg='#28a745', bg='#ffffff')
        self.main_status_label.pack(pady=10)
        
        # Session info
        session_frame = tk.Frame(parent, bg='#f8f9fa', relief='solid', bd=1)
        session_frame.pack(fill='x', pady=(20, 0))
        
        session_info = f"Session expires: {datetime.fromisoformat(self.user_data['session_expires']).strftime('%I:%M %p')}"
        session_label = tk.Label(session_frame, text=session_info, 
                                font=('Segoe UI', 9), 
                                fg='#6c757d', bg='#f8f9fa')
        session_label.pack(side='left', padx=15, pady=8)
        
        logout_btn = tk.Button(session_frame, text="Logout", 
                              font=('Segoe UI', 9),
                              bg='#dc3545', fg='white',
                              command=self.logout_user,
                              relief='flat')
        logout_btn.pack(side='right', padx=15, pady=5)
        
        # Start session monitoring
        self.start_session_monitoring()
    
    def process_email_step(self):
        """Process email input and generate OTP"""
        email = self.email_var.get().strip().lower()
        
        if not email:
            self.status_label.config(text="Please enter your email address", foreground='#dc3545')
            return
        
        # Show loading
        self.status_label.config(text="Generating verification code...", foreground='#1f4e79')
        self.root.update()
        
        def generate_otp_async():
            result = self.auth.generate_otp(email)
            
            self.root.after(0, lambda: self.handle_otp_result(result, email))
        
        threading.Thread(target=generate_otp_async, daemon=True).start()
    
    def handle_otp_result(self, result, email):
        """Handle OTP generation result"""
        if result['success']:
            self.current_email = email
            self.current_step = "otp"
            self.create_login_interface()
            
            # Show OTP file location for development
            messagebox.showinfo("Development Mode", 
                              f"OTP sent! Check 'otp_emails/' folder for the code.\n\n"
                              f"In production, this will be sent to: {email}")
        else:
            self.status_label.config(text=result['message'], foreground='#dc3545')
    
    def show_registration_step(self):
        """Show registration step"""
        self.current_step = "register"
        self.create_login_interface()
    
    def show_email_step(self):
        """Show email input step"""
        self.current_step = "email"
        self.create_login_interface()
    
    def process_registration(self):
        """Process user registration"""
        email = self.reg_email_var.get().strip().lower()
        name = self.reg_name_var.get().strip()
        dept = self.reg_dept_var.get().strip()
        
        if not all([email, name, dept]):
            self.reg_status_label.config(text="Please fill in all required fields", foreground='#dc3545')
            return
        
        self.reg_status_label.config(text="Creating account...", foreground='#1f4e79')
        self.root.update()
        
        def register_async():
            result = self.auth.register_user(email, name, dept)
            self.root.after(0, lambda: self.handle_registration_result(result, email))
        
        threading.Thread(target=register_async, daemon=True).start()
    
    def handle_registration_result(self, result, email):
        """Handle registration result"""
        if result['success']:
            messagebox.showinfo("Registration Successful", 
                              f"{result['message']}\n\nYou can now login with your email.")
            self.email_var.set(email)  # Pre-fill email for login
            self.show_email_step()
        else:
            self.reg_status_label.config(text=result['message'], foreground='#dc3545')
    
    def verify_otp(self):
        """Verify OTP and login"""
        otp_code = self.otp_var.get().strip()
        
        if not otp_code or len(otp_code) != 6:
            self.otp_status_label.config(text="Please enter the 6-digit verification code", foreground='#dc3545')
            return
        
        self.otp_status_label.config(text="Verifying code...", foreground='#1f4e79')
        self.root.update()
        
        def verify_async():
            result = self.auth.verify_otp(self.current_email, otp_code)
            self.root.after(0, lambda: self.handle_login_result(result))
        
        threading.Thread(target=verify_async, daemon=True).start()
    
    def handle_login_result(self, result):
        """Handle login verification result"""
        if result['success']:
            self.session_token = result['session_token']
            self.user_data = result['user_data']
            
            messagebox.showinfo("Login Successful", 
                              f"Welcome to Laude Agent Enterprise!\n\n"
                              f"User: {self.user_data['full_name']}\n"
                              f"Company: {self.user_data['company_domain'].upper()}")
            
            self.current_step = "main_app"
            self.root.geometry("900x700")  # Larger window for main app
            self.create_login_interface()
        else:
            self.otp_status_label.config(text=result['message'], foreground='#dc3545')
    
    def resend_otp(self):
        """Resend OTP code"""
        if hasattr(self, 'current_email'):
            self.otp_status_label.config(text="Sending new code...", foreground='#1f4e79')
            self.root.update()
            
            def resend_async():
                result = self.auth.generate_otp(self.current_email)
                self.root.after(0, lambda: self.handle_resend_result(result))
            
            threading.Thread(target=resend_async, daemon=True).start()
    
    def handle_resend_result(self, result):
        """Handle OTP resend result"""
        if result['success']:
            self.otp_status_label.config(text="New verification code sent!", foreground='#28a745')
            self.start_otp_timer()  # Restart timer
            messagebox.showinfo("Code Sent", "New verification code sent to your email!")
        else:
            self.otp_status_label.config(text=result['message'], foreground='#dc3545')
    
    def start_otp_timer(self):
        """Start OTP countdown timer"""
        self.otp_expiry = datetime.now() + timedelta(minutes=10)  # 10 minutes
        self.update_timer()
    
    def update_timer(self):
        """Update countdown timer display"""
        if hasattr(self, 'otp_expiry'):
            remaining = self.otp_expiry - datetime.now()
            
            if remaining.total_seconds() > 0:
                minutes = int(remaining.total_seconds() // 60)
                seconds = int(remaining.total_seconds() % 60)
                self.timer_label.config(text=f"Code expires in: {minutes:02d}:{seconds:02d}")
                
                # Schedule next update
                self.root.after(1000, self.update_timer)
            else:
                self.timer_label.config(text="Verification code expired", foreground='#dc3545')
    
    def start_session_monitoring(self):
        """Start monitoring session validity"""
        def check_session():
            if self.session_token:
                result = self.auth.validate_session(self.session_token)
                
                if not result['success']:
                    messagebox.showwarning("Session Expired", 
                                         "Your session has expired. Please login again.")
                    self.logout_user()
                    return
                
                # Update user data
                self.user_data = result['user_data']
            
            # Schedule next check (every 5 minutes)
            self.session_check_job = self.root.after(300000, check_session)
        
        # Start monitoring
        self.session_check_job = self.root.after(300000, check_session)
    
    def logout_user(self):
        """Logout current user"""
        if self.session_token:
            self.auth.logout_user(self.session_token)
        
        # Cancel session monitoring
        if self.session_check_job:
            self.root.after_cancel(self.session_check_job)
        
        # Reset state
        self.session_token = None
        self.user_data = None
        self.current_step = "email"
        
        # Reset window size and show login
        self.root.geometry("800x600")
        self.create_login_interface()
        
        messagebox.showinfo("Logged Out", "You have been logged out successfully.")
    
    def start_voice_recording(self):
        """Start the voice recording process"""
        self.main_status_label.config(text="Voice recording feature coming soon...", foreground='#1f4e79')
        messagebox.showinfo("Feature Coming Soon", 
                          "Voice recording integration will be available in the next update!")
    
    def generate_quick_email(self):
        """Generate a quick professional email"""
        # Create sample content for demo
        sample_transcript = f"""
        This week at {self.user_data['company_domain'].split('.')[0].upper()} I completed several important tasks.
        I worked on system improvements and collaborated with the team on various projects.
        Performance was good this week and I maintained all operational standards.
        Next week I'm planning to focus on new initiatives and continued development.
        """
        
        self.main_status_label.config(text="Generating professional email...", foreground='#1f4e79')
        self.root.update()
        
        def generate_async():
            try:
                company_name = self.user_data['company_domain'].split('.')[0].upper() + " Medicine"
                
                email_content = generate_professional_email(
                    sample_transcript,
                    self.user_data['full_name'],
                    company_name,
                    self.user_data['department']
                )
                
                self.root.after(0, lambda: self.show_generated_email(email_content))
                
            except Exception as e:
                logger.error(f"Email generation error: {str(e)}")
                self.root.after(0, lambda: self.main_status_label.config(
                    text="Email generation failed. Please try again.", foreground='#dc3545'))
        
        threading.Thread(target=generate_async, daemon=True).start()
    
    def show_generated_email(self, email_content):
        """Show generated email in a new window"""
        if email_content:
            # Create new window for email preview
            email_window = tk.Toplevel(self.root)
            email_window.title("Generated Professional Email")
            email_window.geometry("700x500")
            email_window.configure(bg='#ffffff')
            
            # Email content display
            text_widget = scrolledtext.ScrolledText(email_window, 
                                                  font=('Consolas', 11),
                                                  bg='#ffffff', fg='#2c3e50',
                                                  relief='solid', bd=1)
            text_widget.pack(fill='both', expand=True, padx=20, pady=20)
            
            text_widget.insert('1.0', email_content)
            text_widget.config(state='disabled')  # Make read-only
            
            # Buttons
            btn_frame = tk.Frame(email_window, bg='#ffffff')
            btn_frame.pack(pady=10)
            
            copy_btn = tk.Button(btn_frame, text="Copy to Clipboard", 
                               font=('Segoe UI', 11),
                               bg='#28a745', fg='white',
                               command=lambda: self.copy_to_clipboard(email_content),
                               relief='flat')
            copy_btn.pack(side='left', padx=10)
            
            close_btn = tk.Button(btn_frame, text="Close", 
                                font=('Segoe UI', 11),
                                bg='#6c757d', fg='white',
                                command=email_window.destroy,
                                relief='flat')
            close_btn.pack(side='left', padx=10)
            
            self.main_status_label.config(text="Professional email generated successfully!", foreground='#28a745')
        else:
            self.main_status_label.config(text="Failed to generate email. Please try again.", foreground='#dc3545')
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copied", "Email content copied to clipboard!")
    
    def show_user_settings(self):
        """Show user settings dialog"""
        messagebox.showinfo("User Settings", 
                          f"User: {self.user_data['full_name']}\n"
                          f"Email: {self.user_data['email']}\n"
                          f"Department: {self.user_data['department']}\n"
                          f"Company: {self.user_data['company_domain'].upper()}\n\n"
                          f"Advanced settings coming soon!")
    
    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Application error: {str(e)}")
            messagebox.showerror("Application Error", f"An error occurred: {str(e)}")


def main():
    """Main application entry point"""
    try:
        # Create required directories
        directories = ["otp_emails", "logs", "emails", "reports", "transcripts", "audio_clips"]
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
        
        # Initialize and run the enterprise GUI
        app = EnterpriseLoginGUI()
        app.run()
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()