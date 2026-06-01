from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


# ──────────────────────────── 1. Користувачі ────────────────────────────

class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String, nullable=False, index=True)
    phone           = Column(String, nullable=False, index=True)
    email           = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active       = Column(Integer, default=1)
    is_admin        = Column(Integer, default=0)
    avatar_url      = Column(String)
    created_at      = Column(DateTime, server_default=func.now())

    # Зв'язки
    orders       = relationship("Order",                 back_populates="user")
    cart_items   = relationship("CartItem",              back_populates="user", cascade="all, delete-orphan")
    rentals      = relationship("Rental",                back_populates="user")
    reviews      = relationship("Review",                back_populates="user")
    wishlist     = relationship("WishlistItem",          back_populates="user", cascade="all, delete-orphan")
    customizations = relationship("CustomizationRequest", back_populates="user")


# ──────────────────────────── 2. Категорії ──────────────────────────────

class Category(Base):
    __tablename__ = "categories"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String, unique=True, nullable=False)
    slug        = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text)
    parent_id   = Column(Integer)
    image_url   = Column(String)
    sort_order  = Column(Integer, default=0)
    created_at  = Column(DateTime, server_default=func.now())

    products    = relationship("Product", back_populates="category_rel")


# ──────────────────────────── 3. Товари ─────────────────────────────────

class Product(Base):
    __tablename__ = "products"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String, nullable=False, index=True)
    category     = Column(String, index=True)          # текстова категорія (legacy)
    category_id  = Column(Integer)
    description  = Column(Text)
    price        = Column(Float, nullable=False, default=0)
    old_price    = Column(Float)
    image_url    = Column(String)
    stock        = Column(Integer, default=0)
    specs        = Column(Text)                        # JSON
    is_available = Column(Integer, default=1)
    is_rental    = Column(Integer, default=0)
    rental_price = Column(Float)
    created_at   = Column(DateTime, server_default=func.now())
    updated_at   = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Зв'язки
    category_rel = relationship("Category",     back_populates="products",
                                foreign_keys=[category_id],
                                primaryjoin="Product.category_id == Category.id")
    images       = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    order_items  = relationship("OrderItem",    back_populates="product")
    reviews      = relationship("Review",       back_populates="product", cascade="all, delete-orphan")


# ──────────────────────────── 4. Зображення товарів ─────────────────────

class ProductImage(Base):
    __tablename__ = "product_images"

    id         = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    image_url  = Column(String, nullable=False)
    sort_order = Column(Integer, default=0)

    product    = relationship("Product", back_populates="images",
                              foreign_keys=[product_id],
                              primaryjoin="ProductImage.product_id == Product.id")


# ──────────────────────────── 5. Замовлення ─────────────────────────────

class Order(Base):
    __tablename__ = "orders"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, index=True)
    order_number    = Column(String, unique=True, nullable=False, index=True)
    status          = Column(String, default="pending")        # pending | confirmed | processing | shipped | delivered | cancelled
    total_amount    = Column(Float, default=0)
    delivery_cost   = Column(Float, default=0)
    discount_amount = Column(Float, default=0)

    customer_name   = Column(String, nullable=False)
    customer_email  = Column(String, nullable=False)
    customer_phone  = Column(String, nullable=False)

    address         = Column(String)
    apartment       = Column(String)
    postcode        = Column(String)
    location_lat    = Column(Float)
    location_lng    = Column(Float)
    branch_name     = Column(String)

    payment_method  = Column(String, default="cash")           # card | transfer | cash | crypto
    payment_status  = Column(String, default="pending")        # pending | paid | failed | refunded
    promo_code      = Column(String)
    notes           = Column(Text)
    created_at      = Column(DateTime, server_default=func.now())
    updated_at      = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Зв'язки
    user  = relationship("User",      back_populates="orders",
                         foreign_keys=[user_id],
                         primaryjoin="Order.user_id == User.id")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


# ──────────────────────────── 6. Позиції замовлення ─────────────────────

class OrderItem(Base):
    __tablename__ = "order_items"

    id           = Column(Integer, primary_key=True, index=True)
    order_id     = Column(Integer, nullable=False, index=True)
    product_id   = Column(Integer, index=True)
    product_name = Column(String, nullable=False)
    quantity     = Column(Integer, default=1)
    unit_price   = Column(Float, nullable=False)
    total_price  = Column(Float, nullable=False)

    order   = relationship("Order",   back_populates="items",
                           foreign_keys=[order_id],
                           primaryjoin="OrderItem.order_id == Order.id")
    product = relationship("Product", back_populates="order_items",
                           foreign_keys=[product_id],
                           primaryjoin="OrderItem.product_id == Product.id")


# ──────────────────────────── 7. Кошик ──────────────────────────────────

class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (UniqueConstraint("user_id", "product_id"),)

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, nullable=False)
    quantity   = Column(Integer, default=1)
    added_at   = Column(DateTime, server_default=func.now())

    user    = relationship("User", back_populates="cart_items",
                           foreign_keys=[user_id],
                           primaryjoin="CartItem.user_id == User.id")
    product = relationship("Product",
                           foreign_keys=[product_id],
                           primaryjoin="CartItem.product_id == Product.id")


# ──────────────────────────── 8. Оренда ─────────────────────────────────

