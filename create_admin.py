import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
from auth import hash_password

async def create_admin_user():
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.getenv('DB_NAME', 'test_database')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Check if admin already exists
    existing_admin = await db.users.find_one({'email': 'admin@afrolatino.ca'})
    
    if existing_admin:
        print('⚠️  Admin user already exists!')
        print('   Email: admin@afrolatino.ca')
        client.close()
        return
    
    # Create admin user
    admin_user = {
        'user_id': 'user_admin001',
        'email': 'admin@afrolatino.ca',
        'name': 'Admin User',
        'picture': None,
        'auth_provider': 'email',
        'password_hash': hash_password('AfroLatino2025!'),
        'phone': None,
        'address': None,
        'is_admin': True,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    await db.users.insert_one(admin_user)
    
    print('✅ Admin user created successfully!')
    print('')
    print('═' * 60)
    print('   ADMIN LOGIN CREDENTIALS')
    print('═' * 60)
    print('   Email:    admin@afrolatino.ca')
    print('   Password: AfroLatino2025!')
    print('═' * 60)
    print('')
    print('🔐 Please save these credentials securely!')
    print('📍 Access admin panel at: /admin')
    print('')
    
    # Initialize default site settings with payment credentials
    settings = await db.site_settings.find_one({'settings_id': 'site_settings'})
    if not settings:
        default_settings = {
            'settings_id': 'site_settings',
            'free_delivery_threshold': 50.0,
            'delivery_base_fee': 10.0,
            'delivery_per_km_fee': 2.0,
            'site_title': 'Afro-Latino Marketplace',
            'contact_email': 'info@afrolatino.ca',
            'stripe_api_key': os.getenv('STRIPE_API_KEY', ''),
            'stripe_webhook_secret': '',
            'paypal_client_id': '',
            'paypal_client_secret': '',
            'updated_at': datetime.utcnow()
        }
        await db.site_settings.insert_one(default_settings)
        print('✅ Default site settings initialized')
    
    client.close()

if __name__ == '__main__':
    asyncio.run(create_admin_user())
