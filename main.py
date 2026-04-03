#!/usr/bin/env python3
"""AI-enhanced SSH Client"""

import asyncio
from ai_ssh_client.ui.app import AISSHApp

def main():
    """Start the AI SSH Client application"""
    app = AISSHApp()
    app.run()

if __name__ == "__main__":
    main()
