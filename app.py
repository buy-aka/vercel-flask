from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    savings = db.relationship('Savings', backref='user', lazy=True, cascade='all, delete-orphan')
    goals = db.relationship('Goal', backref='user', lazy=True, cascade='all, delete-orphan')

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'category': self.category,
            'amount': self.amount,
            'description': self.description,
            'date': self.date.isoformat()
        }

class Savings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    initial_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, nullable=False)
    annual_rate = db.Column(db.Float, nullable=False)  # Interest rate in percentage
    compound_frequency = db.Column(db.String(20), default='monthly')  # daily, monthly, yearly
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_calculated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def calculate_compound_interest(self):
        """Calculate compound interest and update current amount"""
        periods = {
            'daily': 365,
            'monthly': 12,
            'yearly': 1
        }
        
        n = periods.get(self.compound_frequency, 12)
        r = self.annual_rate / 100
        
        days_passed = (datetime.utcnow() - self.last_calculated).days
        t = days_passed / 365
        
        self.current_amount = self.initial_amount * ((1 + r/n) ** (n * t))
        self.last_calculated = datetime.utcnow()
        db.session.commit()
        
        return self.current_amount
    
    def to_dict(self):
        self.calculate_compound_interest()
        return {
            'id': self.id,
            'initial_amount': self.initial_amount,
            'current_amount': round(self.current_amount, 2),
            'annual_rate': self.annual_rate,
            'compound_frequency': self.compound_frequency,
            'created_at': self.created_at.isoformat()
        }

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0)
    deadline = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    
    def progress_percentage(self):
        if self.target_amount == 0:
            return 0
        return (self.current_amount / self.target_amount) * 100
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'progress_percentage': round(self.progress_percentage(), 2),
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes - Authentication
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'Registration successful'}), 201
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return jsonify({'message': 'Login successful'}), 200
        
        return jsonify({'error': 'Invalid username or password'}), 401
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Routes - Dashboard
@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/dashboard-summary')
@login_required
def get_dashboard_summary():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    savings = Savings.query.filter_by(user_id=current_user.id).all()
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.type == 'expense')
    total_savings = sum(s.calculate_compound_interest() for s in savings)
    total_goals_target = sum(g.target_amount for g in goals if g.status == 'active')
    total_goals_current = sum(g.current_amount for g in goals if g.status == 'active')
    
    return jsonify({
        'total_income': round(total_income, 2),
        'total_expenses': round(total_expenses, 2),
        'balance': round(total_income - total_expenses, 2),
        'total_savings': round(total_savings, 2),
        'total_goals_target': round(total_goals_target, 2),
        'total_goals_current': round(total_goals_current, 2),
        'goals_progress': round((total_goals_current / total_goals_target * 100) if total_goals_target > 0 else 0, 2)
    })

# Routes - Transactions
@app.route('/api/transactions', methods=['GET', 'POST'])
@login_required
def transactions():
    if request.method == 'POST':
        data = request.get_json()
        transaction = Transaction(
            user_id=current_user.id,
            type=data.get('type'),
            category=data.get('category'),
            amount=float(data.get('amount')),
            description=data.get('description'),
            date=datetime.fromisoformat(data.get('date')) if data.get('date') else datetime.utcnow()
        )
        db.session.add(transaction)
        db.session.commit()
        return jsonify(transaction.to_dict()), 201
    
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    return jsonify([t.to_dict() for t in transactions])

@app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if not transaction or transaction.user_id != current_user.id:
        return jsonify({'error': 'Transaction not found'}), 404
    
    db.session.delete(transaction)
    db.session.commit()
    return jsonify({'message': 'Transaction deleted'}), 200

# Routes - Savings
@app.route('/api/savings', methods=['GET', 'POST'])
@login_required
def savings():
    if request.method == 'POST':
        data = request.get_json()
        saving = Savings(
            user_id=current_user.id,
            initial_amount=float(data.get('initial_amount')),
            current_amount=float(data.get('initial_amount')),
            annual_rate=float(data.get('annual_rate')),
            compound_frequency=data.get('compound_frequency', 'monthly')
        )
        db.session.add(saving)
        db.session.commit()
        return jsonify(saving.to_dict()), 201
    
    savings_list = Savings.query.filter_by(user_id=current_user.id).all()
    return jsonify([s.to_dict() for s in savings_list])

@app.route('/api/savings/<int:saving_id>', methods=['DELETE'])
@login_required
def delete_savings(saving_id):
    saving = Savings.query.get(saving_id)
    if not saving or saving.user_id != current_user.id:
        return jsonify({'error': 'Savings not found'}), 404
    
    db.session.delete(saving)
    db.session.commit()
    return jsonify({'message': 'Savings deleted'}), 200

# Routes - Goals
@app.route('/api/goals', methods=['GET', 'POST'])
@login_required
def goals():
    if request.method == 'POST':
        data = request.get_json()
        goal = Goal(
            user_id=current_user.id,
            name=data.get('name'),
            description=data.get('description'),
            target_amount=float(data.get('target_amount')),
            deadline=datetime.fromisoformat(data.get('deadline')) if data.get('deadline') else None
        )
        db.session.add(goal)
        db.session.commit()
        return jsonify(goal.to_dict()), 201
    
    goals_list = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.created_at.desc()).all()
    return jsonify([g.to_dict() for g in goals_list])

@app.route('/api/goals/<int:goal_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def goal_detail(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal or goal.user_id != current_user.id:
        return jsonify({'error': 'Goal not found'}), 404
    
    if request.method == 'DELETE':
        db.session.delete(goal)
        db.session.commit()
        return jsonify({'message': 'Goal deleted'}), 200
    
    if request.method == 'PUT':
        data = request.get_json()
        goal.name = data.get('name', goal.name)
        goal.description = data.get('description', goal.description)
        goal.target_amount = float(data.get('target_amount', goal.target_amount))
        goal.current_amount = float(data.get('current_amount', goal.current_amount))
        goal.status = data.get('status', goal.status)
        if data.get('deadline'):
            goal.deadline = datetime.fromisoformat(data.get('deadline'))
        db.session.commit()
        return jsonify(goal.to_dict()), 200
    
    return jsonify(goal.to_dict())

@app.route('/api/goals/<int:goal_id>/contribute', methods=['POST'])
@login_required
def contribute_to_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal or goal.user_id != current_user.id:
        return jsonify({'error': 'Goal not found'}), 404
    
    data = request.get_json()
    amount = float(data.get('amount', 0))
    
    goal.current_amount += amount
    if goal.current_amount >= goal.target_amount:
        goal.status = 'completed'
    
    db.session.commit()
    return jsonify(goal.to_dict()), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5001)
