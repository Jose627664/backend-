# Seed data for initial database setup
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime

mock_products = [
    {
        'product_id': 'prod-001',
        'name': 'Nigerian Jollof Rice Mix',
        'price': 12.99,
        'image': 'https://images.unsplash.com/photo-1665332195309-9d75071138f0?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwxfHxBZnJpY2FuJTIwZm9vZHxlbnwwfHx8fDE3NjUwNTMzNDB8MA&ixlib=rb-4.1.0&q=85',
        'images': [],
        'category': 'Grains & Flours',
        'culture': 'African',
        'country': 'Nigeria',
        'region': 'West Africa',
        'description': 'Authentic Nigerian Jollof rice spice blend with tomatoes and peppers',
        'in_stock': True,
        'featured': True,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'product_id': 'prod-002',
        'name': 'Mexican Adobo Seasoning',
        'price': 8.99,
        'image': 'https://images.unsplash.com/photo-1640719028782-8230f1bdc42a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHwzfHxMYXRpbiUyMEFtZXJpY2FuJTIwZm9vZHxlbnwwfHx8fDE3NjUwNTMzNDZ8MA&ixlib=rb-4.1.0&q=85',
        'images': [],
        'category': 'Spices & Herbs',
        'culture': 'Latino',
        'country': 'Mexico',
        'region': 'Central America',
        'description': 'Traditional Mexican adobo blend with chili, garlic, and cumin',
        'in_stock': True,
        'featured': True,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'product_id': 'prod-003',
        'name': 'Plantains (Green)',
        'price': 4.99,
        'image': 'https://images.unsplash.com/photo-1665332561290-cc6757172890?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwyfHxBZnJpY2FuJTIwZm9vZHxlbnwwfHx8fDE3NjUwNTMzNDB8MA&ixlib=rb-4.1.0&q=85',
        'images': [],
        'category': 'Fresh Produce',
        'culture': 'Fusion',
        'country': 'Multiple',
        'region': 'Multiple',
        'description': 'Fresh green plantains perfect for frying or baking. Loved from Lagos to Bogota',
        'in_stock': True,
        'featured': True,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'product_id': 'prod-004',
        'name': 'Suya Spice Blend',
        'price': 10.99,
        'image': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHw0fHxBZnJpY2FuJTIwZm9vZHxlbnwwfHx8fDE3NjUwNTMzNDB8MA&ixlib=rb-4.1.0&q=85',
        'images': [],
        'category': 'Spices & Herbs',
        'culture': 'African',
        'country': 'Nigeria',
        'region': 'West Africa',
        'description': 'Authentic Nigerian Suya spice blend with peanuts, ginger, and cayenne',
        'in_stock': True,
        'featured': True,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'product_id': 'prod-005',
        'name': 'Colombian Coffee',
        'price': 15.99,
        'image': 'https://images.pexels.com/photos/35030234/pexels-photo-35030234.jpeg',
        'images': [],
        'category': 'Beverages & Juices',
        'culture': 'Latino',
        'country': 'Colombia',
        'region': 'South America',
        'description': 'Premium Colombian coffee beans, medium roast',
        'in_stock': True,
        'featured': False,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'product_id': 'prod-006',
        'name': 'Ethiopian Coffee Beans',
        'price': 16.99,
        'image': 'https://images.pexels.com/photos/3213283/pexels-photo-3213283.jpeg',
        'images': [],
        'category': 'Beverages & Juices',
        'culture': 'African',
        'country': 'Ethiopia',
        'region': 'East Africa',
        'description': 'Single-origin Ethiopian coffee beans with floral notes',
        'in_stock': True,
        'featured': False,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'product_id': 'prod-007',
        'name': 'Goya Black Beans',
        'price': 3.99,
        'image': 'https://images.unsplash.com/photo-1674669520816-c3c5615dfe51?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHwxfHxMYXRpbiUyMEFtZXJpY2FuJTIwZm9vZHxlbnwwfHx8fDE3NjUwNTMzNDZ8MA&ixlib=rb-4.1.0&q=85',
        'images': [],
        'category': 'Pantry Staples',
        'culture': 'Latino',
        'country': 'Multiple',
        'region': 'Caribbean Latino',
        'description': 'Premium Goya black beans, ready to cook',
        'in_stock': True,
        'featured': False,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'product_id': 'prod-008',
        'name': 'Egusi Seeds',
        'price': 9.99,
        'image': 'https://images.unsplash.com/photo-1665400808116-f0e6339b7e9a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwzfHxBZnJpY2FuJTIwZm9vZHxlbnwwfHx8fDE3NjUwNTMzNDB8MA&ixlib=rb-4.1.0&q=85',
        'images': [],
        'category': 'Grains & Flours',
        'culture': 'African',
        'country': 'Nigeria',
        'region': 'West Africa',
        'description': 'Ground egusi (melon seeds) for authentic Nigerian soups',
        'in_stock': True,
        'featured': False,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
]

mock_categories = [
    {'category_id': 'cat-001', 'name': 'Fresh Produce', 'icon': '🥬', 'product_count': 0},
    {'category_id': 'cat-002', 'name': 'Spices & Herbs', 'icon': '🌶️', 'product_count': 0},
    {'category_id': 'cat-003', 'name': 'Grains & Flours', 'icon': '🌾', 'product_count': 0},
    {'category_id': 'cat-004', 'name': 'Frozen Foods', 'icon': '❄️', 'product_count': 0},
    {'category_id': 'cat-005', 'name': 'Snacks & Sweets', 'icon': '🍬', 'product_count': 0},
    {'category_id': 'cat-006', 'name': 'Oils, Sauces & Condiments', 'icon': '🫙', 'product_count': 0},
    {'category_id': 'cat-007', 'name': 'Beverages & Juices', 'icon': '🥤', 'product_count': 0},
    {'category_id': 'cat-008', 'name': 'Beauty & Wellness', 'icon': '💆', 'product_count': 0},
    {'category_id': 'cat-009', 'name': 'Home & Kitchen', 'icon': '🍳', 'product_count': 0},
    {'category_id': 'cat-010', 'name': 'Meal Kits', 'icon': '🍱', 'product_count': 0},
    {'category_id': 'cat-011', 'name': 'Pantry Staples', 'icon': '🥫', 'product_count': 0}
]

mock_regions = [
    {
        'region_id': 'reg-001',
        'name': 'West Africa',
        'countries': ['Nigeria', 'Ghana', 'Senegal'],
        'image': 'https://images.unsplash.com/photo-1665332195309-9d75071138f0?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwxfHxBZnJpY2FuJTIwZm9vZHxlbnwwfHx8fDE3NjUwNTMzNDB8MA&ixlib=rb-4.1.0&q=85'
    },
    {
        'region_id': 'reg-002',
        'name': 'East Africa',
        'countries': ['Kenya', 'Ethiopia', 'Tanzania'],
        'image': 'https://images.pexels.com/photos/3213283/pexels-photo-3213283.jpeg'
    },
    {
        'region_id': 'reg-003',
        'name': 'North Africa',
        'countries': ['Morocco', 'Egypt', 'Tunisia'],
        'image': 'https://images.pexels.com/photos/106343/pexels-photo-106343.jpeg'
    },
    {
        'region_id': 'reg-004',
        'name': 'Central America',
        'countries': ['Mexico', 'Guatemala', 'Costa Rica'],
        'image': 'https://images.unsplash.com/photo-1640719028782-8230f1bdc42a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHwzfHxMYXRpbiUyMEFtZXJpY2FuJTIwZm9vZHxlbnwwfHx8fDE3NjUwNTMzNDZ8MA&ixlib=rb-4.1.0&q=85'
    },
    {
        'region_id': 'reg-005',
        'name': 'South America',
        'countries': ['Colombia', 'Brazil', 'Peru'],
        'image': 'https://images.pexels.com/photos/35030234/pexels-photo-35030234.jpeg'
    },
    {
        'region_id': 'reg-006',
        'name': 'Caribbean Latino',
        'countries': ['Dominican Republic', 'Puerto Rico', 'Cuba'],
        'image': 'https://images.unsplash.com/photo-1674669520816-c3c5615dfe51?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHwxfHxMYXRpbiUyMEFtZXJpY2FuJTIwZm9vZHxlbnwwfHx8fDE3NjUwNTMzNDZ8MA&ixlib=rb-4.1.0&q=85'
    }
]

mock_recipes = [
    {
        'recipe_id': 'rec-001',
        'title': 'Nigerian-Mexican Fusion Jollof Tacos',
        'culture': 'Fusion',
        'image': 'https://images.unsplash.com/photo-1640718862942-e18cc8873892?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHw0fHxMYXRpbiUyMEFtZXJpY2FuJTIwZm9vZHxlbnwwfHx8fDE3NjUwNTMzNDZ8MA&ixlib=rb-4.1.0&q=85',
        'description': 'A delicious fusion of Nigerian Jollof rice served in Mexican tacos',
        'cook_time': '45 mins',
        'difficulty': 'Medium',
        'ingredients': ['Jollof rice mix', 'Tortillas', 'Chicken', 'Onions', 'Peppers'],
        'instructions': ['Cook Jollof rice', 'Prepare chicken', 'Warm tortillas', 'Assemble tacos'],
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'recipe_id': 'rec-002',
        'title': 'Ethiopian Coffee Ceremony',
        'culture': 'African',
        'image': 'https://images.pexels.com/photos/3213283/pexels-photo-3213283.jpeg',
        'description': 'Traditional Ethiopian coffee ceremony with roasting and brewing',
        'cook_time': '60 mins',
        'difficulty': 'Advanced',
        'ingredients': ['Ethiopian coffee beans', 'Water', 'Sugar'],
        'instructions': ['Roast beans', 'Grind beans', 'Brew coffee', 'Serve'],
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    },
    {
        'recipe_id': 'rec-003',
        'title': 'Dominican Platos Favoritos',
        'culture': 'Latino',
        'image': 'https://images.pexels.com/photos/2843394/pexels-photo-2843394.jpeg',
        'description': 'Classic Dominican dishes featuring rice, beans, and plantains',
        'cook_time': '90 mins',
        'difficulty': 'Medium',
        'ingredients': ['Rice', 'Black beans', 'Plantains', 'Chicken'],
        'instructions': ['Cook rice', 'Prepare beans', 'Fry plantains', 'Cook chicken'],
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
]

mock_testimonials = [
    {
        'testimonial_id': 'test-001',
        'name': 'Amara Johnson',
        'location': 'Moncton, NB',
        'culture': 'African',
        'rating': 5,
        'text': 'Finally found authentic Nigerian ingredients in Moncton! The Egusi and Jollof rice mix are perfect.',
        'avatar': 'https://images.pexels.com/photos/6305734/pexels-photo-6305734.jpeg'
    },
    {
        'testimonial_id': 'test-002',
        'name': 'Carlos Rodriguez',
        'location': 'Moncton, NB',
        'culture': 'Latino',
        'rating': 5,
        'text': 'Best place for authentic Mexican and Colombian products. Fast delivery and great quality!',
        'avatar': 'https://images.pexels.com/photos/4965326/pexels-photo-4965326.jpeg'
    },
    {
        'testimonial_id': 'test-003',
        'name': 'Fatima Santos',
        'location': 'Moncton, NB',
        'culture': 'Fusion',
        'rating': 5,
        'text': 'Love discovering new fusion recipes. This marketplace brings my African and Latino heritage together.',
        'avatar': 'https://images.unsplash.com/photo-1578203657036-746e6c4eb3b1?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHwyfHxkaXZlcnNlJTIwY3Vpc2luZXxlbnwwfHx8fDE3NjUwNTMzNTJ8MA&ixlib=rb-4.1.0&q=85'
    }
]

async def seed_database():
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.getenv('DB_NAME', 'test_database')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Clear existing data
    await db.products.delete_many({})
    await db.categories.delete_many({})
    await db.regions.delete_many({})
    await db.recipes.delete_many({})
    await db.testimonials.delete_many({})
    
    # Insert seed data
    await db.products.insert_many(mock_products)
    await db.categories.insert_many(mock_categories)
    await db.regions.insert_many(mock_regions)
    await db.recipes.insert_many(mock_recipes)
    await db.testimonials.insert_many(mock_testimonials)
    
    # Update category counts
    for category in mock_categories:
        count = await db.products.count_documents({'category': category['name']})
        await db.categories.update_one(
            {'category_id': category['category_id']},
            {'$set': {'product_count': count}}
        )
    
    print('✅ Database seeded successfully!')
    print(f'   - {len(mock_products)} products')
    print(f'   - {len(mock_categories)} categories')
    print(f'   - {len(mock_regions)} regions')
    print(f'   - {len(mock_recipes)} recipes')
    print(f'   - {len(mock_testimonials)} testimonials')
    
    client.close()

if __name__ == '__main__':
    asyncio.run(seed_database())
