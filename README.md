# 🎮 Game Night Tracker

A comprehensive web application for tracking scores and managing competitions during game nights.

## 🚀 Quick Start

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Edit .env with your settings

# 4. Initialize database
python scripts/init_db.py

# 5. Run development server
python run.py
```

Visit `http://localhost:5000`
Default login: `admin` / `admin` ⚠️ Change immediately!

## 📁 Project Structure

```
app/
├── models/      # Database models
├── routes/      # Route blueprints  
├── services/    # Business logic
├── forms/       # WTForms
├── templates/   # Jinja2 templates
└── static/      # CSS, JS, images
```

## 🔧 Development

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Format code
black app/

# Lint code
flake8 app/
```

## 📚 Documentation

- Architecture overview: See code comments
- Migration guide: `MIGRATION_GUIDE.md`
- Contributing: `CONTRIBUTING.md`

## 📄 License

MIT License
