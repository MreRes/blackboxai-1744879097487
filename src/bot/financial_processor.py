from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import sqlite3
import os

class FinancialProcessor:
    def __init__(self, db_path: str = 'financial.db'):
        self.db_path = db_path
        self.setup_database()

    def setup_database(self):
        """Initialize the SQLite database and create necessary tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                description TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Create savings goals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS savings_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                target_amount REAL NOT NULL,
                current_amount REAL DEFAULT 0,
                deadline DATE,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()
        conn.close()

    def add_transaction(self, user_id: int, amount: float, category: str, 
                       transaction_type: str, description: Optional[str] = None) -> bool:
        """Add a new transaction to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO transactions (user_id, amount, category, transaction_type, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, amount, category, transaction_type, description))
            
            conn.commit()
            
            # Update savings goals if it's an income transaction
            if transaction_type == 'income':
                self._process_savings_allocation(user_id, amount)
                
            return True
        except Exception as e:
            print(f"Error adding transaction: {str(e)}")
            return False
        finally:
            conn.close()

    def get_balance(self, user_id: int) -> float:
        """Calculate current balance for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get sum of income
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) FROM transactions 
                WHERE user_id = ? AND transaction_type = 'income'
            ''', (user_id,))
            total_income = cursor.fetchone()[0]
            
            # Get sum of expenses
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) FROM transactions 
                WHERE user_id = ? AND transaction_type = 'expense'
            ''', (user_id,))
            total_expenses = cursor.fetchone()[0]
            
            return total_income - total_expenses
        finally:
            conn.close()

    def get_monthly_summary(self, user_id: int, month: Optional[int] = None, 
                          year: Optional[int] = None) -> Dict:
        """Get monthly financial summary"""
        if month is None:
            month = datetime.now().month
        if year is None:
            year = datetime.now().year

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get monthly income
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) FROM transactions 
                WHERE user_id = ? 
                AND transaction_type = 'income'
                AND strftime('%m', date) = ?
                AND strftime('%Y', date) = ?
            ''', (user_id, f"{month:02d}", str(year)))
            monthly_income = cursor.fetchone()[0]
            
            # Get monthly expenses
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) FROM transactions 
                WHERE user_id = ? 
                AND transaction_type = 'expense'
                AND strftime('%m', date) = ?
                AND strftime('%Y', date) = ?
            ''', (user_id, f"{month:02d}", str(year)))
            monthly_expenses = cursor.fetchone()[0]
            
            # Get expense breakdown by category
            cursor.execute('''
                SELECT category, SUM(amount) FROM transactions 
                WHERE user_id = ? 
                AND transaction_type = 'expense'
                AND strftime('%m', date) = ?
                AND strftime('%Y', date) = ?
                GROUP BY category
            ''', (user_id, f"{month:02d}", str(year)))
            expense_categories = dict(cursor.fetchall())
            
            return {
                'monthly_income': monthly_income,
                'monthly_expenses': monthly_expenses,
                'savings': monthly_income - monthly_expenses,
                'expense_categories': expense_categories
            }
        finally:
            conn.close()

    def get_savings_goals(self, user_id: int) -> List[Dict]:
        """Get all savings goals for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, target_amount, current_amount, deadline 
                FROM savings_goals 
                WHERE user_id = ?
            ''', (user_id,))
            
            goals = []
            for row in cursor.fetchall():
                goals.append({
                    'id': row[0],
                    'name': row[1],
                    'target_amount': row[2],
                    'current_amount': row[3],
                    'deadline': row[4],
                    'progress': (row[3] / row[2]) * 100 if row[2] > 0 else 0
                })
            
            return goals
        finally:
            conn.close()

    def add_savings_goal(self, user_id: int, name: str, target_amount: float, 
                        deadline: Optional[str] = None) -> bool:
        """Add a new savings goal"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO savings_goals (user_id, name, target_amount, deadline)
                VALUES (?, ?, ?, ?)
            ''', (user_id, name, target_amount, deadline))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding savings goal: {str(e)}")
            return False
        finally:
            conn.close()

    def _process_savings_allocation(self, user_id: int, income_amount: float):
        """Automatically allocate a portion of income to savings goals"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all active savings goals
            cursor.execute('''
                SELECT id, target_amount, current_amount 
                FROM savings_goals 
                WHERE user_id = ? 
                AND current_amount < target_amount
            ''', (user_id,))
            
            goals = cursor.fetchall()
            if not goals:
                return
            
            # Allocate 20% of income among savings goals
            savings_amount = income_amount * 0.2
            allocation_per_goal = savings_amount / len(goals)
            
            for goal_id, target, current in goals:
                # Calculate how much can be added without exceeding target
                remaining = target - current
                to_add = min(allocation_per_goal, remaining)
                
                cursor.execute('''
                    UPDATE savings_goals 
                    SET current_amount = current_amount + ?
                    WHERE id = ?
                ''', (to_add, goal_id))
            
            conn.commit()
        finally:
            conn.close()

    def get_financial_advice(self, user_id: int) -> str:
        """Generate personalized financial advice using AI based on spending patterns"""
        try:
            import requests
            from src.utils.config import Config
            
            # Get user's financial data
            monthly_summary = self.get_monthly_summary(user_id)
            balance = self.get_balance(user_id)
            savings_goals = self.get_savings_goals(user_id)
            
            # Calculate key financial metrics
            monthly_income = monthly_summary['monthly_income']
            monthly_expenses = monthly_summary['monthly_expenses']
            savings_rate = (monthly_summary['savings'] / monthly_income * 100) if monthly_income > 0 else 0
            expense_categories = monthly_summary['expense_categories']
            
            # Get current exchange rates
            try:
                exchange_url = f"https://v6.exchangerate-api.com/v6/{Config.EXCHANGE_RATE_API_KEY}/latest/IDR"
                exchange_response = requests.get(exchange_url)
                exchange_data = exchange_response.json()
                usd_rate = exchange_data['conversion_rates']['USD']
            except:
                usd_rate = None
            
            # Get market data from Alpha Vantage
            try:
                alpha_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=^JKSE&apikey={Config.ALPHA_VANTAGE_API_KEY}"
                market_response = requests.get(alpha_url)
                market_data = market_response.json()
                market_change = market_data.get('Global Quote', {}).get('10. change percent', 'N/A')
            except:
                market_change = None
            
            # Prepare context for AI advice
            context = {
                "monthly_income": monthly_income,
                "monthly_expenses": monthly_expenses,
                "savings_rate": savings_rate,
                "balance": balance,
                "expense_categories": expense_categories,
                "savings_goals": [
                    {
                        "name": goal["name"],
                        "progress": goal["progress"],
                        "target": goal["target_amount"]
                    } for goal in savings_goals
                ],
                "market_conditions": {
                    "idr_to_usd": usd_rate,
                    "idx_change": market_change
                }
            }
            
            # Generate advice using pattern matching first
            advice = []
            
            # Emergency fund check
            months_of_expenses = balance / monthly_expenses if monthly_expenses > 0 else 0
            if months_of_expenses < Config.MIN_EMERGENCY_FUND:
                advice.append(f"⚠️ Dana darurat Anda hanya cukup untuk {months_of_expenses:.1f} bulan. "
                            f"Sebaiknya memiliki dana darurat untuk {Config.MIN_EMERGENCY_FUND} bulan pengeluaran.")
            
            # Expense ratio check
            if monthly_expenses > monthly_income * 0.8:
                advice.append("⚠️ Pengeluaran Anda tinggi dibandingkan pendapatan. "
                            "Pertimbangkan untuk mengurangi pengeluaran non-esensial.")
            
            # Savings rate check
            if savings_rate < Config.RECOMMENDED_SAVINGS_RATE * 100:
                advice.append(f"💡 Cobalah untuk menyisihkan minimal {Config.RECOMMENDED_SAVINGS_RATE * 100}% "
                            "dari pendapatan bulanan Anda untuk jangka panjang.")
            
            # Category-specific advice
            for category, amount in expense_categories.items():
                if category == 'food' and amount > monthly_income * 0.3:
                    advice.append("🍽️ Pengeluaran makanan Anda tinggi. "
                                "Pertimbangkan untuk merencanakan menu dan memasak di rumah.")
                elif category == 'entertainment' and amount > monthly_income * 0.2:
                    advice.append("🎮 Pengeluaran hiburan cukup signifikan. "
                                "Carilah alternatif hiburan gratis atau berbiaya rendah.")
            
            # Investment advice
            if balance > Config.INVESTMENT_THRESHOLD:
                advice.append("💰 Anda memiliki dana lebih yang bisa diinvestasikan. "
                            "Pertimbangkan untuk diversifikasi portfolio Anda.")
            
            # Market-based advice
            if market_change and market_change != 'N/A':
                market_change_float = float(market_change.strip('%'))
                if market_change_float > 0:
                    advice.append(f"📈 IHSG sedang naik ({market_change}). "
                                "Ini bisa jadi momentum baik untuk investasi jangka panjang.")
                elif market_change_float < -5:
                    advice.append(f"📉 IHSG sedang turun ({market_change}). "
                                "Tetap tenang dan fokus pada strategi investasi jangka panjang Anda.")
            
            # Currency advice
            if usd_rate:
                advice.append(f"💱 Kurs USD/IDR saat ini: Rp {(1/usd_rate):,.2f}. "
                            "Pertimbangkan ini dalam perencanaan keuangan Anda.")
            
            # If no specific advice was generated
            if not advice:
                advice.append("👍 Anda mengelola keuangan dengan baik! Pertahankan!")
            
            # Add general tips
            advice.append("\n💡 Tips umum:")
            advice.append("• Selalu catat setiap pengeluaran dan pemasukan")
            advice.append("• Evaluasi budget Anda secara berkala")
            advice.append("• Siapkan dana darurat")
            advice.append("• Diversifikasi investasi Anda")
            
            return "\n\n".join(advice)
            
        except Exception as e:
            logging.error(f"Error generating financial advice: {str(e)}")
            return "Maaf, terjadi kesalahan dalam menghasilkan saran keuangan. Silakan coba lagi nanti."

    def generate_report(self, user_id: int) -> Dict:
        """Generate a comprehensive financial report"""
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        return {
            'current_balance': self.get_balance(user_id),
            'monthly_summary': self.get_monthly_summary(user_id),
            'savings_goals': self.get_savings_goals(user_id),
            'advice': self.get_financial_advice(user_id)
        }
