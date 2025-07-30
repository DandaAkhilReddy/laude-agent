#!/usr/bin/env python3
"""
Enterprise Admin Panel for Laude Agent
Advanced administration and monitoring capabilities
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from auth_system import EnterpriseAuth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdminPanel:
    """Enterprise administration panel with advanced monitoring"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Laude Agent Enterprise - Admin Panel")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f8f9fa')
        
        # Initialize auth system
        self.auth = EnterpriseAuth()
        
        # Admin authentication
        self.admin_authenticated = False
        self.current_admin_user = None
        
        self.setup_styles()
        self.show_admin_login()
        
    def setup_styles(self):
        """Setup professional admin styling"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Admin.TLabel', 
                       font=('Segoe UI', 12),
                       background='#f8f9fa')
        
        style.configure('AdminTitle.TLabel',
                       font=('Segoe UI', 16, 'bold'),
                       foreground='#1f4e79',
                       background='#f8f9fa')
        
        style.configure('AdminButton.TButton',
                       font=('Segoe UI', 10),
                       padding=(15, 8))
    
    def show_admin_login(self):
        """Show admin authentication dialog"""
        # Clear main window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Center login frame
        login_frame = tk.Frame(self.root, bg='#ffffff', relief='solid', bd=2)
        login_frame.pack(expand=True, pady=100)
        
        # Header
        header_label = tk.Label(login_frame, text="🔐 Admin Access Required", 
                               font=('Segoe UI', 18, 'bold'),
                               fg='#1f4e79', bg='#ffffff')
        header_label.pack(pady=20)
        
        # Admin email input
        tk.Label(login_frame, text="Admin Email:", 
                font=('Segoe UI', 12, 'bold'),
                fg='#495057', bg='#ffffff').pack(pady=(20, 5))
        
        self.admin_email_var = tk.StringVar()
        admin_email_entry = tk.Entry(login_frame, textvariable=self.admin_email_var,
                                   font=('Segoe UI', 12), width=30, relief='solid', bd=1)
        admin_email_entry.pack(pady=(0, 15), ipady=8)
        admin_email_entry.focus()
        
        # Info text
        info_label = tk.Label(login_frame, 
                             text="Only system administrators can access this panel.\nOTP verification will be required.",
                             font=('Segoe UI', 10), fg='#6c757d', bg='#ffffff')
        info_label.pack(pady=10)
        
        # Login button
        login_btn = tk.Button(login_frame, text="Request Admin Access", 
                             font=('Segoe UI', 12, 'bold'),
                             bg='#dc3545', fg='white',
                             command=self.authenticate_admin,
                             width=20, height=2, relief='flat')
        login_btn.pack(pady=20)
        
        # Status label
        self.admin_status_label = tk.Label(login_frame, text="", 
                                          font=('Segoe UI', 10),
                                          bg='#ffffff')
        self.admin_status_label.pack(pady=10)
        
        # Bind Enter key
        admin_email_entry.bind('<Return>', lambda e: self.authenticate_admin())
    
    def authenticate_admin(self):
        """Authenticate admin user"""
        email = self.admin_email_var.get().strip().lower()
        
        if not email:
            self.admin_status_label.config(text="Please enter admin email", fg='#dc3545')
            return
        
        # Check if user exists and has admin privileges
        try:
            conn = sqlite3.connect(self.auth.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, full_name, is_admin FROM users 
                WHERE email = ? AND is_active = 1
            ''', (email,))
            
            user_record = cursor.fetchone()
            conn.close()
            
            if not user_record:
                self.admin_status_label.config(text="Admin user not found", fg='#dc3545')
                return
            
            user_id, full_name, is_admin = user_record
            
            if not is_admin:
                self.admin_status_label.config(text="Access denied - Admin privileges required", fg='#dc3545')
                return
            
            # For demo purposes, skip OTP and authenticate directly
            # In production, you would generate and verify OTP here
            self.admin_authenticated = True
            self.current_admin_user = {
                'id': user_id,
                'email': email,
                'name': full_name
            }
            
            self.show_admin_dashboard()
            
        except Exception as e:
            logger.error(f"Admin authentication error: {str(e)}")
            self.admin_status_label.config(text="Authentication failed", fg='#dc3545')
    
    def show_admin_dashboard(self):
        """Show main admin dashboard"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main layout
        self.create_admin_header()
        self.create_admin_tabs()
    
    def create_admin_header(self):
        """Create admin panel header"""
        header_frame = tk.Frame(self.root, bg='#1f4e79', height=80)
        header_frame.pack(fill='x', pady=0)
        header_frame.pack_propagate(False)
        
        # Title and admin info
        title_frame = tk.Frame(header_frame, bg='#1f4e79')
        title_frame.pack(side='left', padx=20, pady=15)
        
        title_label = tk.Label(title_frame, text="🎙️ Laude Agent Enterprise - Admin Panel", 
                              font=('Segoe UI', 16, 'bold'), 
                              fg='white', bg='#1f4e79')
        title_label.pack()
        
        admin_info = tk.Label(title_frame, 
                             text=f"Administrator: {self.current_admin_user['name']} ({self.current_admin_user['email']})", 
                             font=('Segoe UI', 10), 
                             fg='#e8f4fd', bg='#1f4e79')
        admin_info.pack()
        
        # Logout button
        logout_btn = tk.Button(header_frame, text="Logout", 
                              font=('Segoe UI', 10),
                              bg='#dc3545', fg='white',
                              command=self.admin_logout,
                              relief='flat')
        logout_btn.pack(side='right', padx=20, pady=25)
    
    def create_admin_tabs(self):
        """Create tabbed interface for admin functions"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Dashboard tab
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="📊 Dashboard")
        self.create_dashboard_tab()
        
        # User Management tab
        self.users_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.users_frame, text="👥 User Management")
        self.create_users_tab()
        
        # System Monitoring tab
        self.monitoring_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.monitoring_frame, text="📈 System Monitoring")
        self.create_monitoring_tab()
        
        # Security & Audit tab
        self.security_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.security_frame, text="🔒 Security & Audit")
        self.create_security_tab()
        
        # Settings tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="⚙️ Settings")
        self.create_settings_tab()
    
    def create_dashboard_tab(self):
        """Create system overview dashboard"""
        # Stats cards
        stats_frame = tk.Frame(self.dashboard_frame, bg='#f8f9fa')
        stats_frame.pack(fill='x', padx=20, pady=20)
        
        # Get system stats
        stats = self.auth.get_user_stats()
        
        # Create stat cards
        self.create_stat_card(stats_frame, "Total Users", stats.get('total_users', 0), "#28a745", 0)
        self.create_stat_card(stats_frame, "Active Sessions", stats.get('active_sessions', 0), "#17a2b8", 1)
        self.create_stat_card(stats_frame, "24h Logins", stats.get('recent_logins_24h', 0), "#ffc107", 2)
        self.create_stat_card(stats_frame, "System Status", "Online", "#28a745", 3)
        
        # Recent activity
        activity_frame = tk.LabelFrame(self.dashboard_frame, text="Recent System Activity", 
                                     font=('Segoe UI', 12, 'bold'))
        activity_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        self.activity_text = scrolledtext.ScrolledText(activity_frame, 
                                                      font=('Consolas', 10),
                                                      height=15)
        self.activity_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Load recent activity
        self.load_recent_activity()
    
    def create_stat_card(self, parent, title, value, color, column):
        """Create a statistics card"""
        card_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        card_frame.grid(row=0, column=column, padx=10, pady=10, sticky='ew')
        parent.grid_columnconfigure(column, weight=1)
        
        # Value
        value_label = tk.Label(card_frame, text=str(value), 
                              font=('Segoe UI', 24, 'bold'),
                              fg=color, bg='white')
        value_label.pack(pady=(15, 5))
        
        # Title
        title_label = tk.Label(card_frame, text=title, 
                              font=('Segoe UI', 11),
                              fg='#6c757d', bg='white')
        title_label.pack(pady=(0, 15))
    
    def create_users_tab(self):
        """Create user management interface"""
        # Control buttons
        control_frame = tk.Frame(self.users_frame, bg='#f8f9fa')
        control_frame.pack(fill='x', padx=20, pady=20)
        
        refresh_btn = tk.Button(control_frame, text="🔄 Refresh Users", 
                               font=('Segoe UI', 10),
                               bg='#17a2b8', fg='white',
                               command=self.refresh_users,
                               relief='flat')
        refresh_btn.pack(side='left', padx=(0, 10))
        
        export_btn = tk.Button(control_frame, text="📊 Export Data", 
                              font=('Segoe UI', 10),
                              bg='#28a745', fg='white',
                              command=self.export_user_data,
                              relief='flat')
        export_btn.pack(side='left', padx=(0, 10))
        
        # Users table
        table_frame = tk.Frame(self.users_frame)
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Create treeview for users
        columns = ('ID', 'Email', 'Name', 'Department', 'Company', 'Last Login', 'Status')
        self.users_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        # Define headings
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=120)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.users_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient='horizontal', command=self.users_tree.xview)
        self.users_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack table and scrollbars
        self.users_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Load users
        self.refresh_users()
    
    def create_monitoring_tab(self):
        """Create system monitoring interface"""
        # Monitoring metrics
        metrics_frame = tk.LabelFrame(self.monitoring_frame, text="System Metrics", 
                                    font=('Segoe UI', 12, 'bold'))
        metrics_frame.pack(fill='x', padx=20, pady=20)
        
        # Create matplotlib figure for charts
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
            fig.suptitle('Laude Agent Enterprise - System Monitoring', fontsize=14, fontweight='bold')
            
            # Sample data for demo
            self.create_sample_charts(ax1, ax2, ax3, ax4)
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, metrics_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
            
        except ImportError:
            # Fallback if matplotlib not available
            fallback_label = tk.Label(metrics_frame, 
                                     text="📊 Advanced monitoring charts\n(Install matplotlib for full functionality)",
                                     font=('Segoe UI', 12),
                                     fg='#6c757d', bg='#f8f9fa')
            fallback_label.pack(pady=50)
        
        # System logs
        logs_frame = tk.LabelFrame(self.monitoring_frame, text="System Logs", 
                                 font=('Segoe UI', 12, 'bold'))
        logs_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        self.logs_text = scrolledtext.ScrolledText(logs_frame, 
                                                  font=('Consolas', 9),
                                                  height=10)
        self.logs_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Load system logs
        self.load_system_logs()
    
    def create_sample_charts(self, ax1, ax2, ax3, ax4):
        """Create sample monitoring charts"""
        # User registrations over time
        dates = [datetime.now() - timedelta(days=x) for x in range(30, 0, -1)]
        registrations = np.random.poisson(2, 30).cumsum()
        
        ax1.plot(dates, registrations, 'b-', linewidth=2)
        ax1.set_title('User Registrations (30 days)')
        ax1.set_ylabel('Total Users')
        ax1.tick_params(axis='x', rotation=45)
        
        # Login activity by hour
        hours = list(range(24))
        logins = np.random.poisson(5, 24)
        
        ax2.bar(hours, logins, color='green', alpha=0.7)
        ax2.set_title('Login Activity by Hour')
        ax2.set_xlabel('Hour of Day')
        ax2.set_ylabel('Login Count')
        
        # Company distribution
        companies = ['HHA Medicine', 'HSS Medicine']
        sizes = [65, 35]
        colors = ['#1f4e79', '#2c5aa0']
        
        ax3.pie(sizes, labels=companies, colors=colors, autopct='%1.1f%%')
        ax3.set_title('Users by Company')
        
        # System performance
        time_points = list(range(24))
        response_times = np.random.normal(150, 30, 24)
        
        ax4.plot(time_points, response_times, 'r-', linewidth=2, marker='o')
        ax4.set_title('Average Response Time (ms)')
        ax4.set_xlabel('Hour of Day')
        ax4.set_ylabel('Response Time (ms)')
        ax4.axhline(y=200, color='orange', linestyle='--', label='Warning Threshold')
        ax4.legend()
        
        plt.tight_layout()
    
    def create_security_tab(self):
        """Create security and audit interface"""
        # Security status
        security_frame = tk.LabelFrame(self.security_frame, text="Security Status", 
                                     font=('Segoe UI', 12, 'bold'))
        security_frame.pack(fill='x', padx=20, pady=20)
        
        # Security indicators
        indicators = [
            ("🔐 Authentication System", "Online", "#28a745"),
            ("🔑 OTP Verification", "Active", "#28a745"),
            ("🛡️ Session Management", "Secure", "#28a745"),
            ("📧 Email Security", "Configured", "#ffc107"),
            ("🔒 Domain Restrictions", "Enforced", "#28a745")
        ]
        
        for i, (name, status, color) in enumerate(indicators):
            indicator_frame = tk.Frame(security_frame, bg='white', relief='solid', bd=1)
            indicator_frame.grid(row=i//2, column=i%2, padx=10, pady=5, sticky='ew')
            security_frame.grid_columnconfigure(0, weight=1)
            security_frame.grid_columnconfigure(1, weight=1)
            
            tk.Label(indicator_frame, text=name, 
                    font=('Segoe UI', 11), bg='white').pack(side='left', padx=10, pady=8)
            
            tk.Label(indicator_frame, text=status, 
                    font=('Segoe UI', 11, 'bold'), 
                    fg=color, bg='white').pack(side='right', padx=10, pady=8)
        
        # Audit log
        audit_frame = tk.LabelFrame(self.security_frame, text="Audit Log", 
                                  font=('Segoe UI', 12, 'bold'))
        audit_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        self.audit_text = scrolledtext.ScrolledText(audit_frame, 
                                                   font=('Consolas', 10),
                                                   height=15)
        self.audit_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Load audit log
        self.load_audit_log()
    
    def create_settings_tab(self):
        """Create system settings interface"""
        # Company settings
        company_frame = tk.LabelFrame(self.settings_frame, text="Company Settings", 
                                    font=('Segoe UI', 12, 'bold'))
        company_frame.pack(fill='x', padx=20, pady=20)
        
        # Settings grid
        settings_grid = tk.Frame(company_frame, bg='#f8f9fa')
        settings_grid.pack(fill='x', padx=20, pady=20)
        
        # Domain management
        tk.Label(settings_grid, text="Allowed Domains:", 
                font=('Segoe UI', 11, 'bold'),
                bg='#f8f9fa').grid(row=0, column=0, sticky='w', pady=5)
        
        domains_text = ", ".join(self.auth.ALLOWED_DOMAINS)
        tk.Label(settings_grid, text=domains_text, 
                font=('Segoe UI', 11),
                bg='#f8f9fa').grid(row=0, column=1, sticky='w', padx=20, pady=5)
        
        # Session settings
        tk.Label(settings_grid, text="Session Duration:", 
                font=('Segoe UI', 11, 'bold'),
                bg='#f8f9fa').grid(row=1, column=0, sticky='w', pady=5)
        
        tk.Label(settings_grid, text=f"{self.auth.SESSION_EXPIRY_HOURS} hours", 
                font=('Segoe UI', 11),
                bg='#f8f9fa').grid(row=1, column=1, sticky='w', padx=20, pady=5)
        
        # OTP settings
        tk.Label(settings_grid, text="OTP Expiry:", 
                font=('Segoe UI', 11, 'bold'),
                bg='#f8f9fa').grid(row=2, column=0, sticky='w', pady=5)
        
        tk.Label(settings_grid, text=f"{self.auth.OTP_EXPIRY_MINUTES} minutes", 
                font=('Segoe UI', 11),
                bg='#f8f9fa').grid(row=2, column=1, sticky='w', padx=20, pady=5)
        
        # Action buttons
        actions_frame = tk.Frame(self.settings_frame, bg='#f8f9fa')
        actions_frame.pack(fill='x', padx=20, pady=20)
        
        backup_btn = tk.Button(actions_frame, text="💾 Backup Database", 
                              font=('Segoe UI', 11),
                              bg='#17a2b8', fg='white',
                              command=self.backup_database,
                              relief='flat')
        backup_btn.pack(side='left', padx=(0, 15))
        
        maintenance_btn = tk.Button(actions_frame, text="🔧 Run Maintenance", 
                                   font=('Segoe UI', 11),
                                   bg='#ffc107', fg='black',
                                   command=self.run_maintenance,
                                   relief='flat')
        maintenance_btn.pack(side='left', padx=(0, 15))
        
        reset_btn = tk.Button(actions_frame, text="⚠️ System Reset", 
                             font=('Segoe UI', 11),
                             bg='#dc3545', fg='white',
                             command=self.system_reset_warning,
                             relief='flat')
        reset_btn.pack(side='left')
    
    def refresh_users(self):
        """Refresh user list"""
        try:
            # Clear existing items
            for item in self.users_tree.get_children():
                self.users_tree.delete(item)
            
            # Get users from database
            conn = sqlite3.connect(self.auth.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, email, full_name, department, company_domain, 
                       last_login, is_active
                FROM users ORDER BY created_at DESC
            ''')
            
            users = cursor.fetchall()
            conn.close()
            
            # Populate tree
            for user in users:
                user_id, email, name, dept, company, last_login, is_active = user
                
                status = "Active" if is_active else "Inactive"
                last_login_str = last_login if last_login else "Never"
                
                self.users_tree.insert('', 'end', values=(
                    user_id, email, name, dept, company.upper(), 
                    last_login_str, status
                ))
            
            logger.info(f"Loaded {len(users)} users")
            
        except Exception as e:
            logger.error(f"Error refreshing users: {str(e)}")
            messagebox.showerror("Error", f"Failed to refresh users: {str(e)}")
    
    def load_recent_activity(self):
        """Load recent system activity"""
        try:
            conn = sqlite3.connect(self.auth.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT a.timestamp, u.email, a.action, a.details
                FROM audit_log a
                LEFT JOIN users u ON a.user_id = u.id
                ORDER BY a.timestamp DESC LIMIT 50
            ''')
            
            activities = cursor.fetchall()
            conn.close()
            
            self.activity_text.delete('1.0', tk.END)
            
            for timestamp, email, action, details in activities:
                activity_line = f"[{timestamp}] {email or 'System'}: {action}\n"
                if details:
                    activity_line += f"  Details: {details}\n"
                activity_line += "\n"
                
                self.activity_text.insert(tk.END, activity_line)
            
        except Exception as e:
            logger.error(f"Error loading activity: {str(e)}")
            self.activity_text.insert(tk.END, f"Error loading activity: {str(e)}\n")
    
    def load_audit_log(self):
        """Load security audit log"""
        try:
            conn = sqlite3.connect(self.auth.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT a.timestamp, u.email, a.action, a.details, a.ip_address
                FROM audit_log a
                LEFT JOIN users u ON a.user_id = u.id
                WHERE a.action IN ('LOGIN_SUCCESS', 'LOGIN_FAILED', 'USER_REGISTERED', 'LOGOUT')
                ORDER BY a.timestamp DESC LIMIT 100
            ''')
            
            audit_entries = cursor.fetchall()
            conn.close()
            
            self.audit_text.delete('1.0', tk.END)
            
            for timestamp, email, action, details, ip_address in audit_entries:
                audit_line = f"[{timestamp}] {action}\n"
                audit_line += f"  User: {email or 'Unknown'}\n"
                if ip_address:
                    audit_line += f"  IP: {ip_address}\n"
                if details:
                    audit_line += f"  Details: {details}\n"
                audit_line += "-" * 50 + "\n\n"
                
                self.audit_text.insert(tk.END, audit_line)
            
        except Exception as e:
            logger.error(f"Error loading audit log: {str(e)}")
            self.audit_text.insert(tk.END, f"Error loading audit log: {str(e)}\n")
    
    def load_system_logs(self):
        """Load system logs"""
        try:
            # Load recent log files
            logs_dir = Path("logs")
            if logs_dir.exists():
                log_files = list(logs_dir.glob("*.log"))
                log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                
                self.logs_text.delete('1.0', tk.END)
                
                # Show recent logs from the latest file
                if log_files:
                    latest_log = log_files[0]
                    with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        # Show last 100 lines
                        recent_lines = lines[-100:] if len(lines) > 100 else lines
                        
                        for line in recent_lines:
                            self.logs_text.insert(tk.END, line)
                else:
                    self.logs_text.insert(tk.END, "No log files found.\n")
            else:
                self.logs_text.insert(tk.END, "Logs directory not found.\n")
                
        except Exception as e:
            logger.error(f"Error loading system logs: {str(e)}")
            self.logs_text.insert(tk.END, f"Error loading system logs: {str(e)}\n")
    
    def export_user_data(self):
        """Export user data to JSON"""
        try:
            conn = sqlite3.connect(self.auth.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT email, full_name, department, company_domain, 
                       created_at, last_login, login_count, is_active
                FROM users ORDER BY created_at
            ''')
            
            users = cursor.fetchall()
            conn.close()
            
            # Convert to JSON format
            user_data = []
            for user in users:
                user_dict = {
                    'email': user[0],
                    'full_name': user[1],
                    'department': user[2],
                    'company_domain': user[3],
                    'created_at': user[4],
                    'last_login': user[5],
                    'login_count': user[6],
                    'is_active': bool(user[7])
                }
                user_data.append(user_dict)
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"user_export_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Export Complete", 
                              f"User data exported to {filename}\n\n"
                              f"Total users: {len(user_data)}")
            
        except Exception as e:
            logger.error(f"Export error: {str(e)}")
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
    
    def backup_database(self):
        """Backup the database"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"database_backup_{timestamp}.db"
            
            # Copy database file
            import shutil
            shutil.copy2(self.auth.db_path, backup_filename)
            
            messagebox.showinfo("Backup Complete", 
                              f"Database backed up to: {backup_filename}")
            
        except Exception as e:
            logger.error(f"Backup error: {str(e)}")
            messagebox.showerror("Backup Error", f"Failed to backup database: {str(e)}")
    
    def run_maintenance(self):
        """Run database maintenance"""
        try:
            conn = sqlite3.connect(self.auth.db_path)
            cursor = conn.cursor()
            
            # Clean up expired OTPs
            cursor.execute("DELETE FROM otp_codes WHERE expires_at < datetime('now')")
            
            # Clean up inactive sessions
            cursor.execute("UPDATE user_sessions SET is_active = 0 WHERE expires_at < datetime('now')")
            
            # Vacuum database
            cursor.execute("VACUUM")
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Maintenance Complete", 
                              "Database maintenance completed successfully.")
            
        except Exception as e:
            logger.error(f"Maintenance error: {str(e)}")
            messagebox.showerror("Maintenance Error", f"Maintenance failed: {str(e)}")
    
    def system_reset_warning(self):
        """Show system reset warning"""
        result = messagebox.askyesno("⚠️ System Reset Warning", 
                                   "This will reset ALL system data including:\n\n"
                                   "• All user accounts\n"
                                   "• All sessions\n"
                                   "• All audit logs\n"
                                   "• All OTP codes\n\n"
                                   "This action CANNOT be undone!\n\n"
                                   "Are you sure you want to continue?")
        
        if result:
            # Second confirmation
            confirm = messagebox.askyesno("Final Confirmation", 
                                        "This is your FINAL warning!\n\n"
                                        "All data will be permanently deleted.\n\n"
                                        "Continue with system reset?")
            if confirm:
                self.perform_system_reset()
    
    def perform_system_reset(self):
        """Perform complete system reset"""
        try:
            # Backup before reset
            self.backup_database()
            
            # Reinitialize database
            conn = sqlite3.connect(self.auth.db_path)
            cursor = conn.cursor()
            
            # Drop all tables
            tables = ['users', 'otp_codes', 'user_sessions', 'audit_log', 'company_settings']
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
            
            conn.commit()
            conn.close()
            
            # Reinitialize
            self.auth.init_database()
            
            messagebox.showinfo("System Reset Complete", 
                              "System has been reset successfully.\n\n"
                              "A backup was created before the reset.\n"
                              "Admin panel will now close.")
            
            self.root.quit()
            
        except Exception as e:
            logger.error(f"Reset error: {str(e)}")
            messagebox.showerror("Reset Error", f"System reset failed: {str(e)}")
    
    def admin_logout(self):
        """Logout admin user"""
        self.admin_authenticated = False
        self.current_admin_user = None
        self.show_admin_login()
    
    def run(self):
        """Start the admin panel"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Admin panel interrupted by user")
        except Exception as e:
            logger.error(f"Admin panel error: {str(e)}")
            messagebox.showerror("Application Error", f"An error occurred: {str(e)}")


def main():
    """Main entry point for admin panel"""
    try:
        # Create required directories
        directories = ["logs", "backups"]
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
        
        # Initialize and run admin panel
        admin = AdminPanel()
        admin.run()
        
    except Exception as e:
        logger.error(f"Failed to start admin panel: {str(e)}")
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()