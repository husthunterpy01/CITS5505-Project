from datetime import datetime, timedelta

from flask import Blueprint, render_template, flash, request, redirect, url_for, session, jsonify, current_app
from app.extensions import db
from app.models import Product, User, Category, Location, ProductImage, Notification
from app.service.authservice import AuthService
from app.service.notificationservice import NotificationService
from app.service.productqueryservice import ProductQueryService
from app.service.productlistingservice import serialize_product_for_listing, search_products_for_listing
from app.service.geolocationservice import GeoLocationService
from app.utils import user_roles
from app.forms import CreateProductForm, SignInForm, SignUpForm
from sqlalchemy import func
import os
from uuid import uuid4
from werkzeug.utils import secure_filename
main = Blueprint('main', __name__)


def _to_public_image_url(raw_url):
    if not raw_url:
        return None
    if raw_url.startswith('http://') or raw_url.startswith('https://') or raw_url.startswith('/'):
        return raw_url
    return url_for('static', filename=raw_url)

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

    form = SignInForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data

        existing_user, error = AuthService.signin_user(email, password)
        if error:
            flash(error, 'error')
            return render_template('signinpage.html', form=form)

        AuthService.login_user(existing_user)

        flash("Login Successful", 'success')
        if existing_user.role == 'admin':
            return redirect(url_for('main.admin_home_page'))
        return redirect(url_for('main.home_page'))

    if request.method == 'POST':
        for field_errors in form.errors.values():
            for err in field_errors:
                flash(err, 'error')

    return render_template('signinpage.html', form=form)


@main.route('/signup', methods=['POST', 'GET'])
def signup_page():
    if 'user_id' in session:
        flash('You are already signed in', 'error')
        return redirect(url_for('main.home_page'))

    form = SignUpForm()
    if form.validate_on_submit():
        first_name = form.first_name.data.strip()
        last_name = form.last_name.data.strip()
        email = form.email.data.strip().lower()
        password = form.password.data

        new_user, error = AuthService.signup_user(first_name, last_name, email, password)
        if error:
            flash(error, 'error')
            return render_template('signuppage.html', form=form)

        AuthService.login_user(new_user)

        flash('Account created successfully.', 'success')
        return redirect(url_for('main.home_page'))

    if request.method == 'POST':
        for field_errors in form.errors.values():
            for err in field_errors:
                flash(err, 'error')

    return render_template('signuppage.html', form=form)


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
    categories = Category.query.order_by(Category.category_name).all()
    default_img = current_app.config['LISTING_DEFAULT_IMAGE']

    products = []

    for product in all_products:
        primary_image = None

        for image in product.images:
            if image.is_primary:
                primary_image = image.image_url
                break

        if not primary_image:
            primary_image = default_img

        seller = getattr(product, 'seller', None)
        seller_name = f"{seller.first_name} {seller.last_name}".strip() if seller else 'Unknown Seller'

        cat = getattr(product, 'category', None)
        category_name = cat.category_name if cat else ''

        image_src = _to_public_image_url(primary_image)

        products.append({
            'product_id': product.product_id,
            'title': product.product_name,
            'description': product.description,
            'category': product.category.category_name if product.category else '',
            'price': product.price,
            'category_id': product.category_id,
            'category_name': category_name,
            'location': product.location.location_name if product.location else 'Unknown Location',
            'distance_km': None,
            'status': product.status,
            'seller_id': product.seller_id,
            'seller_name': seller_name,
            'image': image_src,
        })

    return render_template('browse.html', products=products, categories=categories)


