#!/usr/bin/env python3
"""
Azure Deployment Configuration for Laude Agent Enterprise
Web application wrapper for Azure App Service deployment
"""

from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from flask_cors import CORS
import os
import sys
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
import secrets

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth_system import EnterpriseAuth
from generate_professional_email import generate_professional_email

# Configure logging for Azure
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Enable CORS for cross-origin requests
CORS(app)

# Initialize authentication system
auth_system = EnterpriseAuth()

# HTML Templates for web interface
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Laude Agent Enterprise - Login</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1f4e79 0%, #2c5aa0 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .login-container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            padding: 40px;
            width: 100%;
            max-width: 400px;
        }
        
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .logo h1 {
            color: #1f4e79;
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        .logo p {
            color: #6c757d;
            font-size: 14px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #495057;
            font-weight: 600;
        }
        
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 6px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #1f4e79;
        }
        
        .btn {
            width: 100%;
            padding: 14px;
            background: #1f4e79;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        .btn:hover {
            background: #2c5aa0;
        }
        
        .btn:disabled {
            background: #6c757d;
            cursor: not-allowed;
        }
        
        .alert {
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .alert-info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        
        .domain-info {
            background: #e7f3ff;
            border: 1px solid #b8daff;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        
        .domain-info h4 {
            color: #1f4e79;
            margin-bottom: 8px;
        }
        
        .domain-info ul {
            margin-left: 20px;
        }
        
        .domain-info li {
            margin-bottom: 5px;
            color: #495057;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e9ecef;
            font-size: 12px;
            color: #6c757d;
        }
        
        .loading {
            display: none;
            text-align: center;
            color: #1f4e79;
        }
        
        @media (max-width: 480px) {
            .login-container {
                margin: 20px;
                padding: 30px 20px;
            }
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>🎙️ Laude Agent</h1>
            <p>Enterprise Voice-to-Email Platform</p>
        </div>
        
        {% if message %}
        <div class="alert alert-{{ message_type }}">
            {{ message }}
        </div>
        {% endif %}
        
        {% if step == 'email' %}
        <form method="POST" action="/login" id="emailForm">
            <div class="form-group">
                <label for="email">Corporate Email Address</label>
                <input type="email" id="email" name="email" required 
                       placeholder="yourname@hhamedicine.com" value="{{ email or '' }}">
            </div>
            
            <div class="domain-info">
                <h4>🔒 Access Restricted</h4>
                <ul>
                    <li>Only @hhamedicine.com and @hssmedicine.com employees</li>
                    <li>OTP verification required for secure access</li>
                </ul>
            </div>
            
            <button type="submit" class="btn" id="continueBtn">Continue with Email</button>
            
            <div class="loading" id="loading">
                <p>🔄 Generating verification code...</p>
            </div>
        </form>
        
        {% elif step == 'otp' %}
        <form method="POST" action="/verify-otp" id="otpForm">
            <h3 style="text-align: center; margin-bottom: 20px; color: #1f4e79;">Email Verification</h3>
            <p style="text-align: center; margin-bottom: 25px; color: #6c757d;">
                Enter the 6-digit code sent to<br><strong>{{ session.email }}</strong>
            </p>
            
            <div class="form-group">
                <label for="otp_code">Verification Code</label>
                <input type="text" id="otp_code" name="otp_code" required 
                       maxlength="6" pattern="[0-9]{6}" 
                       placeholder="123456" style="text-align: center; font-size: 20px; letter-spacing: 3px;">
            </div>
            
            <div style="text-align: center; margin-bottom: 20px;">
                <small style="color: #6c757d;">Code expires in: <span id="timer">10:00</span></small>
            </div>
            
            <button type="submit" class="btn" id="verifyBtn">Verify & Login</button>
            
            <div style="text-align: center; margin-top: 15px;">
                <a href="/resend-otp" style="color: #1f4e79; text-decoration: none; font-size: 14px;">
                    Didn't receive code? Resend
                </a>
            </div>
            
            <div class="loading" id="loading">
                <p>🔄 Verifying code...</p>
            </div>
        </form>
        
        <script>
            // OTP timer countdown
            let timeLeft = 600; // 10 minutes in seconds
            const timer = document.getElementById('timer');
            
            function updateTimer() {
                const minutes = Math.floor(timeLeft / 60);
                const seconds = timeLeft % 60;
                timer.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
                
                if (timeLeft > 0) {
                    timeLeft--;
                    setTimeout(updateTimer, 1000);
                } else {
                    timer.textContent = 'Expired';
                    timer.style.color = '#dc3545';
                }
            }
            
            updateTimer();
            
            // Auto-focus OTP input
            document.getElementById('otp_code').focus();
        </script>
        {% endif %}
        
        <div class="footer">
            <p>Laude Agent Enterprise System<br>
            Secure authentication for healthcare organizations</p>
        </div>
    </div>
    
    <script>
        // Form submission loading states
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function() {
                const loading = document.getElementById('loading');
                const btn = form.querySelector('.btn');
                if (loading && btn) {
                    loading.style.display = 'block';
                    btn.disabled = true;
                }
            });
        });
    </script>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Laude Agent Enterprise - Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f8f9fa;
            min-height: 100vh;
        }
        
        .header {
            background: #1f4e79;
            color: white;
            padding: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            font-size: 24px;
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .user-details {
            text-align: right;
        }
        
        .user-details h3 {
            font-size: 16px;
            margin-bottom: 5px;
        }
        
        .user-details p {
            font-size: 12px;
            opacity: 0.8;
        }
        
        .logout-btn {
            background: #dc3545;
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        
        .logout-btn:hover {
            background: #c82333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        .welcome-card {
            background: white;
            border-radius: 8px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .welcome-card h2 {
            color: #1f4e79;
            margin-bottom: 10px;
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .feature-card {
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
        }
        
        .feature-card h3 {
            color: #1f4e79;
            margin-bottom: 15px;
            font-size: 20px;
        }
        
        .feature-card p {
            color: #6c757d;
            margin-bottom: 20px;
            line-height: 1.5;
        }
        
        .feature-btn {
            background: #1f4e79;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: background-color 0.3s;
            text-decoration: none;
            display: inline-block;
        }
        
        .feature-btn:hover {
            background: #2c5aa0;
        }
        
        .feature-btn.secondary {
            background: #28a745;
        }
        
        .feature-btn.secondary:hover {
            background: #218838;
        }
        
        .status-bar {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            justify-content: between;
            align-items: center;
        }
        
        .status-text {
            color: #28a745;
            font-weight: 600;
        }
        
        .session-info {
            color: #6c757d;
            font-size: 14px;
        }
        
        @media (max-width: 768px) {
            .header-content {
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }
            
            .features-grid {
                grid-template-columns: 1fr;
            }
            
            .container {
                padding: 20px 15px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <h1>🎙️ Laude Agent Enterprise</h1>
            <div class="user-info">
                <div class="user-details">
                    <h3>{{ user_data.full_name }}</h3>
                    <p>{{ user_data.department }} • {{ user_data.company_domain.upper() }}</p>
                </div>
                <form method="POST" action="/logout" style="display: inline;">
                    <button type="submit" class="logout-btn">Logout</button>
                </form>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="welcome-card">
            <h2>Welcome back, {{ user_data.full_name.split()[0] }}! 👋</h2>
            <p>Your professional voice-to-email assistant is ready to help you create polished weekly updates.</p>
        </div>
        
        <div class="features-grid">
            <div class="feature-card">
                <h3>🎙️ Voice Recording</h3>
                <p>Record your weekly updates using advanced voice recognition. Speak naturally and let AI transform your words into professional emails.</p>
                <button class="feature-btn" onclick="startVoiceRecording()">Start Recording</button>
            </div>
            
            <div class="feature-card">
                <h3>📧 Quick Email</h3>
                <p>Generate a professional email template instantly. Perfect for when you need a structured format to get started.</p>
                <button class="feature-btn secondary" onclick="generateQuickEmail()">Generate Email</button>
            </div>
            
            <div class="feature-card">
                <h3>📊 Analytics</h3>
                <p>View your usage statistics, email history, and performance metrics. Track your productivity over time.</p>
                <button class="feature-btn" onclick="viewAnalytics()" disabled>Coming Soon</button>
            </div>
        </div>
        
        <div class="status-bar">
            <div class="status-text">🟢 System Online - All services operational</div>
            <div class="session-info">Session expires: {{ session_expires }}</div>
        </div>
    </div>
    
    <script>
        function startVoiceRecording() {
            alert('Voice recording feature will be available in the next update!\n\nFor now, you can use the Quick Email feature to see how the system works.');
        }
        
        function generateQuickEmail() {
            if (confirm('Generate a sample professional email based on your profile?')) {
                window.location.href = '/generate-email';
            }
        }
        
        function viewAnalytics() {
            alert('Analytics dashboard coming soon!\n\nThis will show your usage statistics, email history, and productivity metrics.');
        }
        
        // Session warning (5 minutes before expiry)
        setTimeout(function() {
            if (confirm('Your session will expire soon. Would you like to extend it?')) {
                window.location.reload();
            }
        }, {{ session_warning_ms }});
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Home page - redirect to login or dashboard"""
    if 'user_id' in session and 'session_token' in session:
        # Validate existing session
        result = auth_system.validate_session(session['session_token'])
        if result['success']:
            return redirect(url_for('dashboard'))
        else:
            session.clear()
    
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with email input and OTP generation"""
    if request.method == 'GET':
        return render_template_string(LOGIN_TEMPLATE, 
                                    step='email', 
                                    message=request.args.get('message'),
                                    message_type=request.args.get('type', 'info'))
    
    # POST request - process email
    email = request.form.get('email', '').strip().lower()
    
    if not email:
        return render_template_string(LOGIN_TEMPLATE, 
                                    step='email',
                                    message="Please enter your email address",
                                    message_type='error',
                                    email=email)
    
    # Generate OTP
    result = auth_system.generate_otp(email)
    
    if result['success']:
        session['email'] = email
        session['otp_generated'] = datetime.now().isoformat()
        
        return render_template_string(LOGIN_TEMPLATE, 
                                    step='otp',
                                    message=f"Verification code sent to {email}")
    else:
        return render_template_string(LOGIN_TEMPLATE, 
                                    step='email',
                                    message=result['message'],
                                    message_type='error',
                                    email=email)

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP and create session"""
    email = session.get('email')
    otp_code = request.form.get('otp_code', '').strip()
    
    if not email or not otp_code:
        return render_template_string(LOGIN_TEMPLATE, 
                                    step='otp',
                                    message="Please enter the verification code",
                                    message_type='error')
    
    # Verify OTP
    result = auth_system.verify_otp(email, otp_code)
    
    if result['success']:
        # Create session
        session['user_id'] = result['user_data']['user_id']
        session['session_token'] = result['session_token']
        session['user_data'] = result['user_data']
        session.permanent = True
        
        logger.info(f"Successful login: {email}")
        return redirect(url_for('dashboard'))
    else:
        return render_template_string(LOGIN_TEMPLATE, 
                                    step='otp',
                                    message=result['message'],
                                    message_type='error')

@app.route('/resend-otp')
def resend_otp():
    """Resend OTP code"""
    email = session.get('email')
    
    if not email:
        return redirect(url_for('login'))
    
    result = auth_system.generate_otp(email)
    
    if result['success']:
        session['otp_generated'] = datetime.now().isoformat()
        return render_template_string(LOGIN_TEMPLATE, 
                                    step='otp',
                                    message="New verification code sent!",
                                    message_type='success')
    else:
        return render_template_string(LOGIN_TEMPLATE, 
                                    step='otp',
                                    message=result['message'],
                                    message_type='error')

@app.route('/dashboard')
def dashboard():
    """Main application dashboard"""
    if 'user_id' not in session or 'session_token' not in session:
        return redirect(url_for('login'))
    
    # Validate session
    result = auth_system.validate_session(session['session_token'])
    
    if not result['success']:
        session.clear()
        return redirect(url_for('login', message="Session expired", type="error"))
    
    # Update user data
    user_data = result['user_data']
    session['user_data'] = user_data
    
    # Calculate session expiry warning (5 minutes before)
    expires_at = datetime.fromisoformat(user_data['session_expires'])
    warning_time = expires_at - timedelta(minutes=5)
    session_warning_ms = max(0, int((warning_time - datetime.now()).total_seconds() * 1000))
    
    return render_template_string(DASHBOARD_TEMPLATE, 
                                user_data=user_data,
                                session_expires=expires_at.strftime('%I:%M %p'),
                                session_warning_ms=session_warning_ms)

@app.route('/generate-email')
def generate_email():
    """Generate sample professional email"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_data = session.get('user_data', {})
    
    # Sample transcript for demo
    sample_transcript = f"""
    This week at {user_data.get('company_domain', 'company').split('.')[0].upper()} I completed several important initiatives.
    I collaborated with team members on various projects and maintained operational excellence.
    System performance was optimal throughout the week with no significant issues.
    I participated in training sessions and contributed to process improvements.
    Next week I'm planning to focus on strategic objectives and continued development.
    Key achievements include maintaining quality standards and supporting team goals.
    """
    
    try:
        company_name = user_data.get('company_domain', 'company').split('.')[0].upper() + " Medicine"
        
        email_content = generate_professional_email(
            sample_transcript,
            user_data.get('full_name', 'User'),
            company_name,
            user_data.get('department', 'Team')
        )
        
        if email_content:
            # Return as JSON for AJAX or as HTML
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({
                    'success': True,
                    'email_content': email_content
                })
            
            # Return as HTML page
            email_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Generated Professional Email</title>
                <style>
                    body {{ font-family: 'Segoe UI', sans-serif; max-width: 800px; margin: 0 auto; padding: 40px 20px; }}
                    .email-container {{ background: white; border: 1px solid #e9ecef; border-radius: 8px; padding: 30px; }}
                    .email-content {{ font-family: 'Courier New', monospace; white-space: pre-line; line-height: 1.6; }}
                    .header {{ background: #1f4e79; color: white; padding: 20px; margin: -30px -30px 30px -30px; border-radius: 8px 8px 0 0; }}
                    .actions {{ text-align: center; margin-top: 30px; }}
                    .btn {{ background: #1f4e79; color: white; padding: 12px 24px; border: none; border-radius: 6px; margin: 0 10px; cursor: pointer; text-decoration: none; display: inline-block; }}
                    .btn:hover {{ background: #2c5aa0; }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="header">
                        <h1>📧 Generated Professional Email</h1>
                        <p>AI-powered voice-to-email transformation</p>
                    </div>
                    <div class="email-content">{email_content}</div>
                    <div class="actions">
                        <button class="btn" onclick="copyToClipboard()">Copy to Clipboard</button>
                        <a href="/dashboard" class="btn">Back to Dashboard</a>
                    </div>
                </div>
                
                <script>
                    function copyToClipboard() {{
                        const content = document.querySelector('.email-content').textContent;
                        navigator.clipboard.writeText(content).then(function() {{
                            alert('Email content copied to clipboard!');
                        }});
                    }}
                </script>
            </body>
            </html>
            """
            
            return email_html
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to generate email'
            }), 500
            
    except Exception as e:
        logger.error(f"Email generation error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Email generation failed'
        }), 500

@app.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    session_token = session.get('session_token')
    
    if session_token:
        auth_system.logout_user(session_token)
    
    session.clear()
    return redirect(url_for('login', message="Logged out successfully", type="success"))

@app.route('/api/user-stats')
def user_stats():
    """API endpoint for user statistics"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        stats = auth_system.get_user_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return jsonify({'error': 'Failed to fetch stats'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Azure monitoring"""
    try:
        # Test database connection
        stats = auth_system.get_user_stats()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'database': 'connected',
            'auth_system': 'operational',
            'total_users': stats.get('total_users', 0)
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Page not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

# Azure startup
def create_app():
    """Application factory for Azure deployment"""
    
    # Create required directories
    directories = ["otp_emails", "logs", "emails", "reports", "transcripts"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    # Configure session
    app.permanent_session_lifetime = timedelta(hours=8)
    
    logger.info("Laude Agent Enterprise application started")
    logger.info(f"Allowed domains: {', '.join(auth_system.ALLOWED_DOMAINS)}")
    
    return app

# For local development
if __name__ == '__main__':
    app = create_app()
    
    # Development mode
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 8000)),
        debug=os.environ.get('FLASK_ENV') == 'development'
    )