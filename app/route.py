from flask import Blueprint, render_template, flash, request, redirect, url_for, session, jsonify
from app.extensions import db
from app.models import Product, User, Category, Location, ProductImage
from app.service.authservice import AuthService
from app.service.productqueryservice import ProductQueryService
from app.utils import user_roles
from app.forms import CreateProductForm
import os
from uuid import uuid4
from werkzeug.utils import secure_filename
from flask import current_app
import json
import urllib.parse
import urllib.request

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
        terms_accepted = request.form.get('terms_accepted') == 'on'

        if not terms_accepted:
            flash('Please agree to the Terms of Service and Privacy Policy before signing up.', 'error')
            return render_template('signuppage.html')

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
            'location': product.location.location_name if product.location else 'Unknown Location',
            'status': product.status,
            'seller_name': seller_name,
            'image': primary_image
        })

    return render_template('browse.html', products=products)


@main.route('/api/products/search', methods=['GET'])
def api_products_search():
    """Search products by text with optional category and price filters."""
    raw_q = request.args.get('q', '') or ''
    q = raw_q.strip()
    raw_category_id = (request.args.get('category_id') or '').strip()
    raw_min_price = (request.args.get('min_price') or '').strip()
    raw_max_price = (request.args.get('max_price') or '').strip()

    category_id = None
    min_price = None
    max_price = None

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

    default_image = current_app.config.get('LISTING_DEFAULT_IMAGE', 'assets/logo/UWA_logo.webp')
    search_limit = current_app.config.get('SEARCH_RESULT_LIMIT', 200)
    rows = search_products_for_listing(
        q,
        search_limit,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
    )
    items = [serialize_product_for_listing(p, default_image) for p in rows]
    payload = {
        'success': True,
        'query': q,
        'applied_filters': {
            'category_id': category_id,
            'min_price': min_price,
            'max_price': max_price,
        },
        'products': items,
    }
    if (q or category_id is not None or min_price is not None or max_price is not None) and not items:
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

        if action == 'report':
            if not reason:
                return jsonify({'ok': False, 'message': 'Report reason is required.'}), 400
            target_user.is_report = True
            target_user.review = reason
        elif action == 'unreport':
            target_user.is_report = False
        else:
            return jsonify({'ok': False, 'message': 'Unsupported action.'}), 400

        db.session.commit()
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

        if action == 'approve':
            target_product.is_legit = True
            # clear previous review when approving
            target_product.review = None
        elif action == 'flag':
            if not reason:
                return jsonify({'ok': False, 'message': 'Reason is required when flagging a post.'}), 400
            target_product.is_legit = False
            target_product.review = reason
        else:
            return jsonify({'ok': False, 'message': 'Unsupported action.'}), 400

        db.session.commit()
        return jsonify({
            'ok': True,
            'message': f"{target_product.product_name} updated successfully.",
            'is_legit': target_product.is_legit,
        })

    all_products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('postmanager.html', products=all_products)

@main.route('/createProduct', methods=['GET', 'POST'])
@AuthService.role_accepted('standard_user')
def create_product_page():
    form = CreateProductForm()

    form.category_id.choices = [
        (category.category_id, category.category_name)
        for category in Category.query.order_by(Category.category_name.asc()).all()
    ]

    if form.validate_on_submit():  
        uploaded_images = [file for file in form.images.data if file and file.filename]

        location_name = form.location_name.data.strip()
        latitude = float(form.latitude.data)
        longitude = float(form.longitude.data)

        location = Location.query.filter(Location.location_name.ilike(location_name)).first()

        if not location: 
            location = Location(
                location_name = location_name,
                latitude = latitude,
                longitude = longitude,
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
        
        upload_dir = os.path.join(current_app.static_folder, 'uploads', 'products')
        os.makedirs(upload_dir, exist_ok=True)

        for index, image_file in enumerate(uploaded_images):
            filename = secure_filename(image_file.filename)
            unique_filename = f"{uuid4().hex}_{filename}"
            file_path = os.path.join(upload_dir, unique_filename)
            image_file.save(file_path)

            image_url = url_for('static', filename=f'uploads/products/{unique_filename}')

            product_image = ProductImage(
                product_id=new_product.product_id,
                image_url=image_url,
                is_primary=(index == 0),
            )
            db.session.add(product_image)

        db.session.commit()

        flash('Your listing has been created.', 'success')
        return redirect(url_for('main.browse_page'))

    return render_template('createproduct.html', form=form)

@main.route('/api/locations/suggest')
def suggest_locations():
    query = request.args.get('q', '').strip()
    
    if len(query) < 3:
        return jsonify({'ok': True, 'locations': []})
    
    api_key = current_app.config.get('GEOAPIFY_API_KEY')
    if not api_key:
        return jsonify({'ok': False, 'message': 'Geoapify API key is missing'}), 500
    
    params = {
        'text': query,
        'type': 'locality',
        'filter': 'rect:112.8,-35.2,129.1,-13.4',
        'limit': 5,
        'format': 'json',
        'apiKey': api_key
    }

    url = 'https://api.geoapify.com/v1/geocode/autocomplete?' + urllib.parse.urlencode(params)

    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            payload = json.loads(response.read().decode('utf-8'))
    except Exception:
        return jsonify({'ok': False, 'message': 'Location lookup failed'}), 502
    
    locations = []
    seen = set()

    for result in payload.get('results', []):
        suburb = result.get('suburb') or result.get('city') or result.get('name')
        state = result.get('state')
        country = result.get('country_code')
        lat = result.get('lat')
        lon = result.get('lon')

        if not suburb or lat is None or lon is None:
            continue

        if country and country.lower() != 'au':
            continue

        key = suburb.strip().lower()
        if key in seen:
            continue

        seen.add(key)
        locations.append({
            'name': suburb,
            'state': state,
            'latitude': lat,
            'longitude': lon,
            'label': f"{suburb}, {state}" if state else suburb,
        })

    return jsonify({'ok': True, 'locations': locations})