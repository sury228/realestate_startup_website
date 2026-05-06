"""
Main routes for public-facing pages.
Handles Home, About, Plots, Services, Contact, and Plot Detail pages.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from models import db, Plot, Query
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    """Home page with featured plots and hero section."""
    featured_plots = Plot.query.filter_by(is_featured=True, is_available=True).limit(6).all()
    total_plots = Plot.query.filter_by(is_available=True).count()
    return render_template('home.html', featured_plots=featured_plots, total_plots=total_plots)


@main_bp.route('/about')
def about():
    """About Us page."""
    return render_template('about.html')


@main_bp.route('/plots')
def plots():
    """Available plots listing with search and filter."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    location_filter = request.args.get('location', '', type=str)
    plot_type_filter = request.args.get('plot_type', '', type=str)
    min_price = request.args.get('min_price', 0, type=float)
    max_price = request.args.get('max_price', 0, type=float)
    sort_by = request.args.get('sort', 'newest', type=str)

    query = Plot.query.filter_by(is_available=True)

    # Search
    if search:
        query = query.filter(
            db.or_(
                Plot.title.ilike(f'%{search}%'),
                Plot.location.ilike(f'%{search}%'),
                Plot.description.ilike(f'%{search}%')
            )
        )

    # Filters
    if location_filter:
        query = query.filter(Plot.location.ilike(f'%{location_filter}%'))
    if plot_type_filter:
        query = query.filter(Plot.plot_type == plot_type_filter)
    if min_price > 0:
        query = query.filter(Plot.price >= min_price)
    if max_price > 0:
        query = query.filter(Plot.price <= max_price)

    # Sort
    if sort_by == 'price_low':
        query = query.order_by(Plot.price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Plot.price.desc())
    elif sort_by == 'size':
        query = query.order_by(Plot.size.desc())
    else:
        query = query.order_by(Plot.created_at.desc())

    plots_paginated = query.paginate(page=page, per_page=9, error_out=False)

    # Get unique locations and types for filter dropdowns
    locations = db.session.query(Plot.location).distinct().all()
    plot_types = db.session.query(Plot.plot_type).distinct().all()

    return render_template(
        'plots.html',
        plots=plots_paginated,
        search=search,
        location_filter=location_filter,
        plot_type_filter=plot_type_filter,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        locations=[l[0] for l in locations],
        plot_types=[t[0] for t in plot_types if t[0]]
    )


@main_bp.route('/plot/<int:plot_id>')
def plot_detail(plot_id):
    """Single plot detail page."""
    plot = Plot.query.get_or_404(plot_id)
    related_plots = Plot.query.filter(
        Plot.id != plot_id,
        Plot.is_available == True,
        Plot.location == plot.location
    ).limit(3).all()
    return render_template('plot_detail.html', plot=plot, related_plots=related_plots)


@main_bp.route('/services')
def services():
    """Services page."""
    return render_template('services.html')


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with form submission and email notification."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        subject = request.form.get('subject', 'General Inquiry').strip()
        message = request.form.get('message', '').strip()

        # Validation
        if not name or not email or not message:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('main.contact'))

        # Save to database
        new_query = Query(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message
        )
        db.session.add(new_query)
        db.session.commit()

        # Send email notification
        try:
            send_notification_email(name, email, phone, subject, message)
        except Exception as e:
            current_app.logger.error(f"Email notification failed: {e}")

        flash('Thank you! Your message has been sent successfully. We will get back to you soon.', 'success')
        return redirect(url_for('main.contact'))

    return render_template('contact.html')


def send_notification_email(name, email, phone, subject, message):
    """Send email notification to business owner when a new query is submitted."""
    config = current_app.config
    owner_email = config.get('BUSINESS_OWNER_EMAIL')
    mail_username = config.get('MAIL_USERNAME')
    mail_password = config.get('MAIL_PASSWORD')
    mail_server = config.get('MAIL_SERVER')
    mail_port = config.get('MAIL_PORT')

    if not all([owner_email, mail_username, mail_password]):
        current_app.logger.warning("Email not configured. Skipping notification.")
        return

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'New Inquiry: {subject} — Mahamaya Real Estate'
    msg['From'] = mail_username
    msg['To'] = owner_email

    html_body = f"""
    <html>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f8; padding: 30px;">
        <div style="max-width: 600px; margin: auto; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.08);">
            <div style="background: linear-gradient(135deg, #1a3a5c, #2980b9); color: #fff; padding: 24px 30px;">
                <h2 style="margin: 0;">🏠 New Customer Inquiry</h2>
                <p style="margin: 5px 0 0; opacity: 0.9; font-size: 14px;">Mahamaya Real Estate</p>
            </div>
            <div style="padding: 30px;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr><td style="padding: 10px 0; color: #666; font-weight: 600;">Name:</td><td style="padding: 10px 0;">{name}</td></tr>
                    <tr><td style="padding: 10px 0; color: #666; font-weight: 600;">Email:</td><td style="padding: 10px 0;"><a href="mailto:{email}">{email}</a></td></tr>
                    <tr><td style="padding: 10px 0; color: #666; font-weight: 600;">Phone:</td><td style="padding: 10px 0;">{phone or 'Not provided'}</td></tr>
                    <tr><td style="padding: 10px 0; color: #666; font-weight: 600;">Subject:</td><td style="padding: 10px 0;">{subject}</td></tr>
                </table>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <h4 style="color: #333; margin-bottom: 8px;">Message:</h4>
                <p style="color: #555; line-height: 1.7; background: #f9fafb; padding: 15px; border-radius: 8px;">{message}</p>
            </div>
            <div style="background: #f9fafb; padding: 15px 30px; text-align: center; font-size: 12px; color: #999;">
                Sent from Mahamaya Real Estate Website
            </div>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_body, 'html'))

    try:
        with smtplib.SMTP(mail_server, mail_port) as server:
            server.starttls()
            server.login(mail_username, mail_password)
            server.send_message(msg)
        current_app.logger.info(f"Notification email sent for query from {name}")
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {e}")
        raise
