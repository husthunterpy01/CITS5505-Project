from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from app.models import Product


user_roles = {
    'admin':0,
    'user':1,
}