@main.route('/products/<int:product_id>')
def product_detail_page(product_id):
    product = Product.query.get_or_404(product_id)
    default_img = current_app.config['LISTING_DEFAULT_IMAGE']

    sorted_images = sorted(
        product.images,
        key=lambda image: (not bool(image.is_primary), image.image_id),
    )
    image_urls = [
        _to_public_image_url(image.image_url)
        for image in sorted_images
        if image.image_url
    ]
    if not image_urls:
        image_urls = [_to_public_image_url(default_img)]

    seller = getattr(product, 'seller', None)
    location = getattr(product, 'location', None)
    category = getattr(product, 'category', None)

    product_data = {
        'product_id': product.product_id,
        'title': product.product_name,
        'description': product.description or '',
        'price': product.price,
        'status': product.status,
        'created_at': product.created_at,
        'seller_id': product.seller_id,
        'seller_name': f"{seller.first_name} {seller.last_name}".strip() if seller else 'Unknown Seller',
        'category_name': category.category_name if category else 'Uncategorized',
        'location_name': location.location_name if location else 'Unknown Location',
        'latitude': float(location.latitude) if location else None,
        'longitude': float(location.longitude) if location else None,
        'images': image_urls,
    }

    return render_template('productdetail.html', product=product_data)


@main.route('/api/products/search', methods=['GET'])
def api_products_search():
    """Search products by text with optional category and price filters."""
    raw_q = request.args.get('q', '') or ''
    q = raw_q.strip()
    raw_category_id = (request.args.get('category_id') or '').strip()
    raw_min_price = (request.args.get('min_price') or '').strip()
    raw_max_price = (request.args.get('max_price') or '').strip()
    raw_user_location = (request.args.get('user_location') or '').strip()
    raw_distance_km = (request.args.get('distance_km') or '').strip()
    raw_user_lat = (request.args.get('user_lat') or '').strip()
    raw_user_lon = (request.args.get('user_lon') or '').strip()

    category_id = None
    min_price = None
    max_price = None
    distance_km = None

    if raw_category_id:
        try:
            category_id = int(raw_category_id)
        except ValueError:
            return jsonify({'success': False, 'message': 'category_id must be an integer.'}), 400

    if raw_min_price:
        try:
            min_price = float(raw_min_price)
        except ValueError:
            return jsonify({'success': False, 'message': 'min_price must be a number.'}), 400

    if raw_max_price:
        try:
            max_price = float(raw_max_price)
        except ValueError:
            return jsonify({'success': False, 'message': 'max_price must be a number.'}), 400

    if min_price is not None and max_price is not None and min_price > max_price:
        return jsonify({'success': False, 'message': 'min_price cannot be greater than max_price.'}), 400

    if raw_distance_km and raw_distance_km.lower() != 'any':
        try:
            distance_km = float(raw_distance_km)
        except ValueError:
            return jsonify({'success': False, 'message': 'distance_km must be a number.'}), 400
        if distance_km <= 0:
            return jsonify({'success': False, 'message': 'distance_km must be greater than 0.'}), 400

    user_coords = None
    resolved_location_name = None
    if raw_user_lat or raw_user_lon:
        if not (raw_user_lat and raw_user_lon):
            return jsonify({'success': False, 'message': 'Both user_lat and user_lon are required.'}), 400
        try:
            user_lat = float(raw_user_lat)
            user_lon = float(raw_user_lon)
        except ValueError:
            return jsonify({'success': False, 'message': 'user_lat and user_lon must be numbers.'}), 400
        user_coords = (user_lat, user_lon)
        resolved_location_name = raw_user_location or 'Current location'
    elif raw_user_location:
        resolved_location = GeoLocationService.resolve_wa_location(raw_user_location)
        if resolved_location:
            user_coords = (resolved_location['latitude'], resolved_location['longitude'])
            resolved_location_name = resolved_location['name']
        else:
            return jsonify({'success': False, 'message': 'Could not resolve that WA location. Try a nearby suburb in Western Australia.'}), 400

    if distance_km is not None and user_coords is None:
        return jsonify({'success': False, 'message': 'Please provide a location when using distance filter.'}), 400

    default_image = current_app.config.get('LISTING_DEFAULT_IMAGE', 'assets/logo/UWA_logo.webp')
    search_limit = current_app.config.get('SEARCH_RESULT_LIMIT', 200)
    rows = search_products_for_listing(
        q,
        None if user_coords else search_limit,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
    )

    if user_coords:
        user_lat, user_lon = user_coords
        with_distance = []
        for product in rows:
            item = serialize_product_for_listing(product, default_image)
            if not product.location:
                item['distance_km'] = None
                if distance_km is None:
                    with_distance.append((float('inf'), item))
                continue

            product_distance = GeoLocationService.calculate_distance(
                user_lon,
                user_lat,
                product.location.longitude,
                product.location.latitude,
            )
            item['distance_km'] = round(product_distance, 2)

            if distance_km is None or product_distance <= distance_km:
                with_distance.append((product_distance, item))

        with_distance.sort(key=lambda row: row[0])
        items = [item for _, item in with_distance[:search_limit]]
    else:
        items = [serialize_product_for_listing(p, default_image) for p in rows]

    payload = {
        'success': True,
        'query': q,
        'applied_filters': {
            'category_id': category_id,
            'min_price': min_price,
            'max_price': max_price,
            'user_location': resolved_location_name if user_coords else None,
            'distance_km': distance_km,
        },
        'products': items,
    }
    if (q or category_id is not None or min_price is not None or max_price is not None or user_coords or distance_km is not None) and not items:
        payload['message'] = 'No products matched your search.'
    return jsonify(payload)


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

    # Analytics from current database records (no synthetic data)
    utc_today = datetime.utcnow().date()
    period_start = utc_today - timedelta(days=6)

    daily_user_rows = (
        db.session.query(
            func.date(User.created_at).label('day'),
            func.count(User.user_id).label('count')
        )
        .filter(User.created_at >= datetime.combine(period_start, datetime.min.time()))
        .group_by(func.date(User.created_at))
        .all()
    )
    daily_product_rows = (
        db.session.query(
            func.date(Product.created_at).label('day'),
            func.count(Product.product_id).label('count')
        )
        .filter(Product.created_at >= datetime.combine(period_start, datetime.min.time()))
        .group_by(func.date(Product.created_at))
        .all()
    )

    daily_user_counts = {str(row.day): row.count for row in daily_user_rows}
    daily_product_counts = {str(row.day): row.count for row in daily_product_rows}

    trend_labels = []
    user_signups_last_7d = []
    product_listings_last_7d = []
    for index in range(7):
        day = period_start + timedelta(days=index)
        day_key = day.isoformat()
        trend_labels.append(day.strftime('%d %b'))
        user_signups_last_7d.append(daily_user_counts.get(day_key, 0))
        product_listings_last_7d.append(daily_product_counts.get(day_key, 0))

    product_status_rows = (
        db.session.query(
            Product.status.label('status'),
            func.count(Product.product_id).label('count')
        )
        .group_by(Product.status)
        .all()
    )
    product_status_labels = [str(row.status or 'unknown').title() for row in product_status_rows]
    product_status_values = [row.count for row in product_status_rows]

    category_rows = (
        db.session.query(
            Category.category_name.label('name'),
            func.count(Product.product_id).label('count')
        )
        .outerjoin(Product, Product.category_id == Category.category_id)
        .group_by(Category.category_id, Category.category_name)
        .order_by(func.count(Product.product_id).desc())
        .limit(6)
        .all()
    )
    category_labels = [row.name for row in category_rows]
    category_values = [row.count for row in category_rows]

    product_location_rows = (
        db.session.query(
            Location.location_name.label('name'),
            Location.latitude.label('latitude'),
            Location.longitude.label('longitude'),
            func.count(Product.product_id).label('count')
        )
        .join(Product, Product.location_id == Location.location_id)
        .group_by(Location.location_id, Location.location_name, Location.latitude, Location.longitude)
        .order_by(func.count(Product.product_id).desc())
        .all()
    )
    product_locations = [
        {
            'name': row.name,
            'latitude': float(row.latitude),
            'longitude': float(row.longitude),
            'count': row.count,
        }
        for row in product_location_rows
    ]

    admin_chart_data = {
        'trend': {
            'labels': trend_labels,
            'users': user_signups_last_7d,
            'products': product_listings_last_7d,
        },
        'product_status': {
            'labels': product_status_labels,
            'values': product_status_values,
        },
        'top_categories': {
            'labels': category_labels,
            'values': category_values,
        },
        'product_locations': product_locations,
    }

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
        admin_chart_data=admin_chart_data,
    )


