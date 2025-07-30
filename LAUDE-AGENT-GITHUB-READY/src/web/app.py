#!/usr/bin/env python3
"""
Azure App Service Entry Point for Laude Agent Enterprise
Main application file for Azure deployment
"""

import os
import sys
from pathlib import Path

# Ensure current directory is in path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from azure_deployment import create_app

# Create the Flask application
app = create_app()

# This is the entry point that Azure App Service will use
if __name__ == '__main__':
    # For local development
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)