"""Configuration de SMART WATER AI.
Les secrets sont lus depuis les variables d'environnement (.env), jamais codés en dur."""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Clé secrète : obligatoire (sessions + CSRF). Pas de valeur par défaut.
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Sessions et cookies sécurisés
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False          # True en production (HTTPS)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

    # CSRF (Flask-WTF)
    WTF_CSRF_ENABLED = True

    # Limitation des tentatives de connexion
    LOGIN_RATE_LIMIT = "5 per minute"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


def get_config():
    return ProductionConfig if os.environ.get("FLASK_ENV") == "production" else DevelopmentConfig
