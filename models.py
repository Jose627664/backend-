from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime
import uuid

def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

# User Models
class User(BaseModel):
    user_id: str = Field(default_factory=lambda: generate_id('user'))
    email: EmailStr
    name: str
    picture: Optional[str] = None
    auth_provider: str = 'email'  # 'google' or 'email'
    password_hash: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    is_admin: bool = False

class UserSession(BaseModel):
    session_token: str
    user_id: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Product Models
class Product(BaseModel):
    product_id: str = Field(default_factory=lambda: generate_id('prod'))
    name: str
    price: float
    image: str
    images: List[str] = []
    category: str
    culture: str  # African, Latino, Fusion
    country: str
    region: str
    description: str
    ingredients: Optional[str] = None
    storage_instructions: Optional[str] = None
    in_stock: bool = True
    featured: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProductCreate(BaseModel):
    name: str
    price: float
    image: str
    images: List[str] = []
    category: str
    culture: str
    country: str
    region: str
    description: str
    ingredients: Optional[str] = None
    storage_instructions: Optional[str] = None
    featured: bool = False

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    image: Optional[str] = None
    images: Optional[List[str]] = None
    category: Optional[str] = None
    culture: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    description: Optional[str] = None
    ingredients: Optional[str] = None
    storage_instructions: Optional[str] = None
    in_stock: Optional[bool] = None
    featured: Optional[bool] = None

# Category Models
class Category(BaseModel):
    category_id: str = Field(default_factory=lambda: generate_id('cat'))
    name: str
    icon: str
    product_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CategoryCreate(BaseModel):
    name: str
    icon: str

# Region Models
class Region(BaseModel):
    region_id: str = Field(default_factory=lambda: generate_id('reg'))
    name: str
    countries: List[str]
    image: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RegionCreate(BaseModel):
    name: str
    countries: List[str]
    image: str

# Recipe Models
class Recipe(BaseModel):
    recipe_id: str = Field(default_factory=lambda: generate_id('rec'))
    title: str
    culture: str
    image: str
    description: str
    cook_time: str
    difficulty: str  # Easy, Medium, Advanced
    ingredients: List[str] = []
    instructions: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class RecipeCreate(BaseModel):
    title: str
    culture: str
    image: str
    description: str
    cook_time: str
    difficulty: str
    ingredients: List[str]
    instructions: List[str]

# Order Models
class OrderItem(BaseModel):
    product_id: str
    name: str
    price: float
    quantity: int
    image: str

class DeliveryInfo(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    address: str
    city: str = 'Moncton'
    province: str = 'NB'
    postal_code: str
    delivery_notes: Optional[str] = None

class Order(BaseModel):
    order_id: str = Field(default_factory=lambda: generate_id('ord'))
    user_id: Optional[str] = None
    items: List[OrderItem]
    delivery_info: DeliveryInfo
    subtotal: float
    delivery_fee: float
    total: float
    payment_method: str  # stripe or paypal
    payment_status: str = 'pending'  # pending, paid, failed
    order_status: str = 'processing'  # processing, shipped, delivered, cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class OrderCreate(BaseModel):
    items: List[OrderItem]
    delivery_info: DeliveryInfo
    payment_method: str

# Payment Models
class PaymentTransaction(BaseModel):
    transaction_id: str = Field(default_factory=lambda: generate_id('txn'))
    order_id: str
    user_id: Optional[str] = None
    amount: float
    currency: str = 'cad'
    payment_method: str  # stripe or paypal
    payment_status: str = 'pending'
    stripe_session_id: Optional[str] = None
    paypal_order_id: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Testimonial Models
class Testimonial(BaseModel):
    testimonial_id: str = Field(default_factory=lambda: generate_id('test'))
    name: str
    location: str
    culture: str
    rating: int = 5
    text: str
    avatar: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Site Settings Models
class SiteSettings(BaseModel):
    settings_id: str = 'site_settings'
    free_delivery_threshold: float = 50.0
    delivery_base_fee: float = 10.0
    delivery_per_km_fee: float = 2.0
    site_title: str = 'Afro-Latino Marketplace'
    contact_email: str = 'info@afrolatino.ca'
    # Payment credentials
    stripe_api_key: str = ''
    stripe_webhook_secret: str = ''
    paypal_client_id: str = ''
    paypal_client_secret: str = ''
    # Social media links
    facebook_url: str = ''
    instagram_url: str = ''
    twitter_url: str = ''
    youtube_url: str = ''
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SiteSettingsUpdate(BaseModel):
    free_delivery_threshold: Optional[float] = None
    delivery_base_fee: Optional[float] = None
    delivery_per_km_fee: Optional[float] = None
    site_title: Optional[str] = None
    contact_email: Optional[str] = None
    stripe_api_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    paypal_client_id: Optional[str] = None
    paypal_client_secret: Optional[str] = None
    facebook_url: Optional[str] = None
    instagram_url: Optional[str] = None
    twitter_url: Optional[str] = None
    youtube_url: Optional[str] = None

# Holiday/Notice Models
class HolidayNotice(BaseModel):
    notice_id: str = Field(default_factory=lambda: generate_id('notice'))
    title: str
    message: str
    start_date: datetime
    end_date: datetime
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class HolidayNoticeCreate(BaseModel):
    title: str
    message: str
    start_date: datetime
    end_date: datetime
    is_active: bool = True

# Blog Models
class BlogPost(BaseModel):
    post_id: str = Field(default_factory=lambda: generate_id('post'))
    title: str
    slug: str
    content: str
    excerpt: str
    author: str
    featured_image: str
    category: str = 'General'
    tags: List[str] = []
    published: bool = False
    views: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BlogPostCreate(BaseModel):
    title: str
    content: str
    excerpt: str
    author: str
    featured_image: str
    category: str = 'General'
    tags: List[str] = []
    published: bool = False

class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    featured_image: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    published: Optional[bool] = None

# Community Announcement Models
class Announcement(BaseModel):
    announcement_id: str = Field(default_factory=lambda: generate_id('ann'))
    title: str
    message: str
    type: str = 'info'  # info, event, promotion
    link: Optional[str] = None
    is_active: bool = True
    priority: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AnnouncementCreate(BaseModel):
    title: str
    message: str
    type: str = 'info'
    link: Optional[str] = None
    is_active: bool = True
    priority: int = 0
