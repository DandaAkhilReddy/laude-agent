#!/usr/bin/env python3
"""
Azure Startup Script for Laude Agent Enterprise
Initializes the application environment and database
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_application():
    """Initialize application for Azure deployment"""
    try:
        logger.info("Starting Laude Agent Enterprise initialization...")
        
        # Create required directories
        directories = [
            "otp_emails",
            "logs", 
            "emails",
            "reports",
            "transcripts",
            "audio_clips",
            "static",
            "templates"
        ]
        
        for directory in directories:
            dir_path = Path(directory)
            dir_path.mkdir(exist_ok=True)
            logger.info(f"Created directory: {directory}")
        
        # Initialize authentication system
        from auth_system import EnterpriseAuth
        auth = EnterpriseAuth()
        logger.info("Authentication system initialized")
        
        # Log system configuration
        logger.info(f"Allowed domains: {', '.join(auth.ALLOWED_DOMAINS)}")
        logger.info(f"Database path: {auth.db_path}")
        
        # Get initial stats
        stats = auth.get_user_stats()
        logger.info(f"System stats: {stats}")
        
        logger.info("✅ Laude Agent Enterprise initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Initialization failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = initialize_application()
    if not success:
        sys.exit(1)
    
    # Start the application
    from app import app
    
    # Get port from Azure environment
    port = int(os.environ.get('WEBSITES_PORT', os.environ.get('PORT', 8000)))
    
    logger.info(f"Starting application on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)