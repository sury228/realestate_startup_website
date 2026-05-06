"""
SQLAlchemy models for Mahamaya Real Estate.
Defines User (admin), Plot, and Query tables.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Admin user model for dashboard authentication."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Plot(db.Model):
    """Real estate plot listing model."""
    __tablename__ = 'plots'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    size = db.Column(db.String(100), nullable=False)  # e.g., "1200 sq ft"
    plot_type = db.Column(db.String(100), nullable=True, default='Residential')
    image_filename = db.Column(db.String(300), nullable=True, default='default_plot.jpg')
    is_featured = db.Column(db.Boolean, default=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def formatted_price(self):
        """Return price in Indian ₹ format."""
        if self.price >= 10000000:
            return f"₹{self.price / 10000000:.2f} Cr"
        elif self.price >= 100000:
            return f"₹{self.price / 100000:.2f} Lakh"
        else:
            return f"₹{self.price:,.0f}"

    def __repr__(self):
        return f'<Plot {self.title}>'


class Query(db.Model):
    """Customer query / contact form submissions."""
    __tablename__ = 'queries'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    subject = db.Column(db.String(200), nullable=True, default='General Inquiry')
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Query from {self.name}>'
