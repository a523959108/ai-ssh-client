"""
Setup for py2app to build DMG
"""
from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'app_icon.icns',  # If you have an icon
    'plist': {
        'CFBundleName': 'AI SSH Client',
        'CFBundleDisplayName': 'AI SSH Client',
        'CFBundleGetInfoString': 'AI-enhanced SSH Client with natural language support',
        'CFBundleIdentifier': 'com.ai-ssh-client.app',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
        'NSHumanReadableCopyright': 'Copyright © 2026',
    }
}

setup(
    name='AI SSH Client',
    version='0.1.0',
    description='AI-enhanced SSH Client with natural language support',
    author='',
    url='',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app']
)
