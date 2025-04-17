# WhatsApp Financial Planner Bot

A financial planning assistant that combines a WhatsApp chatbot with a web dashboard for managing personal finances in Indonesia.

## Features

- 💬 WhatsApp Integration
  - Track expenses and income through chat
  - Get instant financial reports
  - Receive AI-powered financial advice
  - Full support for Indonesian language
  - Real-time market data integration

- 📊 Web Dashboard
  - Real-time financial overview
  - Expense tracking and categorization
  - Income monitoring
  - Savings goals tracking
  - Visual reports and charts
  - Market trends visualization

- 🤖 AI Financial Planning
  - Personalized financial advice
  - Investment recommendations
  - Risk assessment
  - Market analysis
  - Budget optimization
  - Savings goal planning

- 💰 Financial Management
  - Smart expense categorization
  - Income tracking and analysis
  - Automated savings goals
  - Dynamic budget planning
  - Real-time IHSG monitoring
  - Currency exchange tracking

## Prerequisites

- Python 3.8 or higher
- Chrome browser (for WhatsApp Web automation)
- SQLite3

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/whatsapp-financial-planner.git
cd whatsapp-financial-planner
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install system dependencies:
```bash
# For Debian/Ubuntu
sudo apt-get update
sudo apt-get install -y xvfb google-chrome-stable

# For RHEL/CentOS
sudo yum update
sudo yum install -y xorg-x11-server-Xvfb google-chrome-stable
```

5. Set up ChromeDriver:
```bash
# Extract included ChromeDriver
unzip chromedriver-linux64.zip
chmod +x chromedriver-linux64/chromedriver
```

6. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration:
DEBUG=True
LOG_LEVEL=INFO  # Set to DEBUG for more detailed logs
ALPHA_VANTAGE_API_KEY=your_key_here  # For stock market data
EXCHANGE_RATE_API_KEY=your_key_here  # For currency exchange rates
OPENAI_API_KEY=your_key_here  # For AI financial advice (optional)
WHATSAPP_ENABLED=true
```

Note: Get your API keys from:
- Alpha Vantage: https://www.alphavantage.co/
- Exchange Rate API: https://www.exchangerate-api.com/

7. Verify system setup:
```bash
# Check Chrome installation
google-chrome --version

# Check Xvfb
Xvfb -version

# Verify Python dependencies
python -c "from selenium import webdriver; from pyvirtualdisplay import Display"
```

## Usage

1. Start the application:
```bash
python main.py
```

2. Access the web dashboard:
```
http://localhost:8000
```

3. Scan the WhatsApp QR code when prompted to connect the bot.

## WhatsApp Commands

### Basic Commands
- Track expense:
```
pengeluaran 50000 makan siang
bayar 50000 makan
```

- Record income:
```
pemasukan 1000000 gaji bulanan
masuk 1000000 gaji
```

- Check balance:
```
saldo
ceksaldo
```

- Get financial report:
```
laporan
rekap
```

### AI Financial Planning Commands
- Get financial advice:
```
rencana
konsultasi
saran
```

- Investment guidance:
```
investasi
saham
reksadana
```

- Set savings goal:
```
target 10000000 liburan 6bulan
nabung 5000000 pendidikan
```

- Budget planning:
```
budget
anggaran
```

- Market information:
```
pasar
ihsg
kurs
```

- Show help:
```
bantuan
tolong
```

## Project Structure

```
financial-whatsapp-bot/
├── src/
│   ├── bot/
│   │   ├── whatsapp_handler.py
│   │   └── financial_processor.py
│   ├── dashboard/
│   │   ├── app.py
│   │   └── templates/
│   └── utils/
│       └── config.py
├── main.py
├── requirements.txt
└── README.md
```

## Development

- Run tests:
```bash
pytest
```

- Format code:
```bash
black .
```

- Lint code:
```bash
flake8
```

## Troubleshooting

### Common Issues and Solutions

1. ChromeDriver Issues:
   - Error: "ChromeDriver not found"
     ```bash
     # Verify ChromeDriver exists and is executable
     ls -l chromedriver-linux64/chromedriver
     chmod +x chromedriver-linux64/chromedriver
     ```
   - Error: "Chrome not reachable"
     ```bash
     # Kill existing Chrome processes
     pkill -f chrome
     # Restart the application
     python main.py
     ```

2. Display Issues:
   - Error: "Display not found"
     ```bash
     # Check Xvfb is running
     ps aux | grep Xvfb
     # Start Xvfb manually if needed
     Xvfb :99 -screen 0 1920x1080x24 &
     export DISPLAY=:99
     ```

3. WhatsApp Web Connection:
   - Error: "Failed to load WhatsApp Web"
     - Check internet connection
     - Verify WhatsApp Web is accessible
     - Try increasing timeout in .env: `WHATSAPP_TIMEOUT=120`
   - QR Code Issues:
     - Ensure temp directory has write permissions
     - Try scanning QR code with WhatsApp beta app

4. Message Processing:
   - Error: "Failed to process message"
     - Check log files for specific error
     - Verify message format matches commands
     - Try with DEBUG=True for more details

### Error Recovery Features

The bot includes several automatic recovery mechanisms:

1. Auto-Retry System:
   - Automatic retry for failed operations
   - Progressive delay between retries
   - Maximum retry limits to prevent infinite loops

2. Connection Recovery:
   - Automatic restart on connection loss
   - Session recovery after crashes
   - Graceful cleanup of resources

3. Error Logging:
   - Detailed error logs in DEBUG mode
   - Stack traces for debugging
   - Operation status logging

### Monitoring

Monitor the bot's health through:

1. Log Files:
   ```bash
   tail -f bot.log  # If logging to file enabled
   ```

2. Process Status:
   ```bash
   ps aux | grep python  # Check bot process
   ps aux | grep chrome  # Check browser processes
   ```

## Security Notes

- The application uses SQLite for data storage
- WhatsApp session data is stored in temporary directories
- Automatic cleanup of sensitive data
- Secure error handling to prevent data leaks
- Use strong passwords and secure environment variables

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Flask and Tailwind CSS
- Uses Selenium for WhatsApp Web automation
- Chart.js for data visualization
