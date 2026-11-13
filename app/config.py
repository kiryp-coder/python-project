import os

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = int(os.environ.get("ACCESS_TOKEN_MINUTES", "30"))

CORS_ORIGINS = [origin.strip() for origin in os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")]

LOGIN_RATE_LIMIT = os.environ.get("LOGIN_RATE_LIMIT", "5/minute")

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin12345")

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6380/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6380/1")
CELERY_TASK_ALWAYS_EAGER = os.environ.get("CELERY_TASK_ALWAYS_EAGER", "false") == "true"
RECEIPT_SECONDS = float(os.environ.get("RECEIPT_SECONDS", "5"))
