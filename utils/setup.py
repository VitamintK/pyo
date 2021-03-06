"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""
from setuptools import setup

APP = ['E-Pyo.py']
APP_NAME = 'E-Pyo'
DATA_FILES = ['Resources/']
OPTIONS = {'argv_emulation': False,
           'iconfile': 'E-PyoIcon.icns',
           'plist': {
               'CFBundleDisplayName': 'E-Pyo',
               'CFBundleExecutable': 'E-Pyo',
               'CFBundleIconFile': 'E-PyoIcon.icns',
               'CFBundleIdentifier': 'com.ajaxsoundstudio.E-Pyo',
               'CFBundleInfoDictionaryVersion': '0.8.6',
               'CFBundleName': 'E-Pyo',
               'CFBundlePackageType': 'APPL',
               'CFBundleShortVersionString': '0.8.6',
               'CFBundleVersion': '0.8.6',
               'CFBundleDocumentTypes': [{'CFBundleTypeOSTypes': ['TEXT'],
                                          'CFBundleTypeExtensions': ['py'],
                                          'CFBundleTypeRole': 'Editor',
                                          'CFBundleTypeIconFile': 'E-PyoIconDoc.icns',
                                          'LSIsAppleDefaultForType': False}]
           }
       }

setup(
    name=APP_NAME,
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
