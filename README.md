# Finance Manager - SQLite Flask App

Санхүүгийн орлого, зарлага, хуримтлалын хүүг сонгож хардаг, зорилго үүсгэж хадгалдаг веб хэрэгслэл.

## Features / Боломжууд

✨ **Income & Expense Tracking** - Орлого, зарлагын дэлгэрэнгүй бүртгэл
- Категоруудаар ангилана (Salary, Bonus, Food, Transport гэх мэт)
- Дэлгэрэнгүй тайлбарын сонголттой

💰 **Savings & Compound Interest** - Хуримтлал ба хурмалтын нийлмэл хүү
- Жилийн хүүг% нь оруулна
- Өдөр, сар, жилийн хүүн компаунд болно
- Өөр өөр хүүгийн төлөв тайрах боломжтой

🎯 **Financial Goals** - Санхүүгийн зорилго үүсгэх
- Зорилгын нэр, хэмжээ, сүүлийн хугацаа оруулна
- Напршлын сонирхол улбаатай байдлаас үзнэ
- Зорилгод хэмжээ нэмэх боломжтой

📊 **Dashboard** - Нийтийн хэргээ хяналтын самбар
- Нийт орлого, зарлага, үлэгдэл үзүүлэх
- Хадгаласаны бүх мөнгө
- Зорилгын улушлаасаа
- Сүүлийн гүйлгээнүүдийн түүх

🔐 **User Authentication** - Хэрэглэгчийн бүртгэл, нэвтрэх

## Installation / Суулгах

```bash
# Clone or create project
cd /opt/vercel-flask

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

Visit `http://localhost:5000` in your browser.

## File Structure / Файлын байгуулалта

```
/opt/vercel-flask/
├── app.py                 # Flask main application
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel deployment config
├── .env.example          # Environment variables example
├── finance.db            # SQLite database (created on first run)
└── templates/
    ├── base.html         # Base template
    ├── login.html        # Login page
    ├── register.html     # Registration page
    └── dashboard.html    # Main dashboard
```

## Database Schema / Өгөгдлийн сан

### Users
- Username, Email, Password Hash

### Transactions
- Type (income/expense), Category, Amount
- Description, Date, User reference

### Savings
- Initial Amount, Current Amount (with interest)
- Annual Interest Rate, Compound Frequency
- Creation date, Last calculation date

### Goals
- Name, Description, Target Amount, Current Amount
- Deadline, Status (active/completed/cancelled)

## Environment Variables / Орчны хувьсагч

Create `.env` file:
```
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
```

## Deployment to Vercel / Vercel-т байршуулах

1. Push code to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```

2. Connect to Vercel:
   - Visit https://vercel.com/new
   - Import GitHub repository
   - Vercel will auto-detect Flask
   - Set environment variables in project settings
   - Deploy!

## API Endpoints / API өндөрлөгүүд

### Authentication
- `POST /register` - Register new user
- `POST /login` - Login user
- `GET /logout` - Logout user

### Dashboard
- `GET /api/dashboard-summary` - Get summary stats

### Transactions
- `GET /api/transactions` - List all transactions
- `POST /api/transactions` - Create transaction
- `DELETE /api/transactions/<id>` - Delete transaction

### Savings
- `GET /api/savings` - List all savings
- `POST /api/savings` - Create savings account
- `DELETE /api/savings/<id>` - Delete savings

### Goals
- `GET /api/goals` - List all goals
- `POST /api/goals` - Create goal
- `GET /api/goals/<id>` - Get goal details
- `PUT /api/goals/<id>` - Update goal
- `POST /api/goals/<id>/contribute` - Add money to goal
- `DELETE /api/goals/<id>` - Delete goal

## Technologies / Технологиуд

- **Backend**: Flask 2.3.3
- **Database**: SQLite3
- **ORM**: SQLAlchemy 2.0
- **Authentication**: Flask-Login
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Deployment**: Vercel

## Local Testing / Орон нутгийн сорилт

```bash
# Run with debug mode
python app.py

# The app will be available at http://localhost:5000
```

## Security Notes / Аюулгүй байдлын үйлчлүүлэгч

- Change `SECRET_KEY` in production
- Use environment variables for sensitive data
- Implement rate limiting for APIs
- Add HTTPS in production
- Validate all user inputs

## License

Open source project

## Support

For issues or questions, create an issue in the repository.
# vercel-flask
