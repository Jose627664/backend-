from fastapi import FastAPI, APIRouter, HTTPException, Header, Cookie, Request, Response, Depends
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timedelta, timezone
import asyncio
# Import models and auth
from models import (
    User, UserCreate, UserLogin, UserResponse, UserSession,
    Product, ProductCreate, ProductUpdate,
    Category, CategoryCreate,
    Region, RegionCreate,
    Recipe, RecipeCreate,
    Order, OrderCreate, OrderItem, DeliveryInfo,
    PaymentTransaction,
    Testimonial
)
from auth import hash_password, verify_password, create_access_token, get_current_user, get_current_admin

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
from pymongo import MongoClient
import os

mongo_url = os.getenv("MONGO_URL")

if mongo_url:
    client = MongoClient(mongo_url)
    db = client.get_database()
    print("✅ MongoDB connected")
else:
    db = None
    print("⚠️ MongoDB not configured — running without DB")
client = AsyncIOMotorClient(mongo_url)
db_name = os.getenv("DB_NAME")

if mongo_url and db_name:
    db = client[db_name]
else:
    db = None
# Create the main app
app = FastAPI(title="Afro-Latino Marketplace API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== AUTH ROUTES ====================

@api_router.post("/auth/register")
async def register(user_data: UserCreate):
    """Register a new user with email/password"""
    # Check if user exists
    existing_user = await db.users.find_one({'email': user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=hash_password(user_data.password),
        auth_provider='email'
    )
    
    await db.users.insert_one(user.dict())
    
    # Create access token
    token = create_access_token(user.user_id)
    
    return {
        'user': UserResponse(**user.dict()),
        'session_token': token
    }

@api_router.post("/auth/login")
async def login(credentials: UserLogin, response: Response):
    """Login with email/password"""
    # Find user
    user_doc = await db.users.find_one({'email': credentials.email}, {'_id': 0})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = User(**user_doc)
    
    # Verify password
    if not user.password_hash or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create access token
    token = create_access_token(user.user_id)
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7*24*60*60,  # 7 days
        path="/"
    )
    
    return {
        'user': UserResponse(**user.dict()),
        'session_token': token
    }

@api_router.get("/auth/me")
async def get_me(
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Get current authenticated user"""
    user = await get_current_user(db, authorization, session_token)
    return UserResponse(**user.dict())

@api_router.post("/auth/logout")
async def logout(response: Response):
    """Logout user"""
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logged out successfully"}

# ==================== PRODUCT ROUTES ====================

@api_router.get("/products")
async def get_products(
    culture: Optional[str] = None,
    category: Optional[str] = None,
    region: Optional[str] = None,
    country: Optional[str] = None,
    search: Optional[str] = None,
    featured: Optional[bool] = None,
    page: int = 1,
    limit: int = 20
):
    """Get all products with filters"""
    query = {}
    
    if culture:
        query['culture'] = {'$in': [culture, 'Fusion']}
    if category:
        query['category'] = {'$regex': category, '$options': 'i'}
    if region:
        query['region'] = {'$regex': region, '$options': 'i'}
    if country:
        query['country'] = {'$regex': country, '$options': 'i'}
    if featured is not None:
        query['featured'] = featured
    if search:
        query['$or'] = [
            {'name': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}},
            {'category': {'$regex': search, '$options': 'i'}},
            {'country': {'$regex': search, '$options': 'i'}}
        ]
    
    # Get total count
    total = await db.products.count_documents(query)
    
    # Get paginated results
    skip = (page - 1) * limit
    cursor = db.products.find(query, {'_id': 0}).skip(skip).limit(limit)
    products = await cursor.to_list(length=limit)
    
    return {
        'products': products,
        'total': total,
        'page': page,
        'pages': (total + limit - 1) // limit
    }

@api_router.get("/products/{product_id}")
async def get_product(product_id: str):
    """Get single product by ID"""
    product = await db.products.find_one({'product_id': product_id}, {'_id': 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@api_router.post("/products")
async def create_product(
    product: ProductCreate,
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Create new product (Admin only)"""
    await get_current_admin(db, authorization, session_token)
    
    new_product = Product(**product.dict())
    await db.products.insert_one(new_product.dict())
    
    # Update category count
    await db.categories.update_one(
        {'name': product.category},
        {'$inc': {'product_count': 1}}
    )
    
    return new_product.dict()

@api_router.put("/products/{product_id}")
async def update_product(
    product_id: str,
    product_update: ProductUpdate,
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Update product (Admin only)"""
    await get_current_admin(db, authorization, session_token)
    
    # Get existing product
    existing = await db.products.find_one({'product_id': product_id}, {'_id': 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update fields
    update_data = {k: v for k, v in product_update.dict().items() if v is not None}
    update_data['updated_at'] = datetime.utcnow()
    
    await db.products.update_one(
        {'product_id': product_id},
        {'$set': update_data}
    )
    
    # If category changed, update counts
    if 'category' in update_data and update_data['category'] != existing['category']:
        await db.categories.update_one({'name': existing['category']}, {'$inc': {'product_count': -1}})
        await db.categories.update_one({'name': update_data['category']}, {'$inc': {'product_count': 1}})
    
    updated = await db.products.find_one({'product_id': product_id}, {'_id': 0})
    return updated

@api_router.delete("/products/{product_id}")
async def delete_product(
    product_id: str,
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Delete product (Admin only)"""
    await get_current_admin(db, authorization, session_token)
    
    product = await db.products.find_one({'product_id': product_id}, {'_id': 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    await db.products.delete_one({'product_id': product_id})
    
    # Update category count
    await db.categories.update_one(
        {'name': product['category']},
        {'$inc': {'product_count': -1}}
    )
    
    return {"message": "Product deleted successfully"}

# ==================== CATEGORY & REGION ROUTES ====================

@api_router.get("/categories")
async def get_categories():
    """Get all categories"""
    categories = await db.categories.find({}, {'_id': 0}).to_list(length=100)
    return {'categories': categories}

@api_router.get("/regions")
async def get_regions():
    """Get all regions"""
    regions = await db.regions.find({}, {'_id': 0}).to_list(length=100)
    return {'regions': regions}

@api_router.post("/categories")
async def create_category(
    category: CategoryCreate,
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Create category (Admin only)"""
    await get_current_admin(db, authorization, session_token)
    new_category = Category(**category.dict())
    await db.categories.insert_one(new_category.dict())
    return new_category.dict()

@api_router.delete("/categories/{category_id}")
async def delete_category(
    category_id: str,
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Delete category (Admin only)"""
    await get_current_admin(db, authorization, session_token)
    await db.categories.delete_one({'category_id': category_id})
    return {"message": "Category deleted"}

# ==================== RECIPE ROUTES ====================

@api_router.get("/recipes")
async def get_recipes(
    culture: Optional[str] = None,
    search: Optional[str] = None
):
    """Get all recipes with filters"""
    query = {}
    if culture:
        query['culture'] = culture
    if search:
        query['$or'] = [
            {'title': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}}
        ]
    
    recipes = await db.recipes.find(query, {'_id': 0}).to_list(length=100)
    return {'recipes': recipes}

@api_router.post("/recipes")
async def create_recipe(
    recipe: RecipeCreate,
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Create recipe (Admin only)"""
    await get_current_admin(db, authorization, session_token)
    new_recipe = Recipe(**recipe.dict())
    await db.recipes.insert_one(new_recipe.dict())
    return new_recipe.dict()

@api_router.delete("/recipes/{recipe_id}")
async def delete_recipe(
    recipe_id: str,
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Delete recipe (Admin only)"""
    await get_current_admin(db, authorization, session_token)
    await db.recipes.delete_one({'recipe_id': recipe_id})
    return {"message": "Recipe deleted"}

# ==================== TESTIMONIAL ROUTES ====================

@api_router.get("/testimonials")
async def get_testimonials():
    """Get all testimonials"""
    testimonials = await db.testimonials.find({}, {'_id': 0}).to_list(length=100)
    return {'testimonials': testimonials}

# ==================== ORDER ROUTES ====================

@api_router.post("/orders")
async def create_order(
    order_data: OrderCreate,
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Create a new order"""
    # Get user if authenticated
    user_id = None
    try:
        user = await get_current_user(db, authorization, session_token)
        user_id = user.user_id
    except:
        pass  # Allow guest checkout
    
    # Calculate totals
    subtotal = sum(item.price * item.quantity for item in order_data.items)
    
    # Calculate delivery fee ($10 for first 5km + $2/km additional)
    # Mock distance calculation
    distance_km = 8
    if subtotal >= 50:
        delivery_fee = 0
    elif distance_km <= 5:
        delivery_fee = 10
    else:
        delivery_fee = 10 + ((distance_km - 5) * 2)
    
    total = subtotal + delivery_fee
    
    # Create order
    order = Order(
        user_id=user_id,
        items=order_data.items,
        delivery_info=order_data.delivery_info,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total=total,
        payment_method=order_data.payment_method
    )
    
    await db.orders.insert_one(order.dict())
    
    # Create payment URL based on method
    if order_data.payment_method == 'stripe':
        # Redirect to Stripe payment route
        return {
            'order_id': order.order_id,
            'payment_url': f'/api/payments/stripe/checkout/{order.order_id}'
        }
    else:
        # Redirect to PayPal payment route
        return {
            'order_id': order.order_id,
            'payment_url': f'/api/payments/paypal/checkout/{order.order_id}'
        }

@api_router.get("/orders")
async def get_orders(
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Get user's orders"""
    user = await get_current_user(db, authorization, session_token)
    orders = await db.orders.find({'user_id': user.user_id}, {'_id': 0}).to_list(length=100)
    return {'orders': orders}

@api_router.get("/orders/{order_id}")
async def get_order(
    order_id: str,
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Get single order"""
    user = await get_current_user(db, authorization, session_token)
    order = await db.orders.find_one({'order_id': order_id, 'user_id': user.user_id}, {'_id': 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# ==================== PAYMENT ROUTES (STRIPE) ====================

async def get_stripe_credentials():
    """Get Stripe credentials from database"""
    settings = await db.site_settings.find_one({'settings_id': 'site_settings'}, {'_id': 0})
    if settings and settings.get('stripe_api_key'):
        return settings['stripe_api_key']
    # Fallback to environment variable
    return os.getenv('STRIPE_API_KEY', 'sk_test_emergent')

@api_router.get("/payments/stripe/checkout/{order_id}")
async def stripe_checkout(order_id: str, request: Request):
    """Create Stripe checkout session"""
    # Get order
    order = await db.orders.find_one({'order_id': order_id}, {'_id': 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Get Stripe API key
    stripe_api_key = await get_stripe_credentials()
    
    # Get host URL from request
    host_url = str(request.base_url).rstrip('/')
    
    # Create Stripe checkout
    stripe_checkout = StripeCheckout(
        api_key=stripe_api_key,
        webhook_url=f"{host_url}/api/payments/stripe/webhook"
    )
    
    # Prepare checkout request
    success_url = f"{host_url}/order-success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{host_url}/checkout"
    
    checkout_request = CheckoutSessionRequest(
        amount=float(order['total']),
        currency='cad',
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            'order_id': order_id,
            'user_id': order.get('user_id', 'guest')
        }
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    # Create payment transaction
    transaction = PaymentTransaction(
        order_id=order_id,
        user_id=order.get('user_id'),
        amount=order['total'],
        currency='cad',
        payment_method='stripe',
        payment_status='pending',
        stripe_session_id=session.session_id,
        metadata={'order_id': order_id}
    )
    
    await db.payment_transactions.insert_one(transaction.dict())
    
    # Redirect to Stripe
    return JSONResponse({'url': session.url, 'session_id': session.session_id})

@api_router.get("/payments/stripe/status/{session_id}")
async def stripe_payment_status(session_id: str):
    """Check Stripe payment status"""
    stripe_api_key = await get_stripe_credentials()
    stripe_checkout = StripeCheckout(api_key=stripe_api_key)
    status = await stripe_checkout.get_checkout_status(session_id)
    
    # Update transaction and order
    transaction = await db.payment_transactions.find_one({'stripe_session_id': session_id}, {'_id': 0})
    if transaction:
        # Update transaction
        await db.payment_transactions.update_one(
            {'stripe_session_id': session_id},
            {'$set': {'payment_status': status.payment_status, 'updated_at': datetime.utcnow()}}
        )
        
        # Update order
        if status.payment_status == 'paid':
            await db.orders.update_one(
                {'order_id': transaction['order_id']},
                {'$set': {'payment_status': 'paid', 'order_status': 'processing', 'updated_at': datetime.utcnow()}}
            )
    
    return status.dict()

@api_router.post("/payments/stripe/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    body = await request.body()
    sig_header = request.headers.get('Stripe-Signature')
    
    stripe_api_key = await get_stripe_credentials()
    stripe_checkout = StripeCheckout(
        api_key=stripe_api_key,
        webhook_url=str(request.base_url) + "/api/payments/stripe/webhook"
    )
    
    try:
        event = await stripe_checkout.handle_webhook(body, sig_header)
        
        if event.event_type == 'checkout.session.completed':
            # Update payment status
            await db.payment_transactions.update_one(
                {'stripe_session_id': event.session_id},
                {'$set': {'payment_status': 'paid', 'updated_at': datetime.utcnow()}}
            )
            
            # Update order
            transaction = await db.payment_transactions.find_one({'stripe_session_id': event.session_id}, {'_id': 0})
            if transaction:
                await db.orders.update_one(
                    {'order_id': transaction['order_id']},
                    {'$set': {'payment_status': 'paid', 'order_status': 'processing', 'updated_at': datetime.utcnow()}}
                )
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# ==================== SITE SETTINGS ROUTES ====================

@api_router.get("/settings")
async def get_settings():
    """Get site settings"""
    settings = await db.site_settings.find_one({'settings_id': 'site_settings'}, {'_id': 0})
    if not settings:
        # Create default settings
        from models import SiteSettings
        default_settings = SiteSettings()
        await db.site_settings.insert_one(default_settings.dict())
        return default_settings.dict()
    return settings

@api_router.put("/settings")
async def update_settings(
    settings_update: dict,
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Update site settings (Admin only)"""
    await get_current_admin(db, authorization, session_token)
    
    settings_update['updated_at'] = datetime.utcnow()
    
    await db.site_settings.update_one(
        {'settings_id': 'site_settings'},
        {'$set': settings_update},
        upsert=True
    )
    
    updated_settings = await db.site_settings.find_one({'settings_id': 'site_settings'}, {'_id': 0})
    return updated_settings

# ==================== HOLIDAY NOTICE ROUTES ====================

@api_router.get("/notices")
async def get_notices():
    """Get active notices"""
    now = datetime.utcnow()
    notices = await db.holiday_notices.find({
        'is_active': True,
        'start_date': {'$lte': now},
        'end_date': {'$gte': now}
    }, {'_id': 0}).to_list(length=10)
    return {'notices': notices}

@api_router.get("/notices/all")
async def get_all_notices(
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Get all notices (Admin only)"""
    await get_current_admin(db, authorization, session_token)
    notices = await db.holiday_notices.find({}, {'_id': 0}).sort('created_at', -1).to_list(length=100)
    return {'notices': notices}

@api_router.post("/notices")
async def create_notice(
    notice_data: dict,
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Create notice (Admin only)"""
    await get_current_admin(db, authorization, session_token)
    
    from models import HolidayNotice
    notice = HolidayNotice(**notice_data)
    await db.holiday_notices.insert_one(notice.dict())
    return notice.dict()

@api_router.put("/notices/{notice_id}")
async def update_notice(
    notice_id: str,
    notice_update: dict,
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Update notice (Admin only)"""
    await get_current_admin(db, authorization, session_token)
    
    notice_update['updated_at'] = datetime.utcnow()
    
    await db.holiday_notices.update_one(
        {'notice_id': notice_id},
        {'$set': notice_update}
    )
    
    updated = await db.holiday_notices.find_one({'notice_id': notice_id}, {'_id': 0})
    return updated

@api_router.delete("/notices/{notice_id}")
async def delete_notice(
    notice_id: str,
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Delete notice (Admin only)"""
    await get_current_admin(db, authorization, session_token)
    await db.holiday_notices.delete_one({'notice_id': notice_id})
    return {"message": "Notice deleted"}

# ==================== BLOG ROUTES ====================

@api_router.get("/blog")
async def get_blog_posts(
    category: Optional[str] = None,
    published: bool = True,
    page: int = 1,
    limit: int = 10
):
    """Get blog posts"""
    query = {'published': published} if published else {}
    if category:
        query['category'] = category
    
    total = await db.blog_posts.count_documents(query)
    skip = (page - 1) * limit
    
    posts = await db.blog_posts.find(query, {'_id': 0}).sort('created_at', -1).skip(skip).limit(limit).to_list(length=limit)
    
    return {
        'posts': posts,
        'total': total,
        'page': page,
        'pages': (total + limit - 1) // limit
    }

@api_router.get("/blog/{post_id}")
async def get_blog_post(post_id: str):
    """Get single blog post"""
    post = await db.blog_posts.find_one({'post_id': post_id}, {'_id': 0})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Increment views
    await db.blog_posts.update_one({'post_id': post_id}, {'$inc': {'views': 1}})
    post['views'] = post.get('views', 0) + 1
    
    return post

@api_router.get("/blog/slug/{slug}")
async def get_blog_post_by_slug(slug: str):
    """Get blog post by slug"""
    post = await db.blog_posts.find_one({'slug': slug}, {'_id': 0})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Increment views
    await db.blog_posts.update_one({'slug': slug}, {'$inc': {'views': 1}})
    post['views'] = post.get('views', 0) + 1
    
    return post

@api_router.post("/blog")
async def create_blog_post(
    post_data: dict,
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Create blog post (Admin only)"""
    await get_current_admin(db, authorization, session_token)
    
    from models import BlogPost
    
    # Generate slug from title
    import re
    slug = re.sub(r'[^a-z0-9]+', '-', post_data['title'].lower()).strip('-')
    post_data['slug'] = slug
    
    post = BlogPost(**post_data)
    await db.blog_posts.insert_one(post.dict())
    return post.dict()

@api_router.put("/blog/{post_id}")
async def update_blog_post(
    post_id: str,
    post_update: dict,
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Update blog post (Admin only)"""
    await get_current_admin(db, authorization, session_token)
    
    post_update['updated_at'] = datetime.utcnow()
    
    # Update slug if title changed
    if 'title' in post_update:
        import re
        slug = re.sub(r'[^a-z0-9]+', '-', post_update['title'].lower()).strip('-')
        post_update['slug'] = slug
    
    await db.blog_posts.update_one(
        {'post_id': post_id},
        {'$set': post_update}
    )
    
    updated = await db.blog_posts.find_one({'post_id': post_id}, {'_id': 0})
    return updated

@api_router.delete("/blog/{post_id}")
async def delete_blog_post(
    post_id: str,
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Delete blog post (Admin only)"""
    await get_current_admin(db, authorization, session_token)
    await db.blog_posts.delete_one({'post_id': post_id})
    return {"message": "Blog post deleted"}

# ==================== ANNOUNCEMENTS ROUTES ====================

@api_router.get("/announcements")
async def get_announcements():
    """Get active announcements"""
    announcements = await db.announcements.find(
        {'is_active': True},
        {'_id': 0}
    ).sort('priority', -1).limit(5).to_list(length=5)
    return {'announcements': announcements}

@api_router.get("/announcements/all")
async def get_all_announcements(
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Get all announcements (Admin only)"""
    await get_current_admin(db, authorization, session_token)
    announcements = await db.announcements.find({}, {'_id': 0}).sort('created_at', -1).to_list(length=100)
    return {'announcements': announcements}

@api_router.post("/announcements")
async def create_announcement(
    announcement_data: dict,
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Create announcement (Admin only)"""
    await get_current_admin(db, authorization, session_token)
    
    from models import Announcement
    announcement = Announcement(**announcement_data)
    await db.announcements.insert_one(announcement.dict())
    return announcement.dict()

@api_router.put("/announcements/{announcement_id}")
async def update_announcement(
    announcement_id: str,
    announcement_update: dict,
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Update announcement (Admin only)"""
    await get_current_admin(db, authorization, session_token)
    
    announcement_update['updated_at'] = datetime.utcnow()
    
    await db.announcements.update_one(
        {'announcement_id': announcement_id},
        {'$set': announcement_update}
    )
    
    updated = await db.announcements.find_one({'announcement_id': announcement_id}, {'_id': 0})
    return updated

@api_router.delete("/announcements/{announcement_id}")
async def delete_announcement(
    announcement_id: str,
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Delete announcement (Admin only)"""
    await get_current_admin(db, authorization, session_token)
    await db.announcements.delete_one({'announcement_id': announcement_id})
    return {"message": "Announcement deleted"}

# ==================== USER ROUTES ====================

@api_router.get("/users")
async def get_users(
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Get all users (Admin only)"""
    await get_current_admin(db, authorization, session_token)
    users = await db.users.find({}, {'_id': 0, 'password_hash': 0}).to_list(length=1000)
    return {'users': users}

@api_router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    update_data: dict,
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None)
):
    """Update user profile"""
    user = await get_current_user(db, authorization, session_token)
    
    # Check permission
    if user.user_id != user_id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Remove sensitive fields
    update_data.pop('password_hash', None)
    update_data.pop('is_admin', None)
    update_data['updated_at'] = datetime.utcnow()
    
    await db.users.update_one({'user_id': user_id}, {'$set': update_data})
    
    updated_user = await db.users.find_one({'user_id': user_id}, {'_id': 0, 'password_hash': 0})
    return updated_user

# Include the router in the main app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
