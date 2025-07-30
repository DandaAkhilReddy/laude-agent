#!/usr/bin/env python3
"""
Enterprise Laude Agent - FastAPI Backend
Real-world voice-to-email automation platform for HSS Medicine
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
import os
import uuid
import secrets
import smtplib
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# MongoDB imports
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# OpenAI imports
import openai
import json
from pathlib import Path

# Initialize FastAPI
app = FastAPI(
    title="Laude Agent Enterprise API",
    description="Voice-to-Email Automation Platform for HSS Medicine",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COMPANY_DOMAIN = "hssmedicine.com"
OTP_EXPIRY_MINUTES = 10
SESSION_EXPIRY_HOURS = 8

# Initialize MongoDB
client = AsyncIOMotorClient(MONGO_URL)
db = client.laude_agent

# Initialize OpenAI
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create directories
for directory in ["audio_clips", "reports", "transcripts", "automation_requests"]:
    Path(directory).mkdir(exist_ok=True)

# Pydantic Models
class UserRegistration(BaseModel):
    email: EmailStr
    full_name: str
    department: str

class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerification(BaseModel):
    email: EmailStr
    otp_code: str

class ReportGeneration(BaseModel):
    transcript: str
    user_id: str

class AutomationRequest(BaseModel):
    title: str
    description: str
    priority: str = "medium"
    user_id: str

class ChatMessage(BaseModel):
    request_id: str
    message: str
    sender_type: str  # "user" or "admin"
    user_id: str

class AdminUpdate(BaseModel):
    request_id: str
    status: str
    admin_notes: Optional[str] = None

# Helper Functions
def generate_otp() -> str:
    """Generate 6-digit OTP"""
    return f"{secrets.randbelow(900000) + 100000:06d}"

def generate_session_token() -> str:
    """Generate secure session token"""
    return secrets.token_urlsafe(32)

async def send_otp_email(email: str, otp_code: str) -> bool:
    """Send OTP via email - Development version saves to file"""
    try:
        # Create email content
        subject = "HSS Medicine - Laude Agent Login Code"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #1f4e79 0%, #2c5aa0 100%); color: white; padding: 30px; text-align: center;">
                <h1 style="margin: 0;">🎙️ Laude Agent</h1>
                <p style="margin: 10px 0 0 0;">HSS Medicine Enterprise Platform</p>
            </div>
            
            <div style="padding: 40px 30px;">
                <h2 style="color: #1f4e79; margin-bottom: 20px;">Login Verification Code</h2>
                
                <p>Hello,</p>
                
                <p>Your verification code for Laude Agent is:</p>
                
                <div style="background-color: #f0f8ff; padding: 25px; text-align: center; margin: 25px 0; border-radius: 8px; border: 2px solid #1f4e79;">
                    <h1 style="color: #1f4e79; font-size: 36px; margin: 0; letter-spacing: 8px; font-family: 'Courier New', monospace;">{otp_code}</h1>
                </div>
                
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 6px; margin: 20px 0;">
                    <p style="margin: 0; color: #856404;"><strong>⏰ Important:</strong></p>
                    <ul style="margin: 10px 0; color: #856404;">
                        <li>This code expires in {OTP_EXPIRY_MINUTES} minutes</li>
                        <li>Valid for one-time use only</li>
                        <li>Do not share this code</li>
                    </ul>
                </div>
                
                <p>If you didn't request this code, please ignore this email.</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; text-align: center; color: #6c757d; font-size: 12px;">
                <p style="margin: 0;"><strong>HSS Medicine - Laude Agent</strong></p>
                <p style="margin: 5px 0 0 0;">Enterprise Voice-to-Email Automation Platform</p>
                <p style="margin: 5px 0 0 0;">Confidential - For Internal Use Only</p>
            </div>
        </body>
        </html>
        """
        
        # Save to file for development
        emails_dir = Path("otp_emails")
        emails_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = emails_dir / f"otp_{email.replace('@', '_at_')}_{timestamp}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"<!-- OTP: {otp_code} -->\n")
            f.write(f"<!-- To: {email} -->\n")
            f.write(f"<!-- Subject: {subject} -->\n\n")
            f.write(html_body)
        
        logger.info(f"OTP email saved for development: {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Email sending error: {str(e)}")
        return False

