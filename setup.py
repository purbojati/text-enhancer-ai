from setuptools import setup

APP = ['fix_ai.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'app.iconset/FixAI.icns',
    'plist': {
        'CFBundleName': 'Fix AI',
        'CFBundleDisplayName': 'Fix AI',
        'CFBundleIdentifier': 'com.fixai.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSUIElement': True,
        'NSAppleEventsUsageDescription': 'This app requires access to automate keyboard input for text enhancement.',
        'NSHighResolutionCapable': True,
    },
    'packages': [
        'rumps',
        'openai',
        'pyperclip',
        'certifi',
        'charset_normalizer',
        'urllib3',
        'requests'
    ],
    'includes': [
        'packaging',
        'packaging.version',
        'packaging.specifiers',
        'packaging.requirements',
        'json',
        'os',
        'sys'
    ],
    'excludes': ['tkinter', 'PyQt5', 'wx', 'PySide2'],
}

setup(
    app=APP,
    name='Fix AI',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'rumps',
        'openai',
        'pyperclip',
        'requests'
    ],
)
