"""
API Request Logger Middleware
==============================
Automatically logs every incoming API request:
  - Method, path, status code, response time, user
No changes needed in views — this runs for every request automatically.
"""
import time
import logging

api_logger = logging.getLogger('api_requests')


class APIRequestLoggerMiddleware:
    """Logs every request: method, path, user, status, duration."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        # Process the request
        response = self.get_response(request)

        # Calculate duration
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Get user info
        user = getattr(request, 'user', None)
        user_str = (
            f"{user.email}" if user and user.is_authenticated
            else "anonymous"
        )

        # Only log API paths (skip admin, static files)
        if request.path.startswith('/api/'):
            level = logging.ERROR if response.status_code >= 500 \
                else logging.WARNING if response.status_code >= 400 \
                else logging.INFO

            api_logger.log(
                level,
                f"{request.method} {request.path} "
                f"→ {response.status_code} "
                f"[{duration_ms}ms] "
                f"user={user_str}"
            )

        return response