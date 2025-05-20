from setuptools import setup, find_packages

setup(
    name="kalki",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyYAML>=6.0.1",
        "pynput>=1.7.6",
        "pyautogui>=0.9.54",
        "Pillow>=10.0.0",
        "PyQt5>=5.15.9",
        "pystray>=0.19.4",
        "requests>=2.31.0",
        "websockets>=11.0.3",
        "SpeechRecognition>=3.10.0",
        "pyttsx3>=2.90",
    ],
    entry_points={
        "console_scripts": [
            "kalki=kalki.main:main",
        ],
    },
) 