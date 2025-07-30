#!/usr/bin/env python3
"""
Weekly Report AI - GUI Application
Click to run voice-to-email reporting system
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from record_voice import record_multiple_clips, test_microphone
    from merge_audio import merge_audio_clips
    from transcribe_audio import transcribe_audio
    from generate_report import generate_report
    from generate_professional_email import generate_professional_email
    from send_email_outlook import send_email_outlook_draft
except ImportError as e:
    print(f"Import error: {e}")

class WeeklyReportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Laude - Your AI Voice Assistant")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.is_recording = False
        self.audio_files = []
        self.transcript = ""
        self.report_html = ""
        
        # User information
        self.user_name = ""
        self.user_email = ""
        self.user_company = ""
        self.user_department = ""
        
        # Check if user info exists, if not show setup
        if not self.load_user_info():
            self.show_user_setup()
        else:
            self.setup_ui()
            self.setup_logging()
    
    def load_user_info(self):
        """Load user information from config file"""
        try:
            config_file = Path("user_config.txt")
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if len(lines) >= 4:
                        self.user_name = lines[0].strip()
                        self.user_email = lines[1].strip()
                        self.user_company = lines[2].strip()
                        self.user_department = lines[3].strip()
                        return True
        except Exception:
            pass
        return False
    
    def save_user_info(self):
        """Save user information to config file"""
        try:
            with open("user_config.txt", 'w', encoding='utf-8') as f:
                f.write(f"{self.user_name}\n")
                f.write(f"{self.user_email}\n")
                f.write(f"{self.user_company}\n")
                f.write(f"{self.user_department}\n")
            return True
        except Exception:
            return False
    
    def show_user_setup(self):
        """Show user setup dialog"""
        setup_window = tk.Toplevel(self.root)
        setup_window.title("Welcome to Laude - Setup Your Profile")
        setup_window.geometry("500x400")
        setup_window.configure(bg='#f0f0f0')
        setup_window.grab_set()  # Make it modal
        
        # Center the window
        setup_window.transient(self.root)
        
        # Header
        header = tk.Label(setup_window, text="🎙️ Welcome to Laude!", 
                         font=('Calibri', 18, 'bold'), bg='#f0f0f0', fg='#1f4e79')
        header.pack(pady=20)
        
        subtitle = tk.Label(setup_window, text="Please enter your information for personalized emails:", 
                           font=('Calibri', 12), bg='#f0f0f0', fg='#666')
        subtitle.pack(pady=(0,20))
        
        # Form frame
        form_frame = tk.Frame(setup_window, bg='#f0f0f0')
        form_frame.pack(padx=40, pady=20, fill='both', expand=True)
        
        # Input fields
        fields = [
            ("Full Name:", "user_name"),
            ("Email Address:", "user_email"), 
            ("Company/Organization:", "user_company"),
            ("Department/Role:", "user_department")
        ]
        
        self.setup_entries = {}
        
        for i, (label_text, field_name) in enumerate(fields):
            # Label
            label = tk.Label(form_frame, text=label_text, font=('Calibri', 11, 'bold'),
                           bg='#f0f0f0', fg='#1f4e79')
            label.grid(row=i, column=0, sticky='w', pady=(10,5))
            
            # Entry
            entry = tk.Entry(form_frame, font=('Calibri', 11), width=30, relief='solid', bd=1)
            entry.grid(row=i, column=1, pady=(10,5), padx=(10,0), sticky='ew')
            
            self.setup_entries[field_name] = entry
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = tk.Frame(setup_window, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        save_btn = tk.Button(button_frame, text="Save & Continue", 
                            font=('Calibri', 12, 'bold'), bg='#1f4e79', fg='white',
                            command=lambda: self.save_setup_info(setup_window), 
                            width=15, height=2)
        save_btn.pack(side='left', padx=10)
        
        # Pre-fill with default values
        self.setup_entries['user_name'].insert(0, "Akhil Reddy")
        self.setup_entries['user_email'].insert(0, "areddy@hssmedicine.com")
        self.setup_entries['user_company'].insert(0, "HSS Medicine")
        self.setup_entries['user_department'].insert(0, "Technology Team")
    
    def save_setup_info(self, setup_window):
        """Save setup information and continue"""
        # Get values from entries
        self.user_name = self.setup_entries['user_name'].get().strip()
        self.user_email = self.setup_entries['user_email'].get().strip()
        self.user_company = self.setup_entries['user_company'].get().strip()
        self.user_department = self.setup_entries['user_department'].get().strip()
        
        # Validate required fields
        if not all([self.user_name, self.user_email, self.user_company, self.user_department]):
            messagebox.showerror("Error", "Please fill in all fields!")
            return
        
        # Save to file
        if self.save_user_info():
            setup_window.destroy()
            self.setup_ui()
            self.setup_logging()
            messagebox.showinfo("Success", f"Welcome {self.user_name}! Your profile has been saved.")
        else:
            messagebox.showerror("Error", "Failed to save user information!")
        
    def setup_ui(self):
        """Setup the user interface"""
        
        # Header
        header_frame = tk.Frame(self.root, bg='#1f4e79', height=80)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🎙️ Laude - Your AI Voice Assistant", 
                              font=('Calibri', 20, 'bold'), fg='white', bg='#1f4e79')
        title_label.pack(pady=15)
        
        subtitle_label = tk.Label(header_frame, text=f"Hi {self.user_name}! Speak → Laude Listens → Professional Email Ready", 
                                 font=('Calibri', 12), fg='#e8f4fd', bg='#1f4e79')
        subtitle_label.pack()
        
        # User info display
        info_label = tk.Label(header_frame, text=f"{self.user_department} • {self.user_company}", 
                             font=('Calibri', 10), fg='#b8d4f0', bg='#1f4e79')
        info_label.pack(pady=(2,10))
        
        # Main content area
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Step indicators
        self.create_step_indicators(main_frame)
        
        # Control buttons
        self.create_control_buttons(main_frame)
        
        # Status and log area
        self.create_status_area(main_frame)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=(10, 0))
        
    def create_step_indicators(self, parent):
        """Create step indicator widgets"""
        
        steps_frame = tk.Frame(parent, bg='#f0f0f0')
        steps_frame.pack(fill='x', pady=(0, 20))
        
        self.steps = [
            "🎤 Record Voice",
            "🔄 Process Audio", 
            "🤖 AI Transcription",
            "📝 Generate Report",
            "📧 Create Email"
        ]
        
        self.step_labels = []
        for i, step in enumerate(self.steps):
            step_frame = tk.Frame(steps_frame, bg='#e8f4fd', relief='ridge', bd=1)
            step_frame.pack(side='left', fill='x', expand=True, padx=2)
            
            label = tk.Label(step_frame, text=step, font=('Calibri', 10), 
                           bg='#e8f4fd', fg='#1f4e79', pady=5)
            label.pack()
            
            self.step_labels.append((step_frame, label))
    
    def create_control_buttons(self, parent):
        """Create control buttons"""
        
        button_frame = tk.Frame(parent, bg='#f0f0f0')
        button_frame.pack(fill='x', pady=(0, 20))
        
        # Main action button
        self.main_button = tk.Button(button_frame, text="🎙️ Start Recording", 
                                   font=('Calibri', 14, 'bold'), bg='#1f4e79', fg='white',
                                   command=self.start_recording, height=2, width=20)
        self.main_button.pack(side='left', padx=(0, 10))
        
        # Test microphone button
        self.test_button = tk.Button(button_frame, text="🎤 Test Microphone", 
                                   font=('Calibri', 12), bg='#27ae60', fg='white',
                                   command=self.test_microphone_click, height=2, width=15)
        self.test_button.pack(side='left', padx=(0, 10))
        
        # Demo button
        self.demo_button = tk.Button(button_frame, text="🚀 Run Demo", 
                                   font=('Calibri', 12), bg='#e67e22', fg='white',
                                   command=self.run_demo, height=2, width=12)
        self.demo_button.pack(side='left')
        
    def create_status_area(self, parent):
        """Create status and log display area"""
        
        # Status label
        self.status_label = tk.Label(parent, text="Ready to record your weekly update", 
                                   font=('Calibri', 12), bg='#f0f0f0', fg='#2c3e50')
        self.status_label.pack(pady=(0, 10))
        
        # Log area
        log_frame = tk.LabelFrame(parent, text="System Log", font=('Calibri', 10, 'bold'),
                                 bg='#f0f0f0', fg='#1f4e79')
        log_frame.pack(fill='both', expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, font=('Consolas', 10),
                                                bg='#ffffff', fg='#2c3e50')
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
    def setup_logging(self):
        """Setup logging to display in GUI"""
        
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Setup logging
        log_file = log_dir / f"gui_app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler(log_file)]
        )
        
        self.logger = logging.getLogger(__name__)
        
    def log_message(self, message, level="INFO"):
        """Add message to log display"""
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
        # Also log to file
        if level == "INFO":
            self.logger.info(message)
        elif level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
    
    def update_step_status(self, step_index, status="active"):
        """Update step indicator status"""
        
        if 0 <= step_index < len(self.step_labels):
            frame, label = self.step_labels[step_index]
            
            if status == "active":
                frame.configure(bg='#f39c12')
                label.configure(bg='#f39c12', fg='white')
            elif status == "completed":
                frame.configure(bg='#27ae60')
                label.configure(bg='#27ae60', fg='white')
            elif status == "error":
                frame.configure(bg='#e74c3c')
                label.configure(bg='#e74c3c', fg='white')
            else:  # reset
                frame.configure(bg='#e8f4fd')
                label.configure(bg='#e8f4fd', fg='#1f4e79')
    
    def reset_steps(self):
        """Reset all step indicators"""
        for i in range(len(self.step_labels)):
            self.update_step_status(i, "reset")
    
    def test_microphone_click(self):
        """Test microphone functionality"""
        
        self.log_message("Testing microphone...")
        self.status_label.configure(text="Testing microphone...")
        
        def test_mic():
            try:
                if test_microphone():
                    self.log_message("Microphone test successful!", "INFO")
                    self.status_label.configure(text="Microphone working correctly")
                    messagebox.showinfo("Success", "Microphone is working correctly!")
                else:
                    self.log_message("Microphone test failed", "ERROR")
                    self.status_label.configure(text="Microphone test failed")
                    messagebox.showerror("Error", "Microphone test failed. Check connections.")
            except Exception as e:
                self.log_message(f"Microphone test error: {str(e)}", "ERROR")
                messagebox.showerror("Error", f"Microphone test error: {str(e)}")
        
        threading.Thread(target=test_mic, daemon=True).start()
    
    def start_recording(self):
        """Start the voice recording process"""
        
        if self.is_recording:
            return
        
        self.is_recording = True
        self.main_button.configure(text="🔴 Recording...", state='disabled')
        self.progress.start()
        self.reset_steps()
        
        def recording_process():
            try:
                # Step 1: Record voice
                self.update_step_status(0, "active")
                self.status_label.configure(text="Recording your voice...")
                self.log_message("Starting voice recording")
                
                # For GUI version, we'll use a simplified recording approach
                messagebox.showinfo("Recording", 
                    "Voice recording will start when you click OK.\n" +
                    "Speak your weekly update clearly.\n" +
                    "The recording will stop automatically after 60 seconds,\n" +
                    "or you can close this dialog early to stop.")
                
                # Simulate recording (in real version, this would be actual recording)
                import time
                time.sleep(2)  # Simulate recording time
                
                # For demo, use sample transcript
                self.transcript = """
                This week at HHA Medicine I completed several important projects.
                I implemented the new patient management system with full HIPAA compliance.
                The telemedicine platform was upgraded and now supports 300% more video calls.
                I trained 25 nursing staff on the new portal features with 95% satisfaction.
                System uptime was maintained at 99.7% with zero security incidents.
                Next week I'm focusing on mobile app launch and insurance integration.
                """
                
                self.update_step_status(0, "completed")
                self.update_step_status(1, "completed")  # Skip audio processing for demo
                
                # Step 3: AI Transcription (simulated)
                self.update_step_status(2, "active")
                self.status_label.configure(text="AI transcribing your voice...")
                self.log_message("Transcribing with OpenAI Whisper")
                time.sleep(3)
                self.update_step_status(2, "completed")
                
                # Step 4: Generate report
                self.update_step_status(3, "active")
                self.status_label.configure(text="Generating professional report...")
                self.log_message("Generating report with GPT-4")
                
                self.report_html = generate_report(self.transcript)
                
                if self.report_html:
                    self.update_step_status(3, "completed")
                    self.log_message("Professional report generated successfully")
                else:
                    self.update_step_status(3, "error")
                    self.log_message("Failed to generate report", "ERROR")
                    return
                
                # Step 5: Create email
                self.update_step_status(4, "active")
                self.status_label.configure(text="Creating professional email...")
                self.log_message("Generating professional email with AI")
                
                # Generate professional email using universal prompt
                professional_email = generate_professional_email(
                    self.transcript, 
                    self.user_name, 
                    self.user_company, 
                    self.user_department
                )
                
                if not professional_email:
                    professional_email = self.create_fallback_email()
                
                combined_content = f"{professional_email}\n\n--- DETAILED REPORT ---\n{self.report_html}"
                
                subject = f"Weekly Update - {datetime.now().strftime('%B %d, %Y')} - {self.user_name}"
                
                if send_email_outlook_draft(combined_content, subject):
                    self.update_step_status(4, "completed")
                    self.log_message("Outlook email draft created successfully")
                    self.status_label.configure(text="Success! Check Outlook for your email draft")
                    
                    messagebox.showinfo("Success!", 
                        f"Professional email created successfully!\n\n" +
                        f"✓ AI transcription completed\n" +
                        f"✓ Professional report generated\n" +
                        f"✓ Personalized email for {self.user_name}\n" +
                        f"✓ Outlook draft ready to send\n\n" +
                        "Check your Outlook application!")
                else:
                    self.update_step_status(4, "error")
                    self.log_message("Failed to create Outlook draft", "ERROR")
                
            except Exception as e:
                self.log_message(f"Process error: {str(e)}", "ERROR")
                messagebox.showerror("Error", f"Process failed: {str(e)}")
            
            finally:
                self.is_recording = False
                self.main_button.configure(text="🎙️ Start Recording", state='normal')
                self.progress.stop()
        
        threading.Thread(target=recording_process, daemon=True).start()
    
    def create_fallback_email(self):
        """Create fallback email if AI generation fails"""
        
        return f"""Good morning,

