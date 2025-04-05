from functools import wraps
from flask import request, jsonify

from app.middleware.jwt_auth import jwt_manager
from app.extensions import redis_client

# from redis.exceptions import RedisError, WatchError

class CustomLimiter:

    def __init__(self, max_requests=None, window_seconds=None):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def init_app(self, app):
        self.max_requests = app.config['RATE_LIMIT_MAX_REQUESTS']
        self.window_seconds = app.config['RATE_LIMIT_WINDOW_SECONDS']
        print(self.max_requests, self.window_seconds)

    def redis_rate_limiter(self, max_requests=None, window_seconds=None, auth=True):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                _max_requests = max_requests or self.max_requests
                _window_seconds = window_seconds or self.window_seconds

                ip_identifier = request.remote_addr

                if auth:
                    auth_header = request.headers.get("Authorization")
                    if not auth_header:
                        return jsonify({"message": "Missing token"}), 401

                    token = auth_header.split(" ")[1] if " " in auth_header else auth_header
                    user_id = jwt_manager.decode_token(token)

                    if not user_id:
                        return jsonify({"message": "Invalid or expired token"}), 401
                    key = f"rate_limit:{ip_identifier}:{user_id}:{func.__name__}"
                else:
                    key = f"rate_limit:{ip_identifier}:{func.__name__}"

                # try:
                #     with redis_client.client.pipeline() as pipe:
                #         while True:
                #             try:
                #                 pipe.watch(key)
                #                 current = pipe.get(key)
                #                 pipe.multi()
                #                 if current:
                #                     if int(current) >= self.max_requests:
                #                         return jsonify({"error": "Rate limit exceeded. Try again later."}), 429
                #                     pipe.incr(key)
                #                 else:
                #                     pipe.set(key, 1, ex=self.window_seconds)
                #                 pipe.execute()
                #                 break
                #             except WatchError:
                #                 continue
                # except RedisError:
                #     return jsonify({"error": "Redis error. Try again later."}), 503

                lua_script = """
                local key = KEYS[1]
                local max_requests = tonumber(ARGV[1])
                local window = tonumber(ARGV[2])
                local current = redis.call("GET", key)

                if current then
                    if tonumber(current) >= max_requests then
                        return -1
                    else
                        return redis.call("INCR", key)
                    end
                else
                    redis.call("SET", key, 1, "EX", window)
                    return 1
                end
                """

                result = redis_client.client.eval(lua_script, 1, key, _max_requests, _window_seconds)

                if result == -1:
                    response = jsonify({"error": "Rate limit exceeded. Try again later."})
                    response.status_code = 429
                    response.headers["Retry-After"] = str(_window_seconds)
                    return response

                return func(*args, **kwargs)
            return wrapper
        return decorator

limiter_manager = CustomLimiter()