class Rental(Base):
    __tablename__ = "rentals"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, nullable=False, index=True)
    product_id  = Column(Integer, nullable=False, index=True)
    status      = Column(String, default="pending")            # pending | active | returned | overdue | cancelled
    start_date  = Column(String, nullable=False)
    end_date    = Column(String, nullable=False)
    daily_rate  = Column(Float, nullable=False)
    total_cost  = Column(Float, nullable=False)
    deposit     = Column(Float, default=0)
    return_date = Column(String)
    notes       = Column(Text)
    created_at  = Column(DateTime, server_default=func.now())

    user    = relationship("User",    back_populates="rentals",
                           foreign_keys=[user_id],
                           primaryjoin="Rental.user_id == User.id")
    product = relationship("Product",
                           foreign_keys=[product_id],
                           primaryjoin="Rental.product_id == Product.id")


# ──────────────────────────── 9. Промокоди ──────────────────────────────

class Promocode(Base):
    __tablename__ = "promocodes"

    id               = Column(Integer, primary_key=True, index=True)
    code             = Column(String, unique=True, nullable=False, index=True)
    discount_percent = Column(Float, default=0)
    discount_amount  = Column(Float, default=0)
    min_order_amount = Column(Float, default=0)
    max_uses         = Column(Integer, default=0)          # 0 = безліміт
    used_count       = Column(Integer, default=0)
    is_active        = Column(Integer, default=1)
    valid_from       = Column(DateTime, server_default=func.now())
    valid_until      = Column(DateTime)
    created_at       = Column(DateTime, server_default=func.now())

    usages = relationship("PromocodeUsage", back_populates="promocode", cascade="all, delete-orphan")


# ──────────────────────────── 10. Використання промокодів ───────────────

class PromocodeUsage(Base):
    __tablename__ = "promocode_usages"

    id           = Column(Integer, primary_key=True, index=True)
    promocode_id = Column(Integer, nullable=False, index=True)
    user_id      = Column(Integer, nullable=False, index=True)
    order_id     = Column(Integer)
    used_at      = Column(DateTime, server_default=func.now())

    promocode = relationship("Promocode", back_populates="usages",
                             foreign_keys=[promocode_id],
                             primaryjoin="PromocodeUsage.promocode_id == Promocode.id")


# ──────────────────────────── 11. Кастомізація ──────────────────────────

class CustomizationRequest(Base):
    __tablename__ = "customization_requests"

    id             = Column(Integer, primary_key=True, index=True)
    user_id        = Column(Integer, index=True)
    status         = Column(String, default="pending")     # pending | in_review | approved | in_progress | completed | cancelled
    cpu            = Column(String)
    gpu            = Column(String)
    ram            = Column(String)
    storage        = Column(String)
    case_type      = Column(String)
    cooling        = Column(String)
    power_supply   = Column(String)
    extras         = Column(Text)                          # JSON
    total_estimate = Column(Float)
    customer_name  = Column(String)
    customer_email = Column(String)
    customer_phone = Column(String)
    notes          = Column(Text)
    admin_comment  = Column(Text)
    created_at     = Column(DateTime, server_default=func.now())
    updated_at     = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="customizations",
                        foreign_keys=[user_id],
                        primaryjoin="CustomizationRequest.user_id == User.id")


# ──────────────────────────── 12. Новини ────────────────────────────────

class News(Base):
    __tablename__ = "news"

    id           = Column(Integer, primary_key=True, index=True)
    title        = Column(String, nullable=False)
    slug         = Column(String, unique=True, nullable=False, index=True)
    content      = Column(Text, nullable=False)
    excerpt      = Column(Text)
    image_url    = Column(String)
    author_id    = Column(Integer)
    is_published = Column(Integer, default=0)
    views_count  = Column(Integer, default=0)
    published_at = Column(DateTime)
    created_at   = Column(DateTime, server_default=func.now())
    updated_at   = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ──────────────────────────── 13. Відгуки ───────────────────────────────

class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("product_id", "user_id"),
        CheckConstraint("rating BETWEEN 1 AND 5", name="check_rating_range"),
    )

    id          = Column(Integer, primary_key=True, index=True)
    product_id  = Column(Integer, nullable=False, index=True)
    user_id     = Column(Integer, nullable=False, index=True)
    rating      = Column(Integer, nullable=False)
    comment     = Column(Text)
    is_approved = Column(Integer, default=0)
    created_at  = Column(DateTime, server_default=func.now())

    product = relationship("Product", back_populates="reviews",
                           foreign_keys=[product_id],
                           primaryjoin="Review.product_id == Product.id")
    user    = relationship("User",    back_populates="reviews",
                           foreign_keys=[user_id],
                           primaryjoin="Review.user_id == User.id")


# ──────────────────────────── 14. Список бажань ─────────────────────────

class WishlistItem(Base):
    __tablename__ = "wishlist"
    __table_args__ = (UniqueConstraint("user_id", "product_id"),)

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, nullable=False)
    added_at   = Column(DateTime, server_default=func.now())

    user    = relationship("User", back_populates="wishlist",
                           foreign_keys=[user_id],
                           primaryjoin="WishlistItem.user_id == User.id")
    product = relationship("Product",
                           foreign_keys=[product_id],
                           primaryjoin="WishlistItem.product_id == Product.id")
