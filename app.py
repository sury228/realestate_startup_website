"""
Mahamaya Real Estate — Main Flask Application
A premium real estate listing and management platform.
"""

import os
from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db, User

login_manager = LoginManager()
login_manager.login_view = 'admin.login'
login_manager.login_message_category = 'info'


def create_app():
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure required directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')), ''), exist_ok=True)
    instance_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')
    os.makedirs(instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.main import main_bp
    from routes.admin import admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    # Create tables and seed admin
    with app.app_context():
        db.create_all()
        seed_admin(app)
        seed_sample_plots()

    # Register error handlers
    register_error_handlers(app)

    return app


def seed_admin(app):
    """Create default admin user if none exists."""
    if User.query.count() == 0:
        admin = User(
            username=app.config.get('ADMIN_USERNAME', 'admin'),
            email='admin@mahamayarealestate.com'
        )
        admin.set_password(app.config.get('ADMIN_PASSWORD', 'admin123'))
        db.session.add(admin)
        db.session.commit()
        print("[OK] Default admin user created (username: admin, password: admin123)")


def seed_sample_plots():
    """Seed sample plots for demonstration if database is empty."""
    from models import Plot
    if Plot.query.count() == 0:
        sample_plots = [
            Plot(
                title="Premium Corner Plot — Sunrise Enclave",
                description="A beautifully located corner plot in the heart of Sunrise Enclave. Surrounded by lush greenery with excellent connectivity to the main highway. Ideal for building a dream villa or premium residence. All civic amenities including water, electricity, and sewage are readily available. Gated community with 24/7 security.",
                price=3500000,
                location="Raipur, Chhattisgarh",
                size="2400 sq ft",
                plot_type="Residential",
                is_featured=True,
                is_available=True
            ),
            Plot(
                title="Commercial Plot — Central Business District",
                description="Prime commercial plot located in the rapidly developing Central Business District. Perfect for office complexes, retail spaces, or mixed-use development. Excellent road frontage and visibility. Close to metro station and major commercial hubs.",
                price=8500000,
                location="Bilaspur, Chhattisgarh",
                size="5000 sq ft",
                plot_type="Commercial",
                is_featured=True,
                is_available=True
            ),
            Plot(
                title="Farmhouse Plot — Green Valley",
                description="Escape to serenity with this sprawling farmhouse plot in Green Valley. Surrounded by nature with views of the hills. Perfect for a weekend getaway or permanent residence away from the city noise. Fertile land suitable for organic farming.",
                price=2200000,
                location="Durg, Chhattisgarh",
                size="10000 sq ft",
                plot_type="Agricultural",
                is_featured=True,
                is_available=True
            ),
            Plot(
                title="Budget-Friendly Residential Plot",
                description="Affordable residential plot in a well-planned colony. Close to schools, hospitals, and shopping centers. Great investment opportunity with rapidly appreciating land value. Clear title and ready for immediate construction.",
                price=1200000,
                location="Korba, Chhattisgarh",
                size="1200 sq ft",
                plot_type="Residential",
                is_featured=False,
                is_available=True
            ),
            Plot(
                title="Industrial Plot — MIDC Zone",
                description="Large industrial plot in the MIDC-approved industrial zone. Ideal for manufacturing units, warehousing, or logistics operations. Excellent infrastructure with wide roads, power supply, and water facilities. Strategic location near the national highway.",
                price=15000000,
                location="Bhilai, Chhattisgarh",
                size="20000 sq ft",
                plot_type="Industrial",
                is_featured=True,
                is_available=True
            ),
            Plot(
                title="Luxury Villa Plot — Royal Gardens",
                description="Exclusive villa plot in the prestigious Royal Gardens township. World-class amenities including clubhouse, swimming pool, jogging track, and landscaped gardens. Premium neighbourhood with top-notch security and maintenance services.",
                price=6500000,
                location="Raipur, Chhattisgarh",
                size="3600 sq ft",
                plot_type="Residential",
                is_featured=True,
                is_available=True
            ),
            Plot(
                title="Riverside Plot — Tranquil Meadows",
                description="Serene riverside plot offering breathtaking views and a peaceful lifestyle. Perfect for a nature-inspired home design. Surrounded by established residential areas with all modern conveniences nearby.",
                price=4100000,
                location="Jagdalpur, Chhattisgarh",
                size="4000 sq ft",
                plot_type="Residential",
                is_featured=False,
                is_available=True
            ),
            Plot(
                title="Highway-Facing Commercial Land",
                description="Strategically located highway-facing commercial land ideal for petrol pumps, showrooms, restaurants, or retail chains. High traffic volume ensures excellent visibility and footfall. All clearances available.",
                price=12000000,
                location="Raipur, Chhattisgarh",
                size="8000 sq ft",
                plot_type="Commercial",
                is_featured=True,
                is_available=True
            ),
            Plot(
                title="Affordable NA Plot — City Edge",
                description="Non-agricultural (NA) converted plot on the outskirts of the city. Rapidly developing area with new road construction and infrastructure projects underway. Excellent long-term investment proposition.",
                price=950000,
                location="Dhamtari, Chhattisgarh",
                size="1500 sq ft",
                plot_type="Residential",
                is_featured=False,
                is_available=True
            ),
        ]
        db.session.add_all(sample_plots)
        db.session.commit()
        print(f"[OK] Seeded {len(sample_plots)} sample plots.")


def register_error_handlers(app):
    """Register custom error pages."""

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template
        return render_template('errors/500.html'), 500


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
