# 🎮 Game Night Tracker

A comprehensive web application for managing and tracking competitive game nights with real-time scoring, leaderboards, and tournament brackets.

## ✨ Features

- **Real-Time Scoring**: Live collaborative scoring with WebSocket synchronization
- **Leaderboard System**: Dynamic rankings with points and penalties
- **Tournament Brackets**: Single-elimination tournament management
- **Team Management**: Create and manage teams with participants
- **Game Library**: Flexible game types with custom scoring rules
- **Mobile-Optimized**: Responsive design for on-the-go scoring
- **Simulation Playground**: "What-if" scenario analysis
- **History Tracking**: Complete game night archives

## 🏗️ Architecture

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLAlchemy ORM with SQLite/PostgreSQL
- **Real-time**: Socket.IO for WebSocket communication
- **Authentication**: Flask-Login with secure session management
- **Security**: CSRF protection, rate limiting, security headers

### Frontend
- **Build System**: Webpack 5 with Babel and PostCSS
- **JavaScript**: ES6 modules with service layer architecture
- **CSS**: Modular stylesheets (12,000+ lines)
- **Real-time**: Socket.IO client for live updates

### Code Quality
- **Test Coverage**: 72%+ (474 passing tests)
- **Logging**: Structured logging with rotation
- **Error Handling**: Custom exceptions with proper error pages
- **Performance**: Optimized with eager loading and database indexes

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+ and npm
- Virtual environment tool (venv/virtualenv)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd GameNight

# Set up Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install

# Build frontend assets
npm run build

# Initialize database
flask db upgrade

# Run the application
flask run
```

### Development Mode

```bash
# Terminal 1: Run Flask with auto-reload
flask run --debug

# Terminal 2: Watch frontend files
npm run watch
```

Access the application at `http://localhost:5000`

## 📁 Project Structure

```
GameNight/
├── app/
│   ├── __init__.py           # Application factory
│   ├── models/               # Database models
│   ├── routes/               # Flask blueprints
│   │   ├── main.py          # Public routes
│   │   ├── admin.py         # Admin routes
│   │   └── auth.py          # Authentication
│   ├── services/             # Business logic layer
│   ├── websockets/           # WebSocket handlers
│   ├── forms/                # WTForms definitions
│   ├── templates/            # Jinja2 templates
│   ├── static/
│   │   ├── js/
│   │   │   └── src/         # Modular ES6 source
│   │   │       ├── services/  # API, WebSocket, State
│   │   │       └── utils/     # DOM, validators, formatting
│   │   ├── css/             # Stylesheets
│   │   └── dist/            # Build output (generated)
│   ├── utils/               # Python utilities
│   │   ├── logger.py        # Structured logging
│   │   └── route_helpers.py # Route utilities
│   └── exceptions.py        # Custom exceptions
├── tests/                   # Test suite (474 tests)
├── migrations/              # Database migrations
├── config.py                # Configuration
├── requirements.txt         # Python dependencies
├── package.json             # Node.js dependencies
├── webpack.config.js        # Build configuration
├── FRONTEND_ARCHITECTURE.md # Frontend docs
└── README.md               # This file
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/integration/test_admin_routes.py

# Run with verbose output
pytest -v
```

Current test coverage: **72.25%** (474 passing tests)

## 📚 Documentation

- [Frontend Architecture Guide](FRONTEND_ARCHITECTURE.md) - Detailed frontend documentation
- [API Documentation](#api-documentation) - REST API endpoints (see routes/)
- [WebSocket Events](#websocket-events) - Real-time event reference (see websockets/)

## 🔧 Development

### Backend Development

Key improvements implemented:
- ✅ Structured logging with rotation
- ✅ Custom exception classes for better error handling
- ✅ Professional error pages (404, 500, 403)
- ✅ Refactored code with helper utilities
- ✅ Fixed N+1 queries with eager loading
- ✅ Added composite database indexes

### Frontend Development

Modern architecture with:
- ✅ Webpack build system with minification
- ✅ ES6 module structure
- ✅ Service layer (API, WebSocket, State management)
- ✅ Utility modules (DOM helpers, validators, formatters)
- ✅ Build commands: `npm run build`, `npm run watch`

### Adding New Features

1. **Backend**: Add routes in `app/routes/`, business logic in `app/services/`
2. **Frontend**: Create modules in `app/static/js/src/`, use services for API/state
3. **Tests**: Add tests in `tests/`, maintain 70%+ coverage
4. **Documentation**: Update relevant .md files

## 🔐 Security

- CSRF protection on all forms
- Rate limiting on sensitive endpoints
- Secure session management
- SQL injection prevention via SQLAlchemy
- XSS prevention via Jinja2 auto-escaping
- Security headers (CSP, HSTS, X-Frame-Options)
- Input validation on all user data

## 🎯 Key Features Detail

### Real-Time Scoring
- WebSocket-based live updates
- Collaborative editing with lock management
- Multi-timer support for timed games
- Auto-save functionality

### Leaderboard System
- Dynamic point calculation
- Support for penalties (stackable and one-time)
- Multiple scoring directions (higher/lower better)
- Game night-specific rankings

### Tournament System
- Single-elimination bracket generation
- Automatic winner advancement
- Play-in match support for odd teams
- Match-by-match scoring

## 🚢 Deployment

### Environment Variables

```bash
# Required
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///gamenight.db  # or PostgreSQL URL

# Optional
FLASK_ENV=production
LOG_LEVEL=INFO
```

### Production Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Configure production database
- [ ] Run `npm run build` for optimized assets
- [ ] Set up log rotation
- [ ] Configure HTTPS
- [ ] Set up monitoring/error tracking
- [ ] Run database migrations
- [ ] Set up backup strategy

## 📊 Performance

- Database queries optimized with eager loading
- Composite indexes on frequent queries
- Frontend assets minified and hashed
- Browser caching with content hashing
- WebSocket connection pooling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

- **Python**: Follow PEP 8
- **JavaScript**: ES6+ with semicolons
- **CSS**: BEM naming convention (in progress)
- **Commits**: Conventional commit messages

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Credits

Built with ❤️ for epic game nights

### Technologies

- Flask & SQLAlchemy
- Socket.IO
- Webpack & Babel
- Font Awesome icons
- Google Fonts

## 📞 Support

- **Issues**: GitHub Issues
- **Documentation**: See FRONTEND_ARCHITECTURE.md
- **Questions**: Open a discussion

## 🗺️ Roadmap

### Completed ✅
- Modern frontend architecture
- Service layer with API/WebSocket/State management
- Utility modules and build system
- Structured logging and error handling
- Performance optimizations
- Comprehensive test suite

### In Progress 🚧
- Refactoring large JavaScript files into modules
- CSS architecture restructuring with BEM
- Template componentization

### Planned 📋
- TypeScript migration
- PWA features (offline support)
- Advanced analytics and insights
- Mobile app (React Native)
- Multi-language support

---

**Version**: 1.0.0
**Last Updated**: 2025-10-22
**Status**: Production-Ready ✨
