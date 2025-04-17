from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pyvirtualdisplay.display import Display
import os
import time
import re
import json
import random
import shutil
import tempfile
import subprocess
import base64
import logging
from datetime import datetime
from .indonesian_commands import IndonesianCommands

class WhatsAppBot:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.commands = {
            'expense': self.handle_expense,
            'income': self.handle_income,
            'balance': self.get_balance,
            'report': self.get_report,
            'help': self.show_help,
            'plan': self.get_financial_plan,
            'invest': self.get_investment_advice,
            'goal': self.handle_savings_goal,
            'budget': self.get_budget_advice,
            'market': self.get_market_info
        }
        self.indonesian = IndonesianCommands()
        self.temp_dir = None
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def start(self):
        """Initialize the WhatsApp Web driver"""
        # Clean up existing processes and create temp directory
        try:
            # Clean up any existing processes more thoroughly
            cleanup_commands = [
                'pkill -f chrome',
                'pkill -f chromedriver',
                'pkill -f Xvfb',
                'rm -rf /tmp/.X*-lock',
                'rm -rf /tmp/.X11-unix/X*'
            ]
            for cmd in cleanup_commands:
                try:
                    subprocess.run(cmd.split(), stderr=subprocess.DEVNULL)
                except:
                    pass
            time.sleep(2)

            # Create unique temporary directory
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            random_suffix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=6))
            self.temp_dir = tempfile.mkdtemp(prefix=f'chrome_data_{timestamp}_{random_suffix}_')
            os.chmod(self.temp_dir, 0o755)
            self.logger.info(f"Created temporary directory: {self.temp_dir}")

            # Initialize virtual display with simpler configuration
            self.display = Display(visible=0, size=(1920, 1080))
            self.display.start()
            time.sleep(2)  # Wait for display to initialize

            if not self.display.is_alive():
                raise Exception("Failed to start virtual display")

            # Set display environment variable
            os.environ["DISPLAY"] = f":{self.display.display}"
            self.logger.info(f"Virtual display started successfully on display :{self.display.display}")

        except Exception as e:
            self.logger.error(f"Error during initialization: {e}")
            self.cleanup()
            raise Exception(f"Initialization failed: {e}")

        # Try to find browser binary
        browser_paths = [
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable',
            '/usr/bin/chromium',
            '/usr/bin/chromium-browser'
        ]
        
        browser_found = None
        for path in browser_paths:
            if os.path.exists(path):
                browser_found = path
                self.logger.info(f"Found browser at: {path}")
                break
                
        if not browser_found:
            raise Exception("No compatible browser found. Please install Google Chrome or Chromium.")

        # Kill any existing Chrome processes
        try:
            subprocess.run(['pkill', '-f', '(chrome|chromedriver)'], shell=True, stderr=subprocess.DEVNULL)
            time.sleep(2)
        except Exception as e:
            self.logger.warning(f"Error cleaning up Chrome processes: {e}")

        # Verify display is ready
        if "DISPLAY" not in os.environ:
            raise Exception("Display environment variable not set")
        
        # Configure Chrome with debugging options
        options = Options()
        options.binary_location = browser_found

        # Basic configuration with additional options for WhatsApp Web
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--user-data-dir={self.temp_dir}')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-gpu')
        options.add_argument('--headless=new')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument(f'--display={os.environ["DISPLAY"]}')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Add remote debugging port
        debug_port = random.randint(9222, 9999)
        options.add_argument(f'--remote-debugging-port={debug_port}')
        self.logger.info(f"Using debug port {debug_port}")
        
        # Additional settings
        options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('prefs', {
            'profile.default_content_setting_values.notifications': 2,
            'profile.default_content_settings.popups': 0,
            'download.prompt_for_download': False,
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False
        })

        # Wait for display to be ready
        time.sleep(2)
        
        # Set up Chrome driver service
        try:
            # Use chromedriver from the extracted archive
            chromedriver_path = os.path.join(os.getcwd(), 'chromedriver-linux64', 'chromedriver')
            if not os.path.exists(chromedriver_path):
                raise Exception(f"ChromeDriver not found at {chromedriver_path}")
            
            # Ensure chromedriver is executable
            os.chmod(chromedriver_path, 0o755)
            
            # Set up service with specific configuration
            service = Service(
                executable_path=chromedriver_path,
                log_path=os.path.join(self.temp_dir, 'chromedriver.log'),
                service_args=['--verbose']
            )
            
            # Initialize Chrome driver with error handling and retry
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:
                try:
                    self.driver = webdriver.Chrome(service=service, options=options)
                    self.logger.info("Chrome driver initialized successfully")
                    
                    # Set page load timeout and wait with increased timeouts
                    self.driver.set_page_load_timeout(60)
                    self.wait = WebDriverWait(self.driver, 30)
                    
                    # Test browser is working
                    self.driver.get('about:blank')
                    time.sleep(2)
                    self.logger.info("Chrome browser test page loaded successfully")
                    break  # Success, exit the retry loop
                    
                except Exception as e:
                    retry_count += 1
                    self.logger.warning(f"Chrome driver initialization attempt {retry_count} failed: {str(e)}")
                    if self.driver:
                        try:
                            self.driver.quit()
                        except:
                            pass
                    if retry_count >= max_retries:
                        raise Exception(f"Chrome driver initialization failed after {max_retries} attempts: {str(e)}")
                    time.sleep(2)  # Wait before retrying
            
            # Load WhatsApp Web with retry
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:
                try:
                    # Load WhatsApp Web with extended timeout
                    self.driver.set_page_load_timeout(120)
                    self.wait = WebDriverWait(self.driver, 60)
                    
                    # Navigate to WhatsApp Web
                    self.logger.info("Navigating to WhatsApp Web...")
                    self.driver.get("https://web.whatsapp.com")
                    time.sleep(5)  # Wait for initial page load
                    
                    # Wait for page to be ready
                    self.logger.info("Waiting for page to be ready...")
                    self.wait.until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # Wait for QR code with multiple selectors
                    self.logger.info("Waiting for QR code...")
                    qr_selectors = [
                        "canvas[aria-label='Scan me!']",
                        "canvas[data-testid='qrcode']",
                        "canvas.qr-code"
                    ]
                    
                    qr_canvas = None
                    for selector in qr_selectors:
                        try:
                            qr_canvas = self.wait.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                            self.logger.info(f"QR code found with selector: {selector}")
                            break
                        except:
                            continue
                    
                    if not qr_canvas:
                        raise Exception("Could not find QR code element with any known selector")
                    
                    # Get and save QR code image with error handling
                    try:
                        self.logger.info("Capturing QR code image...")
                        qr_base64 = self.driver.execute_script(
                            "return arguments[0].toDataURL('image/png').substring(21);", 
                            qr_canvas
                        )
                        
                        # Verify base64 data
                        if not qr_base64:
                            raise Exception("Failed to get QR code image data")
                        
                        # Save QR code image with error handling
                        qr_path = os.path.join(self.temp_dir, "qr_code.png")
                        try:
                            with open(qr_path, "wb") as f:
                                f.write(base64.b64decode(qr_base64))
                            
                            # Verify file was created
                            if not os.path.exists(qr_path) or os.path.getsize(qr_path) == 0:
                                raise Exception("QR code image file is empty or not created")
                                
                            self.logger.info(f"QR code saved successfully to: {qr_path}")
                            print(f"\nPlease scan the QR code saved at: {qr_path}\n")
                            
                        except Exception as save_error:
                            raise Exception(f"Failed to save QR code image: {str(save_error)}")
                            
                    except Exception as qr_error:
                        raise Exception(f"Failed to capture QR code: {str(qr_error)}")
                    
                    # Wait for login with multiple indicators
                    self.logger.info("Waiting for WhatsApp Web login...")
                    login_selectors = [
                        "div[data-testid='chat-list']",
                        "div._3YewW",  # Alternative chat list selector
                        "div[data-testid='default-user']"  # User profile indicator
                    ]
                    
                    login_success = False
                    for selector in login_selectors:
                        try:
                            self.wait.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                            self.logger.info(f"Login detected via selector: {selector}")
                            login_success = True
                            break
                        except:
                            continue
                    
                    if not login_success:
                        raise Exception("Could not detect successful login with any known indicator")
                    
                    # Additional verification
                    try:
                        self.logger.info("Verifying login state...")
                        self.driver.execute_script("return window.Store !== undefined")
                        self.logger.info("WhatsApp Web interface fully loaded")
                    except:
                        self.logger.warning("Could not verify WhatsApp Web interface state")
                    
                    self.logger.info("Successfully logged into WhatsApp Web")
                    break  # Success, exit the retry loop
                    
                except Exception as e:
                    retry_count += 1
                    error_msg = str(e)
                    
                    # Check for specific error conditions
                    if "net::ERR_CONNECTION_TIMED_OUT" in error_msg:
                        self.logger.warning(f"Connection timeout on attempt {retry_count}, retrying...")
                    elif "net::ERR_CONNECTION_REFUSED" in error_msg:
                        self.logger.warning(f"Connection refused on attempt {retry_count}, retrying...")
                    elif "no such element" in error_msg.lower():
                        self.logger.warning(f"Required element not found on attempt {retry_count}, retrying...")
                    elif "chrome not reachable" in error_msg.lower():
                        self.logger.warning(f"Chrome not reachable on attempt {retry_count}, restarting driver...")
                        if self.driver:
                            try:
                                self.driver.quit()
                            except:
                                pass
                    else:
                        self.logger.warning(f"WhatsApp Web loading attempt {retry_count} failed: {error_msg}")
                    
                    if retry_count >= max_retries:
                        raise Exception(f"WhatsApp Web loading failed after {max_retries} attempts. Last error: {error_msg}")
                    
                    # Progressive delay with jitter
                    delay = min(5 * retry_count + random.uniform(0, 2), 30)
                    self.logger.info(f"Waiting {delay:.1f} seconds before retry...")
                    time.sleep(delay)
            
        except Exception as e:
            error_msg = f"WhatsApp bot initialization failed: {str(e)}"
            self.logger.error(error_msg)
            
            # Ensure cleanup happens even if driver quit fails
            try:
                self.cleanup()
            except Exception as cleanup_error:
                self.logger.error(f"Additional error during cleanup: {str(cleanup_error)}")
            
            raise Exception(error_msg)
        

    def listen_for_messages(self):
        """Listen for incoming messages and process them"""
        retry_count = 0
        max_retries = 3
        retry_delay = 2
        max_consecutive_errors = 5
        consecutive_errors = 0

        while True:
            try:
                # Check if driver is alive
                if not self.is_driver_alive():
                    raise Exception("Chrome driver is not responsive")

                # Find unread messages with timeout and retry
                try:
                    self.logger.debug("Checking for unread messages...")
                    unread = self.wait.until(EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, 'span[aria-label="UNREAD"]')))
                    retry_count = 0  # Reset retry count on success
                    consecutive_errors = 0  # Reset error count on success
                except Exception as e:
                    retry_count += 1
                    consecutive_errors += 1
                    if retry_count >= max_retries:
                        self.logger.error(f"Failed to find unread messages after {max_retries} attempts: {str(e)}")
                        raise
                    if consecutive_errors >= max_consecutive_errors:
                        self.logger.error(f"Too many consecutive errors ({consecutive_errors}), restarting bot...")
                        raise Exception("Too many consecutive errors")
                    self.logger.warning(f"Retry {retry_count}/{max_retries} finding unread messages: {str(e)}")
                    time.sleep(retry_delay)
                    continue

                # Process each unread message
                for message in unread:
                    try:
                        # Click on the chat with retry
                        click_success = False
                        for attempt in range(3):
                            try:
                                message.click()
                                click_success = True
                                break
                            except Exception as click_error:
                                self.logger.warning(f"Click attempt {attempt + 1} failed: {str(click_error)}")
                                time.sleep(1)
                        
                        if not click_success:
                            raise Exception("Failed to click chat after multiple attempts")

                        # Wait for messages to load and verify
                        time.sleep(1)
                        messages = self.wait.until(EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, 'div.message-in')))
                        
                        if not messages:
                            self.logger.warning("No incoming messages found after clicking chat")
                            continue
                        
                        # Get and verify last message
                        last_message = messages[-1].text
                        if not last_message:
                            self.logger.warning("Last message text is empty")
                            continue
                        
                        # Process message with logging
                        self.logger.info(f"Processing message: {last_message[:50]}...")
                        self.process_message(last_message)
                        
                        # Ensure message is marked as read
                        time.sleep(1)
                        
                    except Exception as message_error:
                        self.logger.error(f"Error processing individual message: {str(message_error)}")
                        consecutive_errors += 1
                        if consecutive_errors >= max_consecutive_errors:
                            raise Exception("Too many consecutive message processing errors")
                        continue
                
            except Exception as e:
                error_msg = str(e)
                self.logger.error(f"Critical error in message listener: {error_msg}")
                
                # Handle different error scenarios
                if "chrome not reachable" in error_msg.lower() or "not responsive" in error_msg.lower():
                    self.logger.error("Chrome driver appears to be dead, attempting restart...")
                    self.cleanup()
                    try:
                        self.start()
                        self.logger.info("Successfully restarted WhatsApp bot")
                        retry_count = 0
                        consecutive_errors = 0
                        continue
                    except Exception as restart_error:
                        self.logger.error(f"Failed to restart WhatsApp bot: {str(restart_error)}")
                        raise
                
                # Progressive delay with jitter
                delay = min(retry_delay * (2 ** retry_count) + random.uniform(0, 2), 30)
                self.logger.info(f"Waiting {delay:.1f} seconds before retry...")
                time.sleep(delay)

    def is_driver_alive(self):
        """Check if the Chrome driver is still responsive"""
        try:
            self.driver.current_url
            return True
        except:
            return False

    def process_message(self, message):
        """Process incoming messages and execute commands"""
        try:
            self.logger.info(f"Processing message: {message}")
            # Try to translate Indonesian command to English
            command, params = self.indonesian.translate_command(message)
            
            if command and command in self.commands:
                self.logger.info(f"Executing command: {command} with params: {params}")
                response = self.commands[command](*params)
                self.send_message(response)
            else:
                self.logger.warning(f"Unknown command in message: {message}")
                self.send_message(self.indonesian.get_help_message())
                
        except Exception as e:
            self.logger.error(f"Error processing message '{message}': {str(e)}")
            self.send_message(self.indonesian.get_error_message())

    def send_message(self, message):
        """Send a message in the current chat"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Find and verify input box is interactive
                input_box = self.wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div[contenteditable="true"]')))
                input_box.clear()  # Clear any existing text
                input_box.send_keys(message)
                
                # Find and verify send button is clickable
                send_button = self.wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'button[aria-label="Send"]')))
                send_button.click()
                
                self.logger.info("Message sent successfully")
                time.sleep(1)
                return  # Success, exit the retry loop
                
            except Exception as e:
                retry_count += 1
                self.logger.warning(f"Send message attempt {retry_count} failed: {str(e)}")
                if retry_count >= max_retries:
                    self.logger.error(f"Failed to send message after {max_retries} attempts")
                    raise
                time.sleep(2)  # Wait before retrying

    def handle_expense(self, amount, category=None, *description):
        """Handle expense tracking command"""
        try:
            # Validate amount
            try:
                amount = float(amount)
                if amount <= 0:
                    raise ValueError("Amount must be positive")
            except ValueError as e:
                self.logger.error(f"Invalid expense amount '{amount}': {str(e)}")
                return self.indonesian.get_error_message()

            # Process category and description
            category = category or "Other"
            desc = " ".join(description) if description else ""
            
            self.logger.info(f"Processing expense: amount={amount}, category={category}, description={desc}")
            
            # Create transaction record
            transaction = {
                "type": "expense",
                "amount": amount,
                "category": category,
                "description": desc,
                "date": datetime.now().isoformat()
            }
            
            # Save transaction to database (implement database connection)
            self.logger.info(f"Expense transaction created: {transaction}")
            
            return self.indonesian.get_success_message('expense', amount, category, desc)
            
        except Exception as e:
            self.logger.error(f"Error handling expense: {str(e)}")
            return self.indonesian.get_error_message()

    def handle_income(self, amount, category=None, *description):
        """Handle income tracking command"""
        try:
            # Validate amount
            try:
                amount = float(amount)
                if amount <= 0:
                    raise ValueError("Amount must be positive")
            except ValueError as e:
                self.logger.error(f"Invalid income amount '{amount}': {str(e)}")
                return self.indonesian.get_error_message()

            # Process category and description
            category = category or "Other"
            desc = " ".join(description) if description else ""
            
            self.logger.info(f"Processing income: amount={amount}, category={category}, description={desc}")
            
            # Create transaction record
            transaction = {
                "type": "income",
                "amount": amount,
                "category": category,
                "description": desc,
                "date": datetime.now().isoformat()
            }
            
            # Save transaction to database (implement database connection)
            self.logger.info(f"Income transaction created: {transaction}")
            
            return self.indonesian.get_success_message('income', amount, category, desc)
            
        except Exception as e:
            self.logger.error(f"Error handling income: {str(e)}")
            return self.indonesian.get_error_message()

    def get_balance(self):
        """Get current balance"""
        try:
            self.logger.info("Fetching current balance")
            # Implement database query to get current balance
            balance = 0  # Replace with actual balance query
            self.logger.info(f"Current balance: {balance}")
            return self.indonesian.get_balance_message(balance)
        except Exception as e:
            self.logger.error(f"Error fetching balance: {str(e)}")
            return self.indonesian.get_error_message()

    def get_report(self):
        """Generate financial report"""
        try:
            self.logger.info("Generating financial report")
            # TODO: Implement report generation logic
            # For now, return placeholder message
            report_message = "📊 Financial Report:\n[Report details will be implemented]"
            self.logger.info("Financial report generated successfully")
            return report_message
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            return self.indonesian.get_error_message()

    def show_help(self):
        """Show help message with available commands"""
        try:
            self.logger.info("Generating help message")
            help_message = self.indonesian.get_help_message()
            self.logger.info("Help message generated successfully")
            return help_message
        except Exception as e:
            self.logger.error(f"Error generating help message: {str(e)}")
            return "Error: Could not generate help message"

    def get_financial_plan(self, *args):
        """Get personalized financial planning advice"""
        try:
            self.logger.info("Generating financial plan")
            from src.bot.financial_processor import FinancialProcessor
            processor = FinancialProcessor()
            advice = processor.get_financial_advice(1)  # Using default user_id for now
            self.logger.info("Financial plan generated successfully")
            return advice
        except Exception as e:
            self.logger.error(f"Error generating financial plan: {str(e)}")
            return "Maaf, terjadi kesalahan dalam membuat rencana keuangan. Silakan coba lagi nanti."

    def get_investment_advice(self, *args):
        """Get investment recommendations"""
        try:
            self.logger.info("Generating investment advice")
            advice = [
                "💡 *Rekomendasi Investasi*:\n",
                "1. *Diversifikasi Portfolio*:",
                "   • Saham: 40%",
                "   • Reksadana: 30%",
                "   • Obligasi: 20%",
                "   • Emas: 10%",
                "\n2. *Tips Investasi*:",
                "   • Mulai dengan modal kecil",
                "   • Lakukan riset mendalam",
                "   • Investasi rutin (Dollar Cost Averaging)",
                "   • Perhatikan profil risiko",
                "\n3. *Langkah Memulai*:",
                "   • Buka rekening efek",
                "   • Pelajari analisis dasar",
                "   • Ikuti perkembangan pasar",
                "   • Konsultasi dengan ahli keuangan"
            ]
            return "\n".join(advice)
        except Exception as e:
            self.logger.error(f"Error generating investment advice: {str(e)}")
            return "Maaf, terjadi kesalahan dalam memberikan saran investasi. Silakan coba lagi nanti."

    def handle_savings_goal(self, amount=None, name=None, duration=None, *args):
        """Handle savings goal setting"""
        try:
            self.logger.info(f"Processing savings goal: amount={amount}, name={name}, duration={duration}")
            
            if not amount:
                return ("Untuk membuat target tabungan, gunakan format:\n"
                       "target <jumlah> [nama_target] [tenggat]\n"
                       "Contoh: target 10000000 liburan 6bulan")
            
            try:
                target_amount = float(amount)
                if target_amount <= 0:
                    raise ValueError("Amount must be positive")
            except ValueError:
                return "Jumlah target harus berupa angka positif."
            
            goal_name = name if name else "Target Tabungan"
            goal_duration = duration if duration else "tidak ditentukan"
            
            from src.bot.financial_processor import FinancialProcessor
            processor = FinancialProcessor()
            
            # Add the savings goal
            if processor.add_savings_goal(1, goal_name, target_amount, goal_duration):
                monthly_needed = target_amount / 6  # Assume 6 months if no duration specified
                
                response = [
                    f"✅ Target tabungan berhasil dibuat!",
                    f"\n📊 *Detail Target*:",
                    f"• Nama: {goal_name}",
                    f"• Target: {self.indonesian.format_currency(target_amount)}",
                    f"• Tenggat: {goal_duration}",
                    f"• Rekomendasi tabungan per bulan: {self.indonesian.format_currency(monthly_needed)}",
                    "\n💡 Tips mencapai target:",
                    "• Atur pengeluaran bulanan",
                    "• Sisihkan uang di awal bulan",
                    "• Pantau progres secara rutin"
                ]
                return "\n".join(response)
            else:
                return "Maaf, terjadi kesalahan dalam membuat target tabungan."
            
        except Exception as e:
            self.logger.error(f"Error handling savings goal: {str(e)}")
            return "Maaf, terjadi kesalahan dalam memproses target tabungan. Silakan coba lagi nanti."

    def get_budget_advice(self, *args):
        """Get budgeting recommendations"""
        try:
            self.logger.info("Generating budget advice")
            from src.bot.financial_processor import FinancialProcessor
            processor = FinancialProcessor()
            monthly_summary = processor.get_monthly_summary(1)  # Using default user_id
            
            income = monthly_summary['monthly_income']
            if income == 0:
                return ("Belum ada data pemasukan. Silakan catat pemasukan Anda terlebih dahulu "
                       "dengan perintah 'pemasukan <jumlah> [kategori] [keterangan]'")
            
            # Calculate recommended budget allocations
            budget = [
                "📊 *Rekomendasi Alokasi Budget Bulanan*:\n",
                f"Pendapatan: {self.indonesian.format_currency(income)}\n",
                "*Alokasi yang disarankan:*",
                f"• Kebutuhan Pokok (50%): {self.indonesian.format_currency(income * 0.5)}",
                "  - Tempat tinggal: 30%",
                "  - Makan: 10%",
                "  - Transportasi: 10%",
                f"\n• Tabungan & Investasi (30%): {self.indonesian.format_currency(income * 0.3)}",
                "  - Dana darurat: 10%",
                "  - Investasi: 15%",
                "  - Target khusus: 5%",
                f"\n• Gaya Hidup (20%): {self.indonesian.format_currency(income * 0.2)}",
                "  - Hiburan",
                "  - Belanja",
                "  - Hobi",
                "\n💡 *Tips Mengatur Budget*:",
                "• Catat semua pengeluaran",
                "• Prioritaskan kebutuhan pokok",
                "• Siapkan dana darurat",
                "• Evaluasi budget secara rutin"
            ]
            return "\n".join(budget)
        except Exception as e:
            self.logger.error(f"Error generating budget advice: {str(e)}")
            return "Maaf, terjadi kesalahan dalam memberikan saran budget. Silakan coba lagi nanti."

    def get_market_info(self, *args):
        """Get current market information"""
        try:
            self.logger.info("Fetching market information")
            import requests
            from src.utils.config import Config
            
            market_info = ["📈 *Informasi Pasar Terkini*:\n"]
            
            # Get IHSG data
            try:
                alpha_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=^JKSE&apikey={Config.ALPHA_VANTAGE_API_KEY}"
                market_response = requests.get(alpha_url)
                market_data = market_response.json()
                if 'Global Quote' in market_data:
                    quote = market_data['Global Quote']
                    price = float(quote.get('05. price', 0))
                    change = quote.get('10. change percent', '0%')
                    market_info.append(f"*IHSG*:")
                    market_info.append(f"• Harga: {price:,.2f}")
                    market_info.append(f"• Perubahan: {change}")
            except Exception as e:
                self.logger.error(f"Error fetching IHSG data: {str(e)}")
                market_info.append("*IHSG*: Data tidak tersedia")
            
            # Get exchange rates
            try:
                exchange_url = f"https://v6.exchangerate-api.com/v6/{Config.EXCHANGE_RATE_API_KEY}/latest/IDR"
                exchange_response = requests.get(exchange_url)
                exchange_data = exchange_response.json()
                if 'conversion_rates' in exchange_data:
                    rates = exchange_data['conversion_rates']
                    market_info.append("\n*Kurs Mata Uang*:")
                    market_info.append(f"• USD/IDR: Rp {(1/rates['USD']):,.2f}")
                    market_info.append(f"• EUR/IDR: Rp {(1/rates['EUR']):,.2f}")
                    market_info.append(f"• SGD/IDR: Rp {(1/rates['SGD']):,.2f}")
            except Exception as e:
                self.logger.error(f"Error fetching exchange rates: {str(e)}")
                market_info.append("\n*Kurs Mata Uang*: Data tidak tersedia")
            
            market_info.append("\n💡 *Tips Trading*:")
            market_info.append("• Perhatikan kondisi fundamental")
            market_info.append("• Analisis tren pasar")
            market_info.append("• Kelola risiko dengan baik")
            market_info.append("• Diversifikasi portfolio")
            
            return "\n".join(market_info)
        except Exception as e:
            self.logger.error(f"Error getting market info: {str(e)}")
            return "Maaf, terjadi kesalahan dalam mengambil informasi pasar. Silakan coba lagi nanti."

    def cleanup(self):
        """Clean up resources"""
        # Clean up Chrome driver
        if self.driver:
            try:
                self.driver.close()
                self.driver.quit()
                self.logger.info("Chrome driver closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing Chrome driver: {e}")
            finally:
                self.driver = None

        # Clean up virtual display
        if hasattr(self, 'display') and self.display:
            try:
                self.display.stop()
                self.logger.info("Virtual display stopped")
            except Exception as e:
                self.logger.error(f"Error stopping virtual display: {e}")
            finally:
                self.display = None

        # Clean up temporary directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                self.logger.info(f"Temporary directory {self.temp_dir} removed")
            except Exception as e:
                self.logger.error(f"Error cleaning up temporary directory: {e}")
            finally:
                self.temp_dir = None

        # Kill any remaining processes
        try:
            subprocess.run(['pkill', '-f', '(chrome|chromedriver|Xvfb)'], 
                         shell=True, stderr=subprocess.DEVNULL)
        except Exception as e:
            self.logger.warning(f"Error during final process cleanup: {e}")

if __name__ == "__main__":
    bot = WhatsAppBot()
    try:
        bot.start()
        bot.listen_for_messages()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        bot.cleanup()
