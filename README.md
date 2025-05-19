# 🤖 Kalki - Your Local AI Assistant

Kalki is a powerful, locally-hosted AI assistant that can control your computer through natural language commands. It uses Jan.ai for language processing and combines screen understanding with automation capabilities.

## 🌟 Features

- 🧠 Natural Language Understanding using Jan.ai
- 👁️ Screen Vision and OCR
- 🖱️ Mouse and Keyboard Automation
- 🔒 Safe Mode and Action Confirmation
- 📝 Command History and Logging

## 🛠️ Requirements

- Python 3.9+
- Jan.ai (with API enabled)
- Tesseract OCR
- X11 or Wayland (Linux)

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/kalki.git
cd kalki
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install system dependencies:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr
# Arch Linux
sudo pacman -S tesseract
# macOS
brew install tesseract
```

5. Install and configure Jan.ai:
- Download from [jan.ai](https://jan.ai)
- Enable API in Settings
- Start the Jan.ai server

## 🚀 Usage

1. Start Kalki:
```bash
python main.py
```

2. Optional arguments:
- `--jan-url`: Jan.ai API URL (default: http://localhost:8080)
- `--safe-mode`: Enable safe mode (default: True)
- `--auto-confirm`: Skip command confirmations

3. Example commands:
```
"Open Firefox"
"Click the login button"
"Type Hello World"
```

## 🏗️ Project Structure

```
kalki/
├── modules/
│   ├── vision.py      # Screen capture and OCR
│   ├── actions.py     # System automation
│   ├── commands.py    # Command processing
│   └── jan_client.py  # Jan.ai integration
├── logs/
│   └── kalki.log      # Application logs
└── main.py            # Main entry point
```

## 🔒 Security

- Safe mode prevents potentially dangerous actions
- Command confirmation for sensitive operations
- Local-only operation (no cloud dependencies)
- Sandboxed execution environment

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Jan.ai](https://jan.ai) for local LLM capabilities
- [PyAutoGUI](https://pyautogui.readthedocs.io/) for automation
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for text recognition # bujji
