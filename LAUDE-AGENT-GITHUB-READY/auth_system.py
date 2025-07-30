#!/usr/bin/env python3
"""
Enterprise Authentication System for Laude Agent
Supports HHA Medicine and HSS Medicine domain authentication with OTP
"""

import sqlite3
import hashlib
import secrets
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Tuple
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnterpriseAuth:
    """Enterprise Authentication System with domain restrictions and OTP"""
    
    # Allowed company domains
    ALLOWED_DOMAINS = ['hhamedicine.com', 'hssmedicine.com']
    
    # OTP expiry time (minutes)
    OTP_EXPIRY_MINUTES = 10
    
    # Session expiry time (hours)
    SESSION_EXPIRY_HOURS = 8
    
    def __init__(self, db_path: str = "enterprise_auth.db"):
        """Initialize the authentication system"""
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize the SQLite database with enterprise tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    department TEXT NOT NULL,
                    company_domain TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    is_admin BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    login_count INTEGER DEFAULT 0
                )
            ''')
            
            # OTP table for email verification
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS otp_codes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    otp_code TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_used BOOLEAN DEFAULT 0,
                    attempts INTEGER DEFAULT 0
                )
            ''')
            
            # User sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')
            
            # Audit log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    ip_address TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')
            
            # Company settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS company_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT UNIQUE NOT NULL,
                    company_name TEXT NOT NULL,
                    admin_email TEXT NOT NULL,
                    smtp_server TEXT,
                    smtp_port INTEGER DEFAULT 587,
                    smtp_username TEXT,
                    smtp_password TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            
            # Insert default company settings
            self._setup_default_companies(cursor)
            conn.commit()
            
            conn.close()
            logger.info("Enterprise database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            raise
    
    def _setup_default_companies(self, cursor):
        """Setup default company configurations"""
        companies = [
            {
                'domain': 'hhamedicine.com',
                'company_name': 'HHA Medicine',
                'admin_email': 'admin@hhamedicine.com'
            },
            {
                'domain': 'hssmedicine.com', 
                'company_name': 'HSS Medicine',
                'admin_email': 'admin@hssmedicine.com'
            }
        ]
        
        for company in companies:
            cursor.execute('''
                INSERT OR IGNORE INTO company_settings 
                (domain, company_name, admin_email)
                VALUES (?, ?, ?)
            ''', (company['domain'], company['company_name'], company['admin_email']))
    
    def validate_email_domain(self, email: str) -> Tuple[bool, str]:
        """Validate if email belongs to allowed company domains"""
        if not email or '@' not in email:
            return False, "Invalid email format"
        
        domain = email.split('@')[1].lower()
        
        if domain not in self.ALLOWED_DOMAINS:
            return False, f"Access restricted to {' and '.join(self.ALLOWED_DOMAINS)} employees only"
        
        return True, domain
    
    def register_user(self, email: str, full_name: str, department: str) -> Dict:
        """Register a new enterprise user"""
        try:
            # Validate email domain
            is_valid, domain_or_error = self.validate_email_domain(email)
            if not is_valid:
                return {
                    'success': False,
                    'message': domain_or_error
                }
            
            domain = domain_or_error
            
            # Get company info
            company_info = self.get_company_info(domain)
            if not company_info:
                return {
                    'success': False,
                    'message': f"Company configuration not found for domain: {domain}"
                }
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute('SELECT id FROM users WHERE email = ?', (email.lower(),))
            if cursor.fetchone():
                conn.close()
                return {
                    'success': False,
                    'message': "User already registered. Please use login instead."
                }
            
            # Insert new user
            cursor.execute('''
                INSERT INTO users (email, full_name, department, company_domain)
                VALUES (?, ?, ?, ?)
            ''', (email.lower(), full_name.strip(), department.strip(), domain))
            
            user_id = cursor.lastrowid
            
            # Log the registration
            self._log_audit(cursor, user_id, "USER_REGISTERED", f"New user registered: {email}")
            
            conn.commit()
            conn.close()
            
            logger.info(f"New user registered: {email}")
            
            return {
                'success': True,
                'message': f"Registration successful! Welcome to {company_info['company_name']}",
                'user_id': user_id
            }
            
        except Exception as e:
            logger.error(f"User registration error: {str(e)}")
            return {
                'success': False,
                'message': "Registration failed. Please try again."
            }
    
    def generate_otp(self, email: str) -> Dict:
        """Generate OTP for email verification"""
        try:
            # Validate email domain first
            is_valid, domain_or_error = self.validate_email_domain(email)
            if not is_valid:
                return {
                    'success': False,
                    'message': domain_or_error
                }
            
            # Generate 6-digit OTP
            otp_code = f"{secrets.randbelow(900000) + 100000:06d}"
            
            # Calculate expiry time
            expires_at = datetime.now() + timedelta(minutes=self.OTP_EXPIRY_MINUTES)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Deactivate any existing OTPs for this email
            cursor.execute('''
                UPDATE otp_codes SET is_used = 1 
                WHERE email = ? AND is_used = 0
            ''', (email.lower(),))
            
            # Insert new OTP
            cursor.execute('''
                INSERT INTO otp_codes (email, otp_code, expires_at)
                VALUES (?, ?, ?)
            ''', (email.lower(), otp_code, expires_at))
            
            conn.commit()
            conn.close()
            
            # Send OTP via email
            email_sent = self.send_otp_email(email, otp_code, expires_at)
            
            if email_sent:
                logger.info(f"OTP generated and sent to: {email}")
                return {
                    'success': True,
                    'message': f"OTP sent to {email}. Valid for {self.OTP_EXPIRY_MINUTES} minutes.",
                    'expires_in_minutes': self.OTP_EXPIRY_MINUTES
                }
            else:
                return {
                    'success': False,
                    'message': "Failed to send OTP email. Please try again."
                }
                
        except Exception as e:
            logger.error(f"OTP generation error: {str(e)}")
            return {
                'success': False,
                'message': "Failed to generate OTP. Please try again."
            }
    
    def verify_otp(self, email: str, otp_code: str) -> Dict:
        """Verify OTP and create user session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find valid OTP
            cursor.execute('''
                SELECT id, expires_at, attempts FROM otp_codes
                WHERE email = ? AND otp_code = ? AND is_used = 0
                ORDER BY created_at DESC LIMIT 1
            ''', (email.lower(), otp_code))
            
            otp_record = cursor.fetchone()
            
            if not otp_record:
                # Increment attempt count for failed attempts
                cursor.execute('''
                    UPDATE otp_codes SET attempts = attempts + 1
                    WHERE email = ? AND is_used = 0
                ''', (email.lower(),))
                conn.commit()
                conn.close()
                
                return {
                    'success': False,
                    'message': "Invalid OTP code. Please check and try again."
                }
            
            otp_id, expires_at_str, attempts = otp_record
            expires_at = datetime.fromisoformat(expires_at_str)
            
            # Check if OTP has expired
            if datetime.now() > expires_at:
                cursor.execute('UPDATE otp_codes SET is_used = 1 WHERE id = ?', (otp_id,))
                conn.commit()
                conn.close()
                
                return {
                    'success': False,
                    'message': "OTP has expired. Please request a new one."
                }
            
            # Check attempt limits
            if attempts >= 3:
                cursor.execute('UPDATE otp_codes SET is_used = 1 WHERE id = ?', (otp_id,))
                conn.commit()
                conn.close()
                
                return {
                    'success': False,
                    'message': "Too many failed attempts. Please request a new OTP."
                }
            
            # Mark OTP as used
            cursor.execute('UPDATE otp_codes SET is_used = 1 WHERE id = ?', (otp_id,))
            
            # Get or create user
            cursor.execute('SELECT id, full_name, department, company_domain FROM users WHERE email = ?', (email.lower(),))
            user_record = cursor.fetchone()
            
            if not user_record:
                conn.close()
                return {
                    'success': False,
                    'message': "User not found. Please register first."
                }
            
            user_id, full_name, department, company_domain = user_record
            
            # Create session token
            session_token = secrets.token_urlsafe(32)
            session_expires = datetime.now() + timedelta(hours=self.SESSION_EXPIRY_HOURS)
            
            # Insert new session
            cursor.execute('''
                INSERT INTO user_sessions (user_id, session_token, expires_at)
                VALUES (?, ?, ?)
            ''', (user_id, session_token, session_expires))
            
            # Update user login stats
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP, login_count = login_count + 1
                WHERE id = ?
            ''', (user_id,))
            
            # Log successful login
            self._log_audit(cursor, user_id, "LOGIN_SUCCESS", f"Successful OTP login from {email}")
            
            conn.commit()
            conn.close()
            
            logger.info(f"Successful login: {email}")
            
            return {
                'success': True,
                'message': "Login successful!",
                'session_token': session_token,
                'user_data': {
                    'user_id': user_id,
                    'email': email,
                    'full_name': full_name,
                    'department': department,
                    'company_domain': company_domain,
                    'session_expires': session_expires.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"OTP verification error: {str(e)}")
            return {
                'success': False,
                'message': "Login failed. Please try again."
            }
    
    def validate_session(self, session_token: str) -> Dict:
        """Validate user session token"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.user_id, s.expires_at, u.email, u.full_name, u.department, u.company_domain
                FROM user_sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = ? AND s.is_active = 1
            ''', (session_token,))
            
            session_record = cursor.fetchone()
            
            if not session_record:
                conn.close()
                return {
                    'success': False,
                    'message': "Invalid session. Please login again."
                }
            
            user_id, expires_at_str, email, full_name, department, company_domain = session_record
            expires_at = datetime.fromisoformat(expires_at_str)
            
            # Check if session has expired
            if datetime.now() > expires_at:
                cursor.execute('UPDATE user_sessions SET is_active = 0 WHERE session_token = ?', (session_token,))
                conn.commit()
                conn.close()
                
                return {
                    'success': False,
                    'message': "Session expired. Please login again."
                }
            
            # Update last activity
            cursor.execute('''
                UPDATE user_sessions SET last_activity = CURRENT_TIMESTAMP
                WHERE session_token = ?
            ''', (session_token,))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'user_data': {
                    'user_id': user_id,
                    'email': email,
                    'full_name': full_name,
                    'department': department,
                    'company_domain': company_domain,
                    'session_expires': expires_at.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Session validation error: {str(e)}")
            return {
                'success': False,
                'message': "Session validation failed. Please login again."
            }
    
    def logout_user(self, session_token: str) -> Dict:
        """Logout user by invalidating session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user info before logout
            cursor.execute('''
                SELECT s.user_id, u.email FROM user_sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = ? AND s.is_active = 1
            ''', (session_token,))
            
            user_record = cursor.fetchone()
            
            # Deactivate session
            cursor.execute('''
                UPDATE user_sessions SET is_active = 0
                WHERE session_token = ?
            ''', (session_token,))
            
            if user_record:
                user_id, email = user_record
                self._log_audit(cursor, user_id, "LOGOUT", f"User logged out: {email}")
                logger.info(f"User logged out: {email}")
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': "Logged out successfully"
            }
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return {
                'success': False,
                'message': "Logout failed"
            }
    
    def get_company_info(self, domain: str) -> Optional[Dict]:
        """Get company information by domain"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT company_name, admin_email, smtp_server, smtp_port, smtp_username
                FROM company_settings WHERE domain = ? AND is_active = 1
            ''', (domain,))
            
            company_record = cursor.fetchone()
            conn.close()
            
            if company_record:
                return {
                    'company_name': company_record[0],
                    'admin_email': company_record[1],
                    'smtp_server': company_record[2],
                    'smtp_port': company_record[3],
                    'smtp_username': company_record[4]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Company info retrieval error: {str(e)}")
            return None
    
    def send_otp_email(self, email: str, otp_code: str, expires_at: datetime) -> bool:
        """Send OTP via email (placeholder - requires SMTP configuration)"""
        try:
            domain = email.split('@')[1]
            company_info = self.get_company_info(domain)
            
            if not company_info:
                logger.error(f"No company info found for domain: {domain}")
                return False
            
            # Create email content
            subject = f"Laude Agent - Login Verification Code"
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #1f4e79;">🎙️ Laude Agent - Login Verification</h2>
                
                <p>Hello,</p>
                
                <p>Your verification code for Laude Agent is:</p>
                
                <div style="background-color: #f0f8ff; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px;">
                    <h1 style="color: #1f4e79; font-size: 32px; margin: 0; letter-spacing: 5px;">{otp_code}</h1>
                </div>
                
                <p><strong>Important Details:</strong></p>
                <ul>
                    <li>This code expires at: {expires_at.strftime('%I:%M %p on %B %d, %Y')}</li>
                    <li>Valid for {self.OTP_EXPIRY_MINUTES} minutes only</li>
                    <li>Do not share this code with anyone</li>
                </ul>
                
                <p>If you didn't request this code, please ignore this email.</p>
                
                <hr style="margin: 30px 0;">
                <p style="color: #666; font-size: 12px;">
                    Laude Agent Enterprise System<br>
                    {company_info['company_name']}<br>
                    This is an automated message - please do not reply.
                </p>
            </body>
            </html>
            """
            
            # For development, save to file instead of sending
            # In production, implement actual SMTP sending
            self._save_email_to_file(email, subject, html_body, otp_code)
            
            logger.info(f"OTP email prepared for: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Email sending error: {str(e)}")
            return False
    
    def _save_email_to_file(self, email: str, subject: str, body: str, otp_code: str):
        """Save email to file for development purposes"""
        try:
            emails_dir = Path("otp_emails")
            emails_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = emails_dir / f"otp_{email.replace('@', '_at_')}_{timestamp}.html"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"<!-- OTP: {otp_code} -->\n")
                f.write(f"<!-- To: {email} -->\n")
                f.write(f"<!-- Subject: {subject} -->\n")
                f.write("<!-- " + "="*50 + " -->\n\n")
                f.write(body)
            
            # Also save simple text version for easy viewing
            text_file = emails_dir / f"otp_{email.replace('@', '_at_')}_{timestamp}.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(f"OTP CODE: {otp_code}\n")
                f.write(f"TO: {email}\n")
                f.write(f"EXPIRES: {datetime.now() + timedelta(minutes=self.OTP_EXPIRY_MINUTES)}\n")
                f.write("="*40 + "\n")
                f.write("FOR DEVELOPMENT: Email saved to file instead of sending\n")
            
            logger.info(f"Development: OTP email saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving email to file: {str(e)}")
    
    def _log_audit(self, cursor, user_id: int, action: str, details: str, ip_address: str = None):
        """Log audit trail"""
        cursor.execute('''
            INSERT INTO audit_log (user_id, action, details, ip_address)
            VALUES (?, ?, ?, ?)
        ''', (user_id, action, details, ip_address))
    
    def get_user_stats(self) -> Dict:
        """Get system usage statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total users
            cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
            total_users = cursor.fetchone()[0]
            
            # Users by domain
            cursor.execute('''
                SELECT company_domain, COUNT(*) FROM users 
                WHERE is_active = 1 GROUP BY company_domain
            ''')
            users_by_domain = dict(cursor.fetchall())
            
            # Active sessions
            cursor.execute('''
                SELECT COUNT(*) FROM user_sessions 
                WHERE is_active = 1 AND expires_at > datetime('now')
            ''')
            active_sessions = cursor.fetchone()[0]
            
            # Recent logins (last 24 hours)
            cursor.execute('''
                SELECT COUNT(*) FROM users 
                WHERE last_login > datetime('now', '-1 day')
            ''')
            recent_logins = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_users': total_users,
                'users_by_domain': users_by_domain,
                'active_sessions': active_sessions,
                'recent_logins_24h': recent_logins
            }
            
        except Exception as e:
            logger.error(f"Stats retrieval error: {str(e)}")
            return {}


# Example usage and testing
if __name__ == "__main__":
    # Initialize the enterprise auth system
    auth = EnterpriseAuth()
    
    print("Enterprise Authentication System - Test Mode")
    print("="*60)
    
    # Test user registration
    test_email = "john.doe@hhamedicine.com"
    print(f"\n1. Testing user registration: {test_email}")
    
    result = auth.register_user(test_email, "John Doe", "Technology Team")
    print(f"Registration result: {result}")
    
    if result['success']:
        # Test OTP generation
        print(f"\n2. Testing OTP generation for: {test_email}")
        otp_result = auth.generate_otp(test_email)
        print(f"OTP result: {otp_result}")
        
        if otp_result['success']:
            print(f"\nCheck 'otp_emails/' folder for the OTP code")
            
    # Show system stats
    print(f"\n3. System Statistics:")
    stats = auth.get_user_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print(f"\nEnterprise Authentication System initialized successfully!")
    print(f"Database: {auth.db_path}")
    print(f"Allowed domains: {', '.join(auth.ALLOWED_DOMAINS)}")