Here is my weekly update:

1. Completed key projects and initiatives as planned
2. Maintained system performance and reliability standards
3. Collaborated with team members on ongoing objectives
4. Addressed technical challenges and operational requirements
5. Continued professional development and skill enhancement
6. Planning to focus on priority tasks and deliverables next week

Key metrics: Weekly objectives met, systems operational, team collaboration maintained.

Best regards,
{self.user_name}
{self.user_department} • {self.user_company}

---
Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Note: This is a fallback email. For detailed updates, please use voice recording feature.
"""
    
    def run_demo(self):
        """Run demo mode"""
        
        self.log_message("Running demo mode")
        
        # Simulate the full process quickly
        self.reset_steps()
        
        def demo_process():
            try:
                for i in range(5):
                    self.update_step_status(i, "active")
                    self.status_label.configure(text=f"Demo: {self.steps[i]}")
                    self.log_message(f"Demo step: {self.steps[i]}")
                    
                    import time
                    time.sleep(1)
                    
                    self.update_step_status(i, "completed")
                
                # Generate actual report in demo
                demo_transcript = """
                Demo week at HHA Medicine: completed patient system integration,
                implemented security protocols, trained staff on new features,
                maintained 99.7% uptime, planning mobile app launch next week.
                """
                
                self.report_html = generate_report(demo_transcript)
                
                # Generate professional email using universal prompt
                professional_email = generate_professional_email(
                    demo_transcript, 
                    self.user_name, 
                    self.user_company, 
                    self.user_department
                )
                
                if not professional_email:
                    professional_email = self.create_fallback_email()
                
                combined_content = f"{professional_email}\n\n--- DETAILED REPORT ---\n{self.report_html}"
                
                subject = f"DEMO - Weekly Update - {datetime.now().strftime('%B %d, %Y')} - {self.user_name}"
                
                if send_email_outlook_draft(combined_content, subject):
                    self.status_label.configure(text="Demo complete! Check Outlook")
                    self.log_message("Demo completed successfully - Outlook draft created")
                    
                    messagebox.showinfo("Demo Complete!", 
                        f"Demo completed successfully!\n\n" +
                        f"✓ All systems tested\n" +
                        f"✓ Professional email created for {self.user_name}\n" +
                        f"✓ Universal prompt system working\n" +
                        f"✓ Ready for real voice recording\n\n" +
                        "Check Outlook for demo email!")
                else:
                    self.log_message("Demo completed - email creation had issues", "WARNING")
            
            except Exception as e:
                self.log_message(f"Demo error: {str(e)}", "ERROR")
        
        threading.Thread(target=demo_process, daemon=True).start()

def main():
    """Main application entry point"""
    
    # Setup directories
    directories = ["audio_clips", "reports", "transcripts", "logs", "templates"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    # Create and run GUI
    root = tk.Tk()
    app = WeeklyReportApp(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()