import sqlalchemy as sa
from sqlalchemy import asc, desc, func
from app.models import Product
from app.extensions import db

class ProductQueryService:

    SORT_MAP = {
        'item':   Product.product_name,
        'price':  Product.price,
        'status': Product.status,
        'views':  Product.product_id,
        'posted': Product.created_at,
    }

    PAGE_WINDOW = 2
    MAX_PER_PAGE = 100
    DEFAULT_PER_PAGE = 4

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