async def validate_session(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate user session token"""
    try:
        token = credentials.credentials
        
        # Check session in database
        session = await db.sessions.find_one({
            "session_token": token,
            "is_active": True,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not session:
            raise HTTPException(status_code=401, detail="Invalid or expired session")
        
        # Update last activity
        await db.sessions.update_one(
            {"session_token": token},
            {"$set": {"last_activity": datetime.utcnow()}}
        )
        
        # Get user data
        user = await db.users.find_one({"_id": session["user_id"]})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return {
            "user_id": str(user["_id"]),
            "email": user["email"],
            "full_name": user["full_name"],
            "department": user["department"],
            "is_admin": user.get("is_admin", False)
        }
        
    except Exception as e:
        logger.error(f"Session validation error: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Laude Agent Enterprise API",
        "version": "2.0.0",
        "status": "operational",
        "company": "HSS Medicine",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/auth/register")
async def register_user(user_data: UserRegistration):
    """Register new user with domain validation"""
    try:
        # Validate domain
        if not user_data.email.endswith(f"@{COMPANY_DOMAIN}"):
            raise HTTPException(
                status_code=400, 
                detail=f"Access restricted to {COMPANY_DOMAIN} employees only"
            )
        
        # Check if user exists
        existing_user = await db.users.find_one({"email": user_data.email.lower()})
        if existing_user:
            raise HTTPException(status_code=400, detail="User already registered")
        
        # Create user
        user_doc = {
            "_id": str(uuid.uuid4()),
            "email": user_data.email.lower(),
            "full_name": user_data.full_name.strip(),
            "department": user_data.department.strip(),
            "company_domain": COMPANY_DOMAIN,
            "is_active": True,
            "is_admin": False,
            "created_at": datetime.utcnow(),
            "login_count": 0
        }
        
        await db.users.insert_one(user_doc)
        
        logger.info(f"New user registered: {user_data.email}")
        
        return {
            "success": True,
            "message": f"Registration successful! Welcome to HSS Medicine.",
            "user_id": user_doc["_id"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/api/auth/generate-otp")
async def generate_otp_endpoint(otp_request: OTPRequest):
    """Generate and send OTP"""
    try:
        # Validate domain
        if not otp_request.email.endswith(f"@{COMPANY_DOMAIN}"):
            raise HTTPException(
                status_code=400,
                detail=f"Access restricted to {COMPANY_DOMAIN} employees only"
            )
        
        # Generate OTP
        otp_code = generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)
        
        # Deactivate existing OTPs
        await db.otp_codes.update_many(
            {"email": otp_request.email.lower(), "is_used": False},
            {"$set": {"is_used": True}}
        )
        
        # Store new OTP
        otp_doc = {
            "_id": str(uuid.uuid4()),
            "email": otp_request.email.lower(),
            "otp_code": otp_code,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "is_used": False,
            "attempts": 0
        }
        
        await db.otp_codes.insert_one(otp_doc)
        
        # Send OTP email
        email_sent = await send_otp_email(otp_request.email, otp_code)
        
        if email_sent:
            return {
                "success": True,
                "message": f"OTP sent to {otp_request.email}. Valid for {OTP_EXPIRY_MINUTES} minutes.",
                "expires_in_minutes": OTP_EXPIRY_MINUTES
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OTP email")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OTP generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate OTP")

@app.post("/api/auth/verify-otp")
async def verify_otp_endpoint(verification: OTPVerification):
    """Verify OTP and create session"""
    try:
        # Find valid OTP
        otp_record = await db.otp_codes.find_one({
            "email": verification.email.lower(),
            "otp_code": verification.otp_code,
            "is_used": False,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not otp_record:
            # Increment attempts
            await db.otp_codes.update_many(
                {"email": verification.email.lower(), "is_used": False},
                {"$inc": {"attempts": 1}}
            )
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        
        # Check attempt limits
        if otp_record["attempts"] >= 3:
            await db.otp_codes.update_one(
                {"_id": otp_record["_id"]},
                {"$set": {"is_used": True}}
            )
            raise HTTPException(status_code=400, detail="Too many failed attempts")
        
        # Mark OTP as used
        await db.otp_codes.update_one(
            {"_id": otp_record["_id"]},
            {"$set": {"is_used": True}}
        )
        
        # Get or create user
        user = await db.users.find_one({"email": verification.email.lower()})
        if not user:
            raise HTTPException(status_code=404, detail="User not found. Please register first.")
        
        # Create session
        session_token = generate_session_token()
        session_expires = datetime.utcnow() + timedelta(hours=SESSION_EXPIRY_HOURS)
        
        session_doc = {
            "_id": str(uuid.uuid4()),
            "user_id": user["_id"],
            "session_token": session_token,
            "created_at": datetime.utcnow(),
            "expires_at": session_expires,
            "is_active": True,
            "last_activity": datetime.utcnow()
        }
        
        await db.sessions.insert_one(session_doc)
        
        # Update user login stats
        await db.users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {"last_login": datetime.utcnow()},
                "$inc": {"login_count": 1}
            }
        )
        
        logger.info(f"Successful login: {verification.email}")
        
        return {
            "success": True,
            "message": "Login successful!",
            "session_token": session_token,
            "user_data": {
                "user_id": user["_id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "department": user["department"],
                "company_domain": user["company_domain"],
                "is_admin": user.get("is_admin", False),
                "session_expires": session_expires.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OTP verification error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/api/auth/logout")
async def logout(user_data: dict = Depends(validate_session)):
    """Logout user"""
    try:
        # Deactivate all sessions for user
        await db.sessions.update_many(
            {"user_id": user_data["user_id"]},
            {"$set": {"is_active": False}}
        )
        
        logger.info(f"User logged out: {user_data['email']}")
        
        return {"success": True, "message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(status_code=500, detail="Logout failed")

@app.post("/api/reports/generate")
async def generate_report(
    report_data: ReportGeneration,
    user_data: dict = Depends(validate_session)
):
    """Generate professional report from transcript"""
    try:
        if not OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="OpenAI API not configured")
        
        # Enhanced system prompt for HSS Medicine
        system_prompt = """You are a specialized AI assistant for HSS Medicine healthcare technology team. You create standardized weekly reports with EXACT consistency.

CRITICAL BEHAVIORAL RULES:
1. ALWAYS follow the template structure precisely - never deviate
2. Use IDENTICAL section headings every time
3. Maintain professional healthcare IT terminology consistently
4. Include specific metrics and measurable outcomes
5. Always relate work back to patient care impact when possible
6. Use the same formatting style every time
7. Keep the tone authoritative but accessible to healthcare executives
8. Never skip sections - if information is missing, note "No updates this week"
9. Always quantify achievements with numbers and percentages when possible
10. Focus on healthcare technology improvements and patient outcomes

Create a comprehensive weekly report with this EXACT structure:

## 📋 Executive Summary
[Brief overview of the week's main accomplishments and healthcare technology focus areas]

## ✅ Completed Tasks
[List of tasks, projects, or activities completed this week with healthcare impact]

## 🔄 In Progress
[Current ongoing projects and their status - focus on patient care improvements]

## 📅 Upcoming Priorities
[Tasks and goals for next week - emphasize healthcare technology advancement]

## 🚧 Challenges & Solutions
[Any issues encountered and how they were addressed - healthcare context]

## 📊 Key Metrics & Results
[Quantifiable achievements, numbers, results - patient care metrics when applicable]

## 💡 Notes & Insights
[Additional observations, learnings, or important points for healthcare technology]

Use professional business language appropriate for healthcare executives."""

        # User prompt
        user_prompt = f"""TRANSCRIPT TO PROCESS:
{report_data.transcript}

Please create a comprehensive weekly report following the exact template structure. Make it suitable for HSS Medicine healthcare executives. Focus on healthcare technology achievements and patient care impact when applicable.

Current date: {datetime.now().strftime('%B %d, %Y')}"""

        # Generate report using OpenAI
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=2500,
            temperature=0.1
        )
        
        if not response.choices or not response.choices[0].message:
            raise HTTPException(status_code=500, detail="Failed to generate report")
        
        report_content = response.choices[0].message.content
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_id = str(uuid.uuid4())
        
        # Save transcript
        transcript_path = f"transcripts/transcript_{user_data['user_id']}_{timestamp}.txt"
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(report_data.transcript)
        
        # Save report
        report_path = f"reports/report_{user_data['user_id']}_{timestamp}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # Store in database
        report_doc = {
            "_id": report_id,
            "user_id": user_data["user_id"],
            "transcript": report_data.transcript,
            "report_content": report_content,
            "transcript_path": transcript_path,
            "report_path": report_path,
            "created_at": datetime.utcnow(),
            "tokens_used": response.usage.total_tokens if response.usage else 0
        }
        
        await db.reports.insert_one(report_doc)
        
        logger.info(f"Report generated for user: {user_data['email']}")
        
        return {
            "success": True,
            "report_id": report_id,
            "report_content": report_content,
            "tokens_used": response.usage.total_tokens if response.usage else 0,
            "created_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate report")

@app.get("/api/reports/history")
async def get_report_history(user_data: dict = Depends(validate_session)):
    """Get user's report history"""
    try:
        reports = await db.reports.find(
            {"user_id": user_data["user_id"]},
            {"report_content": 0}  # Exclude large content
        ).sort("created_at", -1).limit(50).to_list(50)
        
        return {
            "success": True,
            "reports": reports
        }
        
    except Exception as e:
        logger.error(f"Report history error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch report history")

# Automation Requests Endpoints

@app.post("/api/automation/requests")
async def create_automation_request(
    request_data: AutomationRequest,
    user_data: dict = Depends(validate_session)
):
    """Create new automation request"""
    try:
        request_id = str(uuid.uuid4())
        
        request_doc = {
            "_id": request_id,
            "title": request_data.title.strip(),
            "description": request_data.description.strip(),
            "priority": request_data.priority,
            "status": "pending",
            "user_id": user_data["user_id"],
            "user_name": user_data["full_name"],
            "user_email": user_data["email"],
            "user_department": user_data["department"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "admin_notes": None
        }
        
        await db.automation_requests.insert_one(request_doc)
        
        logger.info(f"Automation request created: {request_id} by {user_data['email']}")
        
        return {
            "success": True,
            "message": "Automation request created successfully",
            "request_id": request_id,
            "request": request_doc
        }
        
    except Exception as e:
        logger.error(f"Create automation request error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create automation request")

@app.get("/api/automation/requests")
async def get_user_automation_requests(user_data: dict = Depends(validate_session)):
    """Get user's automation requests"""
    try:
        requests = await db.automation_requests.find(
            {"user_id": user_data["user_id"]}
        ).sort("created_at", -1).to_list(100)
        
        return {
            "success": True,
            "requests": requests
        }
        
    except Exception as e:
        logger.error(f"Get automation requests error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch automation requests")

@app.put("/api/automation/requests/{request_id}")
async def update_automation_request(
    request_id: str,
    update_data: dict,
    user_data: dict = Depends(validate_session)
):
    """Update automation request (user can only update own requests)"""
    try:
        # Check if request exists and belongs to user
        request = await db.automation_requests.find_one({
            "_id": request_id,
            "user_id": user_data["user_id"]
        })
        
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        # Update allowed fields
        update_fields = {}
        if "title" in update_data:
            update_fields["title"] = update_data["title"].strip()
        if "description" in update_data:
            update_fields["description"] = update_data["description"].strip()
        if "priority" in update_data:
            update_fields["priority"] = update_data["priority"]
        
        update_fields["updated_at"] = datetime.utcnow()
        
        await db.automation_requests.update_one(
            {"_id": request_id},
            {"$set": update_fields}
        )
        
        logger.info(f"Automation request updated: {request_id} by {user_data['email']}")
        
        return {
            "success": True,
            "message": "Request updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Update automation request error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update automation request")

@app.post("/api/automation/requests/{request_id}/messages")
async def add_message_to_request(
    request_id: str,
    message_data: ChatMessage,
    user_data: dict = Depends(validate_session)
):
    """Add message to automation request chat"""
    try:
        # Verify request exists and user has access
        request = await db.automation_requests.find_one({"_id": request_id})
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        # Check user access (owner or admin)
        if request["user_id"] != user_data["user_id"] and not user_data.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Access denied")
        
        message_id = str(uuid.uuid4())
        message_doc = {
            "_id": message_id,
            "request_id": request_id,
            "message": message_data.message.strip(),
            "sender_type": message_data.sender_type,
            "sender_name": user_data["full_name"],
            "sender_email": user_data["email"],
            "created_at": datetime.utcnow()
        }
        
        await db.chat_messages.insert_one(message_doc)
        
        # Update request timestamp
        await db.automation_requests.update_one(
            {"_id": request_id},
            {"$set": {"updated_at": datetime.utcnow()}}
        )
        
        logger.info(f"Message added to request {request_id} by {user_data['email']}")
        
        return {
            "success": True,
            "message": "Message added successfully",
            "message_id": message_id
        }
        
    except Exception as e:
        logger.error(f"Add message error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add message")

@app.get("/api/automation/requests/{request_id}/messages")
async def get_request_messages(
    request_id: str,
    user_data: dict = Depends(validate_session)
):
    """Get messages for automation request"""
    try:
        # Verify request exists and user has access
        request = await db.automation_requests.find_one({"_id": request_id})
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        # Check user access (owner or admin)
        if request["user_id"] != user_data["user_id"] and not user_data.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Access denied")
        
        messages = await db.chat_messages.find(
            {"request_id": request_id}
        ).sort("created_at", 1).to_list(1000)
        
        return {
            "success": True,
            "messages": messages
        }
        
    except Exception as e:
        logger.error(f"Get messages error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch messages")

# Admin Endpoints

@app.get("/api/admin/requests")
async def get_all_automation_requests(user_data: dict = Depends(validate_session)):
    """Get all automation requests (admin only)"""
    try:
        if not user_data.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        requests = await db.automation_requests.find({}).sort("created_at", -1).to_list(1000)
        
        return {
            "success": True,
            "requests": requests
        }
        
    except Exception as e:
        logger.error(f"Get all requests error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch requests")

@app.put("/api/admin/requests/{request_id}/status")
async def update_request_status(
    request_id: str,
    status_data: AdminUpdate,
    user_data: dict = Depends(validate_session)
):
    """Update request status (admin only)"""
    try:
        if not user_data.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Verify request exists
        request = await db.automation_requests.find_one({"_id": request_id})
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        # Update request
        update_fields = {
            "status": status_data.status,
            "updated_at": datetime.utcnow()
        }
        
        if status_data.admin_notes:
            update_fields["admin_notes"] = status_data.admin_notes.strip()
        
        await db.automation_requests.update_one(
            {"_id": request_id},
            {"$set": update_fields}
        )
        
        # Add admin message if notes provided
        if status_data.admin_notes:
            message_doc = {
                "_id": str(uuid.uuid4()),
                "request_id": request_id,
                "message": f"Status updated to '{status_data.status}': {status_data.admin_notes}",
                "sender_type": "admin",
                "sender_name": user_data["full_name"],
                "sender_email": user_data["email"],
                "created_at": datetime.utcnow()
            }
            await db.chat_messages.insert_one(message_doc)
        
        logger.info(f"Request status updated: {request_id} to {status_data.status} by {user_data['email']}")
        
        return {
            "success": True,
            "message": "Request status updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Update request status error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update request status")

@app.get("/api/admin/stats")
async def get_admin_stats(user_data: dict = Depends(validate_session)):
    """Get admin statistics"""
    try:
        if not user_data.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Get request stats
        total_requests = await db.automation_requests.count_documents({})
        pending_requests = await db.automation_requests.count_documents({"status": "pending"})
        in_progress_requests = await db.automation_requests.count_documents({"status": "in_progress"})
        completed_requests = await db.automation_requests.count_documents({"status": "completed"})
        
        # Get user stats
        total_users = await db.users.count_documents({"is_active": True})
        recent_users = await db.users.count_documents({
            "last_login": {"$gte": datetime.utcnow() - timedelta(days=30)}
        })
        
        return {
            "success": True,
            "stats": {
                "total_requests": total_requests,
                "pending_requests": pending_requests,
                "in_progress_requests": in_progress_requests,
                "completed_requests": completed_requests,
                "total_users": total_users,
                "active_users": recent_users,
                "completion_rate": round((completed_requests / max(total_requests, 1)) * 100, 1)
            }
        }
        
    except Exception as e:
        logger.error(f"Get admin stats error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch admin statistics")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)