# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///learning_league.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
