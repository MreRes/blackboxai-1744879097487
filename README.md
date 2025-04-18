# Financial Dashboard with WhatsApp Bot

A comprehensive financial management system combining a web dashboard and WhatsApp bot for tracking personal finances in Indonesia.

## Features

### 📊 Web Dashboard
- Real-time financial overview
- Expense tracking and categorization
- Income monitoring
- Savings goals tracking
- Visual reports and charts

### 💬 WhatsApp Bot
- Track expenses and income through chat
- Get instant financial reports
- Receive AI-powered financial advice
- Full support for Indonesian language
- Real-time market data integration

## Prerequisites

- Python 3.8 or higher
- Google Chrome browser
- SQLite3

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a virtual environment:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements_fixed.txt
```

4. Set up Chrome and ChromeDriver:

### For Windows:
1. Install Google Chrome if not already installed
   - Download from: https://www.google.com/chrome/

2. Download ChromeDriver for Windows:
   - Visit: https://chromedriver.chromium.org/downloads
   - Download the version matching your Chrome browser
   - Extract the zip file
   - Place chromedriver.exe in the project root directory

### For Linux:
```bash
# For Debian/Ubuntu
sudo apt-get update
sudo apt-get install -y xvfb google-chrome-stable

# For RHEL/CentOS
sudo yum update
sudo yum install -y xorg-x11-server-Xvfb google-chrome-stable

# Extract included ChromeDriver
unzip chromedriver-linux64.zip
chmod +x chromedriver-linux64/chromedriver
```

## Running the Applications

### Web Dashboard

1. Start the Flask server:
```bash
# On Windows PowerShell
$env:PYTHONPATH="."; $env:FLASK_APP="new_app.py"; $env:FLASK_DEBUG=1; python new_app.py

# On Windows CMD
set PYTHONPATH=. && set FLASK_APP=new_app.py && set FLASK_DEBUG=1 && python new_app.py

# On Linux/Mac
PYTHONPATH=. FLASK_APP=new_app.py FLASK_DEBUG=1 python new_app.py
```

2. Access the dashboard at:
```
http://localhost:8000/dashboard
```

### WhatsApp Bot

1. Start the bot:
```bash
python main.py
```

2. Scan the QR code when prompted to connect WhatsApp.

## WhatsApp Commands

### Basic Commands
```
# Record expense
pengeluaran 50000 makan siang
bayar 50000 makan

# Record income
pemasukan 1000000 gaji bulanan
masuk 1000000 gaji

# Check balance
saldo
ceksaldo

# Get report
laporan
rekap
```

### Financial Planning Commands
```
# Get financial advice
rencana
konsultasi
saran

# Investment guidance
investasi
saham
reksadana

# Set savings goal
target 10000000 liburan 6bulan
nabung 5000000 pendidikan

# Budget planning
budget
anggaran

# Market information
pasar
ihsg
kurs
```

## Troubleshooting

### Common Issues on Windows

1. ChromeDriver Issues:
   - Error: "ChromeDriver not found"
     - Make sure chromedriver.exe is in the project root directory
     - Verify ChromeDriver version matches your Chrome browser version
   
   - Error: "Chrome not reachable"
     - Close all Chrome instances from Task Manager
     - Restart the bot application

2. WhatsApp Web Connection:
   - Error: "Failed to load WhatsApp Web"
     - Check internet connection
     - Clear Chrome browser cache
     - Try increasing timeout in config.py: `WHATSAPP_TIMEOUT=120`

3. QR Code Issues:
   - Make sure temp directory has write permissions
   - Try scanning QR code with latest WhatsApp version

## Project Structure
```
financial-system/
├── src/
│   ├── bot/
│   │   ├── whatsapp_handler.py
│   │   ├── financial_processor.py
│   │   └── indonesian_commands.py
│   ├── dashboard/
│   │   ├── app.py
│   │   └── templates/
│   └── utils/
│       └── config.py
├── new_app.py
├── main.py
└── requirements_fixed.txt
```

## Technology Stack

- Backend: Flask 2.0.1
- Database: SQLite with SQLAlchemy
- Frontend: Tailwind CSS
- WhatsApp Integration: Selenium
- Charts: Modern JavaScript libraries
- Icons: Font Awesome

## Dependencies

Core dependencies are locked to these versions for stability:
- Flask==2.0.1
- Werkzeug==2.0.1
- Flask-SQLAlchemy==2.5.1
- SQLAlchemy==1.4.23
- python-dotenv==0.19.0

## Notes

- The web dashboard runs on port 8000
- Sample data is automatically loaded for demonstration
- WhatsApp bot requires Chrome browser
- Tailwind CSS is included via CDN for simplicity

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Flask and Tailwind CSS
- Uses Selenium for WhatsApp Web automation
- Chart.js for data visualization
