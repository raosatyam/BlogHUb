from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis

# Initialize SQLAlchemy
db = SQLAlchemy()

# Initialize JWT
jwt = JWTManager()

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Create a Redis client class
class RedisClient:
    def __init__(self):
        self.client = None

    def initialize(self, app):
        """Initialize the Redis client with app configuration."""
        self.client = redis.Redis(
            host=app.config['REDIS_HOST'],
            port=app.config['REDIS_PORT'],
            db=app.config['REDIS_DB'],
            password=app.config['REDIS_PASSWORD'] or None,
            decode_responses=True
        )

# Initialize Redis client
redis_client = RedisClient()
