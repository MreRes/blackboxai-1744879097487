from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Initialize Flask app
app = Flask(__name__, 
    template_folder='src/dashboard/templates',
    static_folder='src/dashboard/static'
)

# Database configuration
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/financial.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    transactions = db.relationship('Transaction', backref='user', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Initialize database and create test data
def init_db():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Add test user if not exists
        test_user = User.query.filter_by(username="test_user").first()
        if not test_user:
            test_user = User(username="test_user")
            db.session.add(test_user)
            db.session.commit()

        # Add sample transactions if none exist
        if not Transaction.query.first():
            sample_transactions = [
                Transaction(
                    amount=8000000,
                    category="Salary",
                    transaction_type="income",
                    description="Monthly salary",
                    user_id=test_user.id
                ),
                Transaction(
                    amount=5000000,
                    category="Housing",
                    transaction_type="expense",
                    description="Rent payment",
                    user_id=test_user.id
                )
            ]
            db.session.bulk_save_objects(sample_transactions)
            db.session.commit()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/transactions')
def get_transactions():
    transactions = Transaction.query.all()
    return jsonify([{
        'id': t.id,
        'amount': t.amount,
        'category': t.category,
        'type': t.transaction_type,
        'description': t.description,
        'date': t.date.strftime('%Y-%m-%d')
    } for t in transactions])

if __name__ == '__main__':
    # Initialize database and test data
    init_db()
    
    # Run the application
    app.run(host='0.0.0.0', port=8000, debug=True)
