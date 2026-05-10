from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from app.models import Product


user_roles = {
    'admin': 0,
    'user': 1,
}


def products_listing_query():
    return (
        Product.query.options(
            joinedload(Product.seller),
            joinedload(Product.images),
            joinedload(Product.location),
            joinedload(Product.category),
        )
        .order_by(Product.created_at.desc())
    )


def primary_image_for_product(product, default_image):
    for image in product.images:
        if image.is_primary:
            return image.image_url
    return default_image


def serialize_product_for_listing(product, default_image):
    loc = product.location
    cat = product.category
    return {
        'product_id': product.product_id,
        'title': product.product_name,
        'description': product.description or '',
        'price': product.price,
        'category_id': product.category_id,
        'category_name': cat.category_name if cat else None,
        'location': loc.location_name if loc else None,
        'status': product.status,
        'seller_name': f'{product.seller.first_name} {product.seller.last_name}',
        'image': primary_image_for_product(product, default_image),
    }


def search_products_for_listing(query, limit, category_id=None, min_price=None, max_price=None):
    base = products_listing_query()

    if query:
        pattern = f'%{query}%'
        base = base.filter(
            or_(
                Product.product_name.ilike(pattern),
                Product.description.ilike(pattern),
            )
        )

    if category_id is not None:
        base = base.filter(Product.category_id == category_id)

    if min_price is not None:
        base = base.filter(Product.price >= min_price)

    if max_price is not None:
        base = base.filter(Product.price <= max_price)

    return base.limit(limit).all()
