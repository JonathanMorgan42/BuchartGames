"""Development Server Entry Point."""
import os
from app import create_app

config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = app.config.get('DEBUG', True)
    host = os.getenv('HOST', '127.0.0.1')
    
    print(f"""
╔══════════════════════════════════════════╗
║  Game Night Tracker Development Server   ║
╚══════════════════════════════════════════╝

Environment: {config_name}
Running on: http://{host}:{port}
Debug mode: {'ON' if debug else 'OFF'}

Press CTRL+C to quit
    """)
    
    app.run(host=host, port=port, debug=debug)
