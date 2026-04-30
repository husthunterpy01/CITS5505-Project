from app.models import Product

class ProductQueryService:
    @staticmethod
    def _sortable_column(sort_by):
        sort_map = {
            'item': Product.product_name,
            'price': Product.price,
            'status': Product.status,
            'views': Product.product_id,
            'posted': Product.created_at,
        }
        return sort_map.get(sort_by, Product.created_at)
    
    @staticmethod
    def get_user_listings(user_id, status='all', query='', page=1, per_page=4, sort_by='posted', direction='desc'):
        status = (status or 'all').strip().lower()
        query = (query or '').strip()
        sort_by = (sort_by or 'posted').strip().lower()
        direction = (direction or 'desc').strip().lower()
        sort_column = ProductQueryService._sortable_column(sort_by)
        is_ascending = direction == 'asc'

        base_query = Product.query.filter_by(seller_id=user_id)
        all_products = base_query.order_by(Product.created_at.desc()).all()

        filtered_query = Product.query.filter_by(seller_id=user_id)
        if status and status != 'all':
            filtered_query = filtered_query.filter_by(status=status)
        if query:
            filtered_query = filtered_query.filter(Product.product_name.ilike(f'%{query}%'))

        if is_ascending:
            filtered_query = filtered_query.order_by(sort_column.asc(), Product.created_at.desc())
        else:
            filtered_query = filtered_query.order_by(sort_column.desc(), Product.created_at.desc())

        total_items = filtered_query.count()
        total_pages = (total_items + per_page - 1) // per_page if total_items else 0

        if total_pages and page > total_pages:
            page = total_pages
        if page < 1:
            page = 1

        offset = (page - 1) * per_page if total_items else 0
        products = filtered_query.offset(offset).limit(per_page).all()

        start_item = offset + 1 if total_items else 0
        end_item = min(offset + len(products), total_items) if total_items else 0

        page_numbers = []
        if total_pages:
            window = 2
            start_page = max(1, page - window)
            end_page = min(total_pages, page + window)

            if end_page - start_page < (window * 2):
                if start_page == 1:
                    end_page = min(total_pages, start_page + (window * 2))
                elif end_page == total_pages:
                    start_page = max(1, end_page - (window * 2))

            page_numbers = list(range(start_page, end_page + 1))

        total_listed = len(all_products)
        active_listed = sum(1 for product in all_products if product.status == 'available')
        earned_total = sum(product.price for product in all_products if product.status == 'sold')
        total_views = 0

        return {
            'products': products,
            'filters': {
                'status': status,
                'query': query,
                'sort_by': sort_by,
                'direction': direction,
            },
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'total_items': total_items,
                'start_item': start_item,
                'end_item': end_item,
                'page_numbers': page_numbers,
            },
            'summary': {
                'total_listed': total_listed,
                'active_listed': active_listed,
                'earned_total': earned_total,
                'total_views': total_views,
            },
        }