@main.route('/admin/users', methods=['GET', 'POST'])
@AuthService.role_accepted('admin')
def admin_users_page():
    if request.method == 'POST':
        payload = request.get_json(silent=True) or request.form
        action = (payload.get('action') or '').strip().lower()
        raw_user_id = payload.get('user_id')
        reason = (payload.get('reason') or '').strip()

        if not action or not raw_user_id:
            return jsonify({'ok': False, 'message': 'Missing action or user_id.'}), 400

        try:
            user_id = int(raw_user_id)
        except (TypeError, ValueError):
            return jsonify({'ok': False, 'message': 'Invalid user_id.'}), 400

        target_user = User.query.get(user_id)
        if not target_user:
            return jsonify({'ok': False, 'message': 'User not found.'}), 404

        if target_user.role == 'admin' and action == 'report':
            return jsonify({'ok': False, 'message': 'Admin users cannot be reported.'}), 400

        created_notification = None
        if action in ('report', 'ban'):
            if not reason:
                return jsonify({'ok': False, 'message': 'Report reason is required.'}), 400
            target_user.is_report = True
            target_user.review = reason
            created_notification = NotificationService.create_notification(
                recipient_id=target_user.user_id,
                notification_type='user_banned',
                title='Account restricted by admin',
                message=f'Your account was restricted by an admin. Reason: {reason}',
                action_url=url_for('main.personal_profile_page'),
                reference_type='user',
                reference_id=target_user.user_id,
                commit=False,
            )
        elif action in ('unreport', 'unban'):
            target_user.is_report = False
        else:
            return jsonify({'ok': False, 'message': 'Unsupported action.'}), 400

        db.session.commit()
        if created_notification:
            NotificationService.emit_notification(created_notification)
        return jsonify({
            'ok': True,
            'message': f"{target_user.first_name} {target_user.last_name} updated successfully.",
            'is_report': target_user.is_report,
        })

    all_users = User.query.all()
    return render_template('usermanager.html', users=all_users)


