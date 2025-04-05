import base64
import hmac
import hashlib
import time
import json

from functools import wraps
from datetime import timedelta


from flask import request, jsonify

# SECRET_KEY = current_app.config['SECRET_KEY']

class CustomJWT:
    def __init__(self, secret_key=None, algorithm="HS256", access_expiry=timedelta(seconds=60), refresh_expiry=timedelta(seconds=86400)):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_expiry = access_expiry  # 1 hour
        self.refresh_expiry = refresh_expiry  # 1 day

    def init_app(self, app):
        """Initialize with Flask app context"""
        self.secret_key = app.config['JWT_SECRET_KEY'].encode()
        self.algorithm = app.config['JWT_ALGORITHM']
        self.access_expiry = app.config['JWT_ACCESS_TOKEN_EXPIRES']
        self.refresh_expiry = app.config['JWT_REFRESH_TOKEN_EXPIRES']

    def base64_encode(self, data):
        """Base64 encode JSON object"""
        return base64.urlsafe_b64encode(json.dumps(data).encode()).decode().strip("=")

    def base64_decode(self, data):
        """Base64 decode JSON object"""
        try:
            padding = "=" * (4 - len(data) % 4)
            decode_data = base64.urlsafe_b64decode(data+padding)
            return json.loads(decode_data.decode())
        except Exception:
            return None

    def sign(self, data):
        """Create HMAC-SHA256 signature"""
        return base64.urlsafe_b64encode(
            hmac.new(self.secret_key, data.encode(), hashlib.sha256).digest()
        ).decode().strip("=")

    def create_token(self, user_id, token_type="access"):
        """Manually create JWT"""
        header = {"alg": self.algorithm, "typ": "JWT"}
        expiry = int(self.access_expiry.total_seconds()) if token_type == "access" else int(
            self.refresh_expiry.total_seconds())

        payload = {
            "sub": user_id,
            "exp": int(time.time()) + expiry,
            "iat": int(time.time()),
            "type": token_type
        }

        # Encode Parts
        encoded_header = self.base64_encode(header)
        encoded_payload = self.base64_encode(payload)

        # Create Signature
        signature = self.sign(f"{encoded_header}.{encoded_payload}")

        # Construct JWT
        return f"{encoded_header}.{encoded_payload}.{signature}"

    def decode_token(self, token):
        """Manually decode and verify JWT"""
        try:
            header_b64, payload_b64, signature = token.split(".")
            expected_signature = self.sign(f"{header_b64}.{payload_b64}")

            if not hmac.compare_digest(expected_signature, signature):
                return None

            payload = self.base64_decode(payload_b64)
            if not payload or time.time() > payload["exp"]:
                return None

            return payload["sub"]
        except Exception:
            return None

    def token_required(self, refresh=False):
        """Decorator to protect routes"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                token = None
                if not refresh:
                    auth_header = request.headers.get("Authorization")
                    token = auth_header.split(" ")[1] if " " in auth_header else auth_header
                else:
                    # For refresh token: check cookies
                    token = request.cookies.get("refresh_token")

                if not token:
                    source = "Authorization header" if not refresh else "refresh_token cookie"
                    return jsonify({"message": f"Missing token in {source}"}), 401

                user_id = self.decode_token(token)
                if not user_id:
                    return jsonify({"message": "Invalid or expired token"}), 401

                # If refresh=True, verify this is a refresh token
                if refresh:
                    try:
                        # Decode without validation to check token type
                        header_b64, payload_b64, _ = token.split(".")
                        payload = self.base64_decode(payload_b64)
                        if payload.get("type") != "refresh":
                            return jsonify({"message": "Access token provided, refresh required"}), 401
                    except Exception:
                        return jsonify({"message": "Invalid token format"}), 401
                    return func(user_id, *args, **kwargs)

                return func(user_id, *args, **kwargs)
            return wrapper
        return decorator

# Initialize JWT Manager
jwt_manager = CustomJWT()
