from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ──────────────────────────── Products ──────────────────────────────────

class ProductBase(BaseModel):
    name: str
    category: Optional[str] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    price: float
    old_price: Optional[float] = None
    image_url: Optional[str] = None
    stock: Optional[int] = 0
    specs: Optional[str] = None
    is_available: Optional[int] = 1
    is_rental: Optional[int] = 0
    rental_price: Optional[float] = None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ──────────────────────────── Categories ────────────────────────────────

class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    image_url: Optional[str] = None
    sort_order: Optional[int] = 0

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ──────────────────────────── Users ─────────────────────────────────────

class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: int
    is_admin: int
    avatar_url: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    is_active: Optional[int] = None
    is_admin: Optional[int] = None

class Token(BaseModel):
    access_token: str
    token_type: str


# ──────────────────────────── Orders ────────────────────────────────────

class OrderItemBase(BaseModel):
    product_id: int
    product_name: str
    quantity: int = 1
    unit_price: float
    total_price: float

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: str
    address: Optional[str] = None
    apartment: Optional[str] = None
    postcode: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    branch_name: Optional[str] = None
    payment_method: str = "cash"
    promo_code: Optional[str] = None
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]
    delivery_cost: float = 0
    discount_amount: float = 0

class OrderResponse(OrderBase):
    id: int
    user_id: Optional[int] = None
    order_number: str
    status: str
    total_amount: float
    delivery_cost: float
    discount_amount: float
    payment_status: str
    items: List[OrderItemResponse] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: Optional[str] = None
    payment_status: Optional[str] = None


# ──────────────────────────── Cart ──────────────────────────────────────

class CartItemBase(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemCreate(CartItemBase):
    pass

class CartItemResponse(CartItemBase):
    id: int
    user_id: int
    added_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ──────────────────────────── Rentals ───────────────────────────────────

class RentalBase(BaseModel):
    product_id: int
    start_date: str
    end_date: str
    notes: Optional[str] = None

class RentalCreate(RentalBase):
    pass

class RentalResponse(RentalBase):
    id: int
    user_id: int
    status: str
    daily_rate: float
    total_cost: float
    deposit: float
    return_date: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ──────────────────────────── Promocodes ────────────────────────────────

class PromocodeBase(BaseModel):
    code: str
    discount_percent: float = 0
    discount_amount: float = 0
    min_order_amount: float = 0
    max_uses: int = 0
    is_active: int = 1
    valid_until: Optional[datetime] = None

class PromocodeCreate(PromocodeBase):
    pass

class PromocodeResponse(PromocodeBase):
    id: int
    used_count: int
    valid_from: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PromocodeCheck(BaseModel):
    code: str

class PromocodeCheckResponse(BaseModel):
    valid: bool
    discount_percent: float = 0
    discount_amount: float = 0
    message: str = ""


# ──────────────────────────── Customization ─────────────────────────────

class CustomizationBase(BaseModel):
    cpu: Optional[str] = None
    gpu: Optional[str] = None
    ram: Optional[str] = None
    storage: Optional[str] = None
    case_type: Optional[str] = None
    cooling: Optional[str] = None
    power_supply: Optional[str] = None
    extras: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    notes: Optional[str] = None

class CustomizationCreate(CustomizationBase):
    pass

class CustomizationResponse(CustomizationBase):
    id: int
    user_id: Optional[int] = None
    status: str
    total_estimate: Optional[float] = None
    admin_comment: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ──────────────────────────── News ──────────────────────────────────────

class NewsBase(BaseModel):
    title: str
    slug: str
    content: str
    excerpt: Optional[str] = None
    image_url: Optional[str] = None
    is_published: int = 0

class NewsCreate(NewsBase):
    pass

class NewsResponse(NewsBase):
    id: int
    author_id: Optional[int] = None
    views_count: int = 0
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ──────────────────────────── Reviews ───────────────────────────────────

class ReviewBase(BaseModel):
    product_id: int
    rating: int
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    is_approved: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ──────────────────────────── Wishlist ──────────────────────────────────

class WishlistItemCreate(BaseModel):
    product_id: int

class WishlistItemResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    added_at: Optional[datetime] = None

    class Config:
        from_attributes = True