@main.route('/admin/reports', methods=['GET', 'POST'])
@AuthService.role_accepted('admin')
def admin_reports_page():
    if request.method == 'POST':
        payload = request.get_json(silent=True) or request.form
        action = (payload.get('action') or '').strip().lower()
        raw_product_id = payload.get('product_id')
        reason = (payload.get('reason') or '').strip()

        if not action or not raw_product_id:
            return jsonify({'ok': False, 'message': 'Missing action or product_id.'}), 400

        try:
            product_id = int(raw_product_id)
        except (TypeError, ValueError):
            return jsonify({'ok': False, 'message': 'Invalid product_id.'}), 400

        target_product = Product.query.get(product_id)
        if not target_product:
            return jsonify({'ok': False, 'message': 'Product not found.'}), 404

        # Do not allow moderation actions on sold products
        if getattr(target_product, 'status', '') == 'sold':
            return jsonify({'ok': False, 'message': 'Cannot moderate a sold product.'}), 400

        created_notification = None
        if action == 'approve':
            target_product.is_legit = True
            # clear previous review when approving
            target_product.review = None
        elif action == 'flag':
            if not reason:
                return jsonify({'ok': False, 'message': 'Reason is required when flagging a post.'}), 400
            target_product.is_legit = False
            target_product.review = reason
            created_notification = NotificationService.create_notification(
                recipient_id=target_product.seller_id,
                notification_type='post_banned',
                title='Your post was flagged by admin',
                message=f'"{target_product.product_name}" was flagged by admin. Reason: {reason}',
                action_url=url_for('main.personal_profile_page'),
                reference_type='product',
                reference_id=target_product.product_id,
                commit=False,
            )
        else:
            return jsonify({'ok': False, 'message': 'Unsupported action.'}), 400

        db.session.commit()
        if created_notification:
            NotificationService.emit_notification(created_notification)
        return jsonify({
            'ok': True,
            'message': f"{target_product.product_name} updated successfully.",
            'is_legit': target_product.is_legit,
        })

    # Normalize legacy rows so legitimacy always has an explicit value.
    unknown_legit_products = Product.query.filter(Product.is_legit.is_(None)).all()
    if unknown_legit_products:
        for product in unknown_legit_products:
            product.is_legit = True
        db.session.commit()

    all_products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('postmanager.html', products=all_products)


