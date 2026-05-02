from flask import Blueprint, render_template, flash, request, redirect, url_for, session
from app.extensions import db
from app.models import User, Product
from app.service.auth import AuthService
from app.service.productqueryservice import ProductQueryService
from app.utils import user_roles

main = Blueprint('main', __name__)


@main.route('/')
def home_page():
    if session.get('user_role') == 'admin':
        return redirect(url_for('main.admin_home_page'))
    return render_template('index.html')


@main.route('/about')
def about_page():
    return render_template('about.html')


@main.route('/signin', methods=['POST', 'GET'])
def signin_page():
    if 'user_id' in session:
        flash('You are already signed in.', 'error')
        return redirect(url_for('main.home_page'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        existing_user, error = AuthService.signin_user(email, password)
        if error:
            flash(error, 'error')
            return render_template('signinpage.html')

        AuthService.login_user(existing_user)

        flash("Login Successful", 'success')
        if existing_user.role == 'admin':
            return redirect(url_for('main.admin_home_page'))
        return redirect(url_for('main.home_page'))

    return render_template('signinpage.html')


@main.route('/signup', methods=['POST', 'GET'])
def signup_page():
    if 'user_id' in session:
        flash('You are already signed in', 'error')
        return redirect(url_for('main.home_page'))

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        new_user, error = AuthService.signup_user(first_name, last_name, email, password)
        if error:
            flash(error, 'error')
            return render_template('signuppage.html')

        AuthService.login_user(new_user)

        flash('Account created successfully.', 'success')
        return redirect(url_for('main.home_page'))

    return render_template('signuppage.html')


@main.route('/logout')
def logout():
    AuthService.logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('main.home_page'))

# User routes
@main.route('/personalprofile', methods=['POST', 'GET'])
@AuthService.role_accepted(*user_roles.keys())
def personal_profile_page():
    current_user_id = session.get('user_id')
    user_profile = User.query.get(current_user_id)
    display_name = ''

    if user_profile:
        display_name = f'{user_profile.first_name} {user_profile.last_name}'.strip()

    if request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type == 'profile_update':
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            email = request.form.get('email', '').strip().lower()

            if first_name:
                user_profile.first_name = first_name
            if last_name:
                user_profile.last_name = last_name
            if email:
                user_profile.email = email
            db.session.commit()
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('main.personal_profile_page'))

        elif form_type == 'password_update':
            old_pwd = request.form.get('current_password', '')
            new_pwd = request.form.get('new_password', '')
            confirm_pwd = request.form.get('confirm_password', '')
            error = AuthService.change_password(current_user_id, old_pwd, new_pwd, confirm_pwd)
            if error:
                flash(error, 'error')
            else:
                flash('Password updated successfully.', 'success')
                return redirect(url_for('main.personal_profile_page'))

    listing_data = ProductQueryService.get_user_listings(
        current_user_id,
        status=request.args.get('status', 'all'),
        query=request.args.get('q', ''),
        page=request.args.get('page', 1, type=int),
        per_page=request.args.get('per_page', 4, type=int),
        sort_by=request.args.get('sort', 'posted'),
        direction=request.args.get('direction', 'desc'),
    )

    return render_template(
        'personalprofile.html',
        user=user_profile,
        username=display_name,
        user_products=listing_data['products'],
        total_listed=listing_data['summary']['total_listed'],
        active_listed=listing_data['summary']['active_listed'],
        earned_total=listing_data['summary']['earned_total'],
        total_views=listing_data['summary']['total_views'],
        filter_status=listing_data['filters']['status'],
        filter_query=listing_data['filters']['query'],
        sort_by=listing_data['filters']['sort_by'],
        sort_direction=listing_data['filters']['direction'],
        per_page=listing_data['pagination']['per_page'],
        pagination={
            'page': listing_data['pagination']['page'],
            'per_page': listing_data['pagination']['per_page'],
            'total_pages': listing_data['pagination']['total_pages'],
            'total_items': listing_data['pagination']['total_items'],
            'start_item': listing_data['pagination']['start_item'],
            'end_item': listing_data['pagination']['end_item'],
        },
        page_numbers=listing_data['pagination']['page_numbers'],
    )


@main.route('/browse', methods=['POST', 'GET'])
def browse_page():
    all_products = Product.query.order_by(Product.created_at.desc()).all()

    products = []

    for product in all_products:
        primary_image = None

        for image in product.images:
            if image.is_primary:
                primary_image = image.image_url
                break

        if not primary_image:
            primary_image = 'assets/logo/UWA_logo.webp'

        seller = getattr(product, 'seller', None)
        if seller:
            seller_name = f"{seller.first_name} {seller.last_name}".strip()
        else:
            seller_name = 'Unknown Seller'

        products.append({
            'product_id': product.product_id,
            'title': product.product_name,
            'description': product.description,
            'price': product.price,
            'location': product.location,
            'status': product.status,
            'seller_name': seller_name,
            'image': primary_image
        })

    return render_template('browse.html', products=products)


# Admin routes
@main.route('/admin')
@AuthService.role_accepted('admin')
def admin_home_page():
    admin_username = User.query.get(session.get('user_id')).first_name if session.get('user_id') else 'Swanflip'
    total_users = User.query.count()
    total_products = Product.query.count()
    reported_users = User.query.filter_by(is_report=True).count()
    pending_products = Product.query.filter_by(status='pending').count()

    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_products = Product.query.order_by(Product.created_at.desc()).limit(5).all()

    # Fetch reported users and suspicious products separately
    reported_users_list = User.query.filter_by(is_report=True).all()
    suspicious_products_list = Product.query.filter_by(is_legit=False).all()

    return render_template(
        'adminhomepage.html',
        admin_username=admin_username,
        total_users=total_users,
        total_products=total_products,
        reported_users=reported_users,
        pending_products=pending_products,
        recent_users=recent_users,
        recent_products=recent_products,
        reported_users_list=reported_users_list,
        suspicious_products_list=suspicious_products_list,
    )


@main.route('/admin/users')
@AuthService.role_accepted('admin')
def admin_users_page():
    all_users = User.query.all()
    return render_template('admin_users.html', users=all_users)


@main.route('/admin/reports')
@AuthService.role_accepted('admin')
def admin_reports_page():
    suspicious_products = Product.query.filter_by(is_legit=False).all()
    return render_template('admin_reports.html', products=suspicious_products)


