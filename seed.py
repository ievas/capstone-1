
from models import User, Level, Badge, Streak, UserBadge, UserLevel
from app import db

db.drop_all()
db.create_all()