@main.route('/notifications/mark-read', methods=['POST'])
@AuthService.role_accepted(*user_roles.keys())
def mark_notification_read():
    current_user_id = session.get('user_id')
    payload = request.get_json(silent=True) or request.form
    raw_notification_id = payload.get('notification_id')

    if raw_notification_id in (None, ''):
        NotificationService.mark_all_read(current_user_id)
        return jsonify({'ok': True, 'message': 'All notifications marked as read.'})

    try:
        notification_id = int(raw_notification_id)
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'message': 'Invalid notification_id.'}), 400

    notification = Notification.query.filter_by(
        notification_id=notification_id,
        recipient_id=current_user_id,
    ).first()
    if not notification:
        return jsonify({'ok': False, 'message': 'Notification not found.'}), 404

    if not notification.is_read:
        notification.is_read = True
        db.session.commit()

    return jsonify({'ok': True, 'message': 'Notification marked as read.'})

def save_product_images(product, uploaded_images):
    upload_dir = os.path.join(current_app.static_folder, 'uploads', 'products')
    os.makedirs(upload_dir, exist_ok=True)

    has_primary = any(image.is_primary for image in product.images)

    for index, image_file in enumerate(uploaded_images):
        filename = secure_filename(image_file.filename)
        unique_filename = f"{uuid4().hex}_{filename}"
        file_path = os.path.join(upload_dir, unique_filename)
        image_file.save(file_path)

        image_url = url_for('static', filename=f'uploads/products/{unique_filename}')

        product_image = ProductImage(
            product_id=product.product_id,
            image_url=image_url,
            is_primary=(not has_primary and index == 0),
        )
        db.session.add(product_image)


@main.route('/createProduct', methods=['GET', 'POST'])
@AuthService.role_accepted('standard_user')
def create_product_page():
    form = CreateProductForm()

    form.category_id.choices = [
        (category.category_id, category.category_name)
        for category in Category.query.order_by(Category.category_name.asc()).all()
    ]

    if form.validate_on_submit():  
        uploaded_images = [file for file in (form.images.data or []) if file and file.filename]

        location_name = form.location_name.data.strip()
        resolved_location = GeoLocationService.resolve_wa_location(location_name)

        if not resolved_location:
            flash('Please enter a valid WA suburb.', 'error')
            return render_template('createproduct.html', form=form)

        location_name = resolved_location['name']
        location = Location.query.filter(Location.location_name.ilike(location_name)).first()

        if not location:
            location = Location(
                location_name = location_name,
                latitude = resolved_location['latitude'],
                longitude = resolved_location['longitude'],
            )
            db.session.add(location)
            db.session.flush()

        new_product = Product(
            product_name=form.product_name.data.strip(),
            description=form.description.data.strip() if form.description.data else None,
            seller_id=session.get('user_id'),
            category_id=form.category_id.data,
            price=float(form.price.data),
            location_id=location.location_id,
            status='available',
            is_legit=True,
        )

        db.session.add(new_product)
        db.session.flush()
        
        save_product_images(new_product, uploaded_images)

        db.session.commit()

        flash('Your listing has been created.', 'success')
        return redirect(url_for('main.browse_page'))

    return render_template('createproduct.html', form=form)

