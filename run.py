import os
from app import create_app

# Get the environment from FLASK_ENV or default to 'development'
env = os.getenv('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    # Get host and port from environment variables or use defaults
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))

    # Run the Flask app
    app.run(host=host, port=port, debug=False)