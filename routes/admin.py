"""
Admin routes for the Mahamaya Real Estate dashboard.
Handles login, plot CRUD, image upload, and query management.
"""

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, Plot, Query

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def allowed_file(filename):
    """Check if file extension is allowed."""
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page."""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            flash('Welcome back! Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('admin/login.html')


@admin_bp.route('/logout')
@login_required
def logout():
    """Admin logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))


@admin_bp.route('/')
@login_required
def dashboard():
    """Admin dashboard overview."""
    total_plots = Plot.query.count()
    available_plots = Plot.query.filter_by(is_available=True).count()
    total_queries = Query.query.count()
    unread_queries = Query.query.filter_by(is_read=False).count()
    recent_queries = Query.query.order_by(Query.created_at.desc()).limit(5).all()
    recent_plots = Plot.query.order_by(Plot.created_at.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        total_plots=total_plots,
        available_plots=available_plots,
        total_queries=total_queries,
        unread_queries=unread_queries,
        recent_queries=recent_queries,
        recent_plots=recent_plots
    )


@admin_bp.route('/plots')
@login_required
def manage_plots():
    """List all plots for management."""
    page = request.args.get('page', 1, type=int)
    plots = Plot.query.order_by(Plot.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/manage_plots.html', plots=plots)


@admin_bp.route('/plots/add', methods=['GET', 'POST'])
@login_required
def add_plot():
    """Add a new plot listing."""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', 0, type=float)
        location = request.form.get('location', '').strip()
        size = request.form.get('size', '').strip()
        plot_type = request.form.get('plot_type', 'Residential').strip()
        is_featured = request.form.get('is_featured') == 'on'
        is_available = request.form.get('is_available', 'on') == 'on'

        # Validation
        if not title or not location or not size or price <= 0:
            flash('Please fill in all required fields with valid data.', 'danger')
            return redirect(url_for('admin.add_plot'))

        # Handle image upload
        image_filename = 'default_plot.jpg'
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to prevent name collision
                import time
                filename = f"{int(time.time())}_{filename}"
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                file.save(upload_path)
                image_filename = filename

        new_plot = Plot(
            title=title,
            description=description,
            price=price,
            location=location,
            size=size,
            plot_type=plot_type,
            image_filename=image_filename,
            is_featured=is_featured,
            is_available=is_available
        )
        db.session.add(new_plot)
        db.session.commit()

        flash(f'Plot "{title}" added successfully!', 'success')
        return redirect(url_for('admin.manage_plots'))

    return render_template('admin/add_plot.html')


@admin_bp.route('/plots/edit/<int:plot_id>', methods=['GET', 'POST'])
@login_required
def edit_plot(plot_id):
    """Edit an existing plot."""
    plot = Plot.query.get_or_404(plot_id)

    if request.method == 'POST':
        plot.title = request.form.get('title', plot.title).strip()
        plot.description = request.form.get('description', '').strip()
        plot.price = request.form.get('price', plot.price, type=float)
        plot.location = request.form.get('location', plot.location).strip()
        plot.size = request.form.get('size', plot.size).strip()
        plot.plot_type = request.form.get('plot_type', 'Residential').strip()
        plot.is_featured = request.form.get('is_featured') == 'on'
        plot.is_available = request.form.get('is_available') == 'on'

        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                import time
                filename = f"{int(time.time())}_{filename}"
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                file.save(upload_path)

                # Delete old image if not default
                if plot.image_filename and plot.image_filename != 'default_plot.jpg':
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], plot.image_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)

                plot.image_filename = filename

        db.session.commit()
        flash(f'Plot "{plot.title}" updated successfully!', 'success')
        return redirect(url_for('admin.manage_plots'))

    return render_template('admin/edit_plot.html', plot=plot)


@admin_bp.route('/plots/delete/<int:plot_id>', methods=['POST'])
@login_required
def delete_plot(plot_id):
    """Delete a plot listing."""
    plot = Plot.query.get_or_404(plot_id)
    title = plot.title

    # Delete associated image
    if plot.image_filename and plot.image_filename != 'default_plot.jpg':
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], plot.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(plot)
    db.session.commit()
    flash(f'Plot "{title}" deleted successfully.', 'warning')
    return redirect(url_for('admin.manage_plots'))


@admin_bp.route('/queries')
@login_required
def queries():
    """View all customer queries."""
    page = request.args.get('page', 1, type=int)
    filter_type = request.args.get('filter', 'all', type=str)

    query = Query.query
    if filter_type == 'unread':
        query = query.filter_by(is_read=False)
    elif filter_type == 'read':
        query = query.filter_by(is_read=True)

    all_queries = query.order_by(Query.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    unread_count = Query.query.filter_by(is_read=False).count()

    return render_template('admin/queries.html', queries=all_queries, filter_type=filter_type, unread_count=unread_count)


@admin_bp.route('/queries/read/<int:query_id>', methods=['POST'])
@login_required
def mark_read(query_id):
    """Mark a query as read."""
    q = Query.query.get_or_404(query_id)
    q.is_read = True
    db.session.commit()
    flash('Query marked as read.', 'info')
    return redirect(url_for('admin.queries'))


@admin_bp.route('/queries/delete/<int:query_id>', methods=['POST'])
@login_required
def delete_query(query_id):
    """Delete a customer query."""
    q = Query.query.get_or_404(query_id)
    db.session.delete(q)
    db.session.commit()
    flash('Query deleted.', 'warning')
    return redirect(url_for('admin.queries'))