@main.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@AuthService.role_accepted('standard_user')
def edit_product_page(product_id):
    product = Product.query.get_or_404(product_id)

    if product.seller_id != session.get('user_id'):
        flash('You do not have permission to edit this listing.', 'error')
        return redirect(url_for('main.personal_profile_page'))

    form = CreateProductForm()
    form.submit.label.text = 'Update Listing'

    form.category_id.choices = [
        (category.category_id, category.category_name)
        for category in Category.query.order_by(Category.category_name.asc()).all()
    ]

    if request.method == 'GET':
        form.product_name.data = product.product_name
        form.description.data = product.description
        form.price.data = product.price
        form.category_id.data = product.category_id

        if product.location:
            form.location_name.data = product.location.location_name
            form.latitude.data = str(product.location.latitude)
            form.longitude.data = str(product.location.longitude)

    if form.validate_on_submit():
        delete_image_ids = request.form.getlist('delete_image_ids')
        delete_image_ids = [int(image_id) for image_id in delete_image_ids if image_id.isdigit()]

        existing_images_after_delete = [
            image for image in product.images
            if image.image_id not in delete_image_ids
        ]

        uploaded_images = [file for file in (form.images.data or []) if file and file.filename]

        if len(existing_images_after_delete) + len(uploaded_images) == 0:
            flash('A product must have at least one image.', 'error')
            return render_template('updateproduct.html', form=form, product=product)

        if len(existing_images_after_delete) + len(uploaded_images) > 10:
            flash('A product can have a maximum of 10 images.', 'error')
            return render_template('updateproduct.html', form=form, product=product)

        location_name = form.location_name.data.strip()
        resolved_location = GeoLocationService.resolve_wa_location(location_name)

        if not resolved_location:
            flash('Please enter a valid WA suburb.', 'error')
            return render_template('updateproduct.html', form=form, product=product)

        location_name = resolved_location['name']
        location = Location.query.filter(Location.location_name.ilike(location_name)).first()

        if not location:
            location = Location(
                location_name=location_name,
                latitude=resolved_location['latitude'],
                longitude=resolved_location['longitude'],
            )
            db.session.add(location)
            db.session.flush()

        product.product_name = form.product_name.data.strip()
        product.description = form.description.data.strip() if form.description.data else None
        product.category_id = form.category_id.data
        product.price = float(form.price.data)
        product.location_id = location.location_id

        if delete_image_ids:
            ProductImage.query.filter(
                ProductImage.product_id == product.product_id,
                ProductImage.image_id.in_(delete_image_ids),
            ).delete(synchronize_session=False)

        db.session.flush()
        save_product_images(product, uploaded_images)

        remaining_images = ProductImage.query.filter_by(product_id=product.product_id).all()
        if remaining_images and not any(image.is_primary for image in remaining_images):
            remaining_images[0].is_primary = True

        db.session.commit()

        flash('Your listing has been updated.', 'success')
        return redirect(url_for('main.personal_profile_page'))

    return render_template('updateproduct.html', form=form, product=product)


@main.route('/products/<int:product_id>/delete', methods=['POST'])
@AuthService.role_accepted('standard_user')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.seller_id != session.get('user_id'):
        flash('You do not have permission to delete this listing.', 'error')
        return redirect(url_for('main.personal_profile_page'))

    ProductImage.query.filter(ProductImage.product_id == product.product_id).delete(synchronize_session=False)
    from app.models import Conversation
    Conversation.query.filter(Conversation.product_id == product.product_id).update({'product_id': None}, synchronize_session=False)

    db.session.delete(product)
    db.session.commit()

    flash('Product deleted successfully.', 'success')
    return redirect(url_for('main.personal_profile_page'))


@main.route('/api/locations/suggest')
def suggest_locations():
    query = request.args.get('q', '').strip()
    
    if len(query) < 3:
        return jsonify({'ok': True, 'locations': []})
    
    api_key = current_app.config.get('GEOAPIFY_API_KEY')
    if not api_key:
        return jsonify({'ok': False, 'message': 'Geoapify API key is missing'}), 500

    locations = GeoLocationService.suggest_wa_locations(query)

    return jsonify({'ok': True, 'locations': locations})