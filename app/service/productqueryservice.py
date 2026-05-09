import sqlalchemy as sa
from sqlalchemy import asc, desc, func
from sqlalchemy.orm import joinedload
from app.models import Product
from app.extensions import db
from app.service.geolocationservice import GeoLocationService


class ProductQueryService:
    PAGE_WINDOW = 2
    MAX_PER_PAGE = 100
    DEFAULT_PER_PAGE = 4

    SORT_MAP = {
        'item':   Product.product_name,
        'price':  Product.price,
        'status': Product.status,
        'posted': Product.created_at,
    }

    @classmethod
    def _sortable_column(cls, sort_by):
        return cls.SORT_MAP.get(sort_by, Product.created_at)

    @staticmethod
    def _parse_int(value, default, min_val=1, max_val=None):
        try:
            result = int(value) if value is not None else default
        except (ValueError, TypeError):
            result = default
        result = max(min_val, result)
        if max_val is not None:
            result = min(max_val, result)
        return result

    @classmethod
    def _build_page_numbers(cls, page, total_pages):
        if not total_pages:
            return []
        start = max(1, page - cls.PAGE_WINDOW)
        end   = min(total_pages, page + cls.PAGE_WINDOW)

        # Expand window if near the edges
        if end - start < cls.PAGE_WINDOW * 2:
            if start == 1:
                end = min(total_pages, start + cls.PAGE_WINDOW * 2)
            elif end == total_pages:
                start = max(1, end - cls.PAGE_WINDOW * 2)

        return list(range(start, end + 1))

    @classmethod
    def get_user_listings(
        cls,
        user_id,
        status='all',
        query='',
        page=1,
        per_page=DEFAULT_PER_PAGE,
        sort_by='posted',
        direction='desc',
    ):
        status    = (status    or 'all').strip().lower()
        query     = (query     or '').strip()
        sort_by   = (sort_by   or 'posted').strip().lower()
        direction = (direction or 'desc').strip().lower()
        per_page  = cls._parse_int(per_page, cls.DEFAULT_PER_PAGE, 1, cls.MAX_PER_PAGE)
        page      = cls._parse_int(page, 1, 1)

        stats = db.session.query(
            func.count(Product.product_id).label('total_listed'),  
            func.sum(sa.case((Product.status == 'available', 1), else_=0)).label('active_listed'),  
            func.coalesce(
                func.sum(sa.case((Product.status == 'sold', Product.price), else_=None)), 0 
            ).label('earned_total'),
        ).filter(Product.seller_id == user_id).one()

        sort_col   = cls._sortable_column(sort_by)
        order_dir  = asc if direction == 'asc' else desc
        base       = Product.query.filter(Product.seller_id == user_id)

        if status != 'all':
            base = base.filter(Product.status == status)
        if query:
            base = base.filter(Product.product_name.ilike(f'%{query}%'))

        base = base.order_by(order_dir(sort_col), desc(Product.created_at))

        total_items = base.count()
        total_pages = -(-total_items // per_page) if total_items else 0  # ceiling div
        page        = min(page, total_pages) if total_pages else 1

        offset   = (page - 1) * per_page if total_items else 0
        products = base.offset(offset).limit(per_page).all()

        start_item = offset + 1 if total_items else 0
        end_item   = offset + len(products) if total_items else 0

        return {
            'products': products,
            'filters': {
                'status':    status,
                'query':     query,
                'sort_by':   sort_by,
                'direction': direction,
            },
            'pagination': {
                'page':         page,
                'per_page':     per_page,
                'total_pages':  total_pages,
                'total_items':  total_items,
                'start_item':   start_item,
                'end_item':     end_item,
                'page_numbers': cls._build_page_numbers(page, total_pages),
                'has_prev':     page > 1,
                'has_next':     page < total_pages,
            },
            'summary': {
                'total_listed':  stats.total_listed  or 0,
                'active_listed': stats.active_listed or 0,
                'earned_total':  float(stats.earned_total or 0),
                'total_views':   0,
            },
        }

    @classmethod
    def get_browse_products(cls, sort_by='posted', direction='desc'):
        sort_by = (sort_by or 'posted').strip().lower()
        direction = (direction or 'desc').strip().lower()

        sort_col = cls._sortable_column(sort_by)
        order_dir = asc if direction == 'asc' else desc

        products = Product.query.options(
            joinedload(Product.images),
            joinedload(Product.seller),
            joinedload(Product.location),
        ).order_by(order_dir(sort_col), desc(Product.created_at)).all()

        product_cards = []
        for product in products:
            primary_image = next((img.image_url for img in product.images if img.is_primary), 'assets/logo/UWA_logo.webp')

            seller = getattr(product, 'seller', None)
            seller_name = f"{seller.first_name} {seller.last_name}".strip() if seller else 'Unknown Seller'

            product_cards.append({
                'product_id': product.product_id,
                'title': product.product_name,
                'description': product.description,
                'price': product.price,
                'location': product.location.location_name if product.location else 'Unknown Location',
                'location_latitude': product.location.latitude if product.location else None,
                'location_longitude': product.location.longitude if product.location else None,
                'status': product.status,
                'seller_name': seller_name,
                'image': primary_image,
                'distance_km': None,
                'distance_band': None,
            })

        return {
            'products': product_cards,
            'filters': {
                'sort_by': sort_by,
                'direction': direction,
            },
            'location_search': {
                'query': '',
                'resolved': False,
                'latitude': None,
                'longitude': None,
                'error': None,
            },
            'distance_summary': {
                'within_5_km': 0,
                'within_10_km': 0,
                'over_15_km': 0,
            },
        }

    @classmethod
    def get_browse_products_with_distance(cls, sort_by='posted', direction='desc', user_location=''):
        data = cls.get_browse_products(sort_by=sort_by, direction=direction)

        query = (user_location or '').strip()
        data['location_search']['query'] = query
        if not query:
            return data

        geocode_map = GeoLocationService.geocode_batch([query])
        coords = geocode_map.get(query)
        if not coords and geocode_map:
            coords = next(iter(geocode_map.values()))

        if not coords:
            data['location_search']['error'] = 'Could not resolve your location. Try suburb/city with state.'
            return data

        user_lon = coords['longitude']
        user_lat = coords['latitude']
        data['location_search'].update({
            'resolved': True,
            'latitude': user_lat,
            'longitude': user_lon,
        })

        within_5 = 0
        within_10 = 0
        over_15 = 0

        for card in data['products']:
            location_lon = card.get('location_longitude')
            location_lat = card.get('location_latitude')
            if location_lon is None or location_lat is None:
                continue

            distance_km = GeoLocationService.calculate_distance(
                user_lon,
                user_lat,
                location_lon,
                location_lat,
            )
            card['distance_km'] = round(distance_km, 2)

            if distance_km <= 5:
                card['distance_band'] = '5 km'
                within_5 += 1
            elif distance_km <= 10:
                card['distance_band'] = '10 km'
                within_10 += 1
            elif distance_km > 15:
                card['distance_band'] = '15+ km'
                over_15 += 1
            else:
                card['distance_band'] = '10-15 km'

        data['distance_summary'] = {
            'within_5_km': within_5,
            'within_10_km': within_10,
            'over_15_km': over_15,
        }
        return data
