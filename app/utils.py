from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from app.models import Product


user_roles = {
    'admin': 0,
    'normal': 1,
}


def products_listing_query():
    return (
        Product.query.options(
            joinedload(Product.seller),
            joinedload(Product.images),
        )
        .order_by(Product.created_at.desc())
    )


def primary_image_for_product(product, default_image):
    for image in product.images:
        if image.is_primary:
            return image.image_url
    return default_image


def serialize_product_for_listing(product, default_image):
    return {
        'product_id': product.product_id,
        'title': product.product_name,
        'description': product.description or '',
        'price': product.price,
        'location': product.location,
        'status': product.status,
        'seller_name': f'{product.seller.first_name} {product.seller.last_name}',
        'image': primary_image_for_product(product, default_image),
    }


def search_products_for_listing(query, limit):
    base = products_listing_query()
    if not query:
        return base.limit(limit).all()

    pattern = f'%{query}%'
    return (
        base.filter(
            or_(
                Product.product_name.ilike(pattern),
                Product.description.ilike(pattern),
            )
        )
        .limit(limit)
        .all()
    )