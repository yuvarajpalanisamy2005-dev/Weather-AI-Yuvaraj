import os
import shutil
from pathlib import Path
from database import engine, SessionLocal, Base
from models import User, Category, Product, Order, OrderItem
from auth import hash_password

def copy_images():
    """Copy images from workspace images/ to static/images/."""
    src_dir = Path("images")
    dst_dir = Path("static/images")
    dst_dir.mkdir(parents=True, exist_ok=True)

    mapping = {
        "bamboo image 1.jpeg": "tray.jpg",
        "bamboo image2.jpeg": "mudda_stool.jpg",
        "bamboo imge 3.jpeg": "urn_vase.jpg",
        "bamboo image 4.jpeg": "flask.jpg",
        "baboo image 5.jpeg": "armchair.jpg",
        "bamboo image 6.jpeg": "swing_chair.jpg",
        "baboo image 7.jpeg": "chair_set.jpg",
        "bamboo image 8.jpeg": "toothbrush.jpg",
    }

    if src_dir.exists():
        for src_file in src_dir.iterdir():
            if src_file.is_file():
                # Copy exact file
                shutil.copy2(src_file, dst_dir / src_file.name)
                # Copy named alias if mapped
                if src_file.name in mapping:
                    shutil.copy2(src_file, dst_dir / mapping[src_file.name])
        print("[OK] Product images copied successfully to static/images/")
    else:
        print("[WARN] Source images directory not found.")

def seed_database():
    """Initialize tables and populate starter seed data."""
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    copy_images()

    db = SessionLocal()
    try:
        # 1. Seed Users
        admin_email = "admin@bamboobliss.com"
        customer_email = "customer@bamboobliss.com"
        shopper_email = "eco_shopper@bamboobliss.com"

        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(
                name="Admin Artisan",
                email=admin_email,
                hashed_password=hash_password("admin123"),
                is_admin=True
            )
            db.add(admin)

        customer = db.query(User).filter(User.email == customer_email).first()
        if not customer:
            customer = User(
                name="Priya Sharma",
                email=customer_email,
                hashed_password=hash_password("password123"),
                is_admin=False
            )
            db.add(customer)

        shopper = db.query(User).filter(User.email == shopper_email).first()
        if not shopper:
            shopper = User(
                name="Liam Green",
                email=shopper_email,
                hashed_password=hash_password("password123"),
                is_admin=False
            )
            db.add(shopper)

        db.commit()
        db.refresh(admin)
        db.refresh(customer)

        # 2. Seed Categories
        categories_data = [
            {
                "name": "Furniture",
                "slug": "furniture",
                "description": "Artisanal bamboo armchairs, mudda stools, hanging swing chairs, and handcrafted lounge sets.",
                "image_url": "/static/images/armchair.jpg"
            },
            {
                "name": "Kitchenware & Dining",
                "slug": "kitchenware",
                "description": "Sustainable woven serving platters, insulated thermal flasks, and eco-friendly kitchen essentials.",
                "image_url": "/static/images/tray.jpg"
            },
            {
                "name": "Home Decor",
                "slug": "home-decor",
                "description": "Intricate bamboo vases, decorative urns, botanical planters, and natural accent craftsmanship.",
                "image_url": "/static/images/urn_vase.jpg"
            },
            {
                "name": "Personal Care",
                "slug": "personal-care",
                "description": "Zero-waste, biodegradable charcoal-infused bamboo toothbrushes and eco-conscious hygiene goods.",
                "image_url": "/static/images/toothbrush.jpg"
            },
        ]

        cat_map = {}
        for cat in categories_data:
            existing = db.query(Category).filter(Category.slug == cat["slug"]).first()
            if not existing:
                existing = Category(**cat)
                db.add(existing)
                db.commit()
                db.refresh(existing)
            cat_map[cat["slug"]] = existing

        # 3. Seed Products mapped to analyzed images
        products_data = [
            {
                "title": "Handcrafted Bamboo Serving Platter Tray",
                "description": "Artisanal eco-friendly rectangular handwoven bamboo platter tray with raised reinforced edges. Ideal for serving refreshments, morning breakfast, fruit displays, or rustic table organizing. Finished with a food-safe natural organic polish.",
                "price": 649.00,
                "stock": 28,
                "category_id": cat_map["kitchenware"].id,
                "image_url": "/static/images/tray.jpg",
                "is_featured": True,
                "eco_material": "100% Organic Golden Bamboo"
            },
            {
                "title": "Artisanal Woven Bamboo & Cane Mudda Stool",
                "description": "Sturdy low-sitting traditional bamboo mudda ottoman with intricate geometric black-and-natural cane weave patterns. Reinforced core framework comfortably supports up to 130kg while providing bohemian seating charm.",
                "price": 1299.00,
                "stock": 16,
                "category_id": cat_map["furniture"].id,
                "image_url": "/static/images/mudda_stool.jpg",
                "is_featured": True,
                "eco_material": "Seasoned Bamboo & Natural Cane Reed"
            },
            {
                "title": "Contoured Amphora Bamboo Vase & Urn",
                "description": "Exquisitely contoured decorative bamboo amphora vase featuring delicate lattice weave detailing. Adds warm organic texture to dining tables, mantlepieces, or botanical corners. Hand-braided rim trim.",
                "price": 899.00,
                "stock": 14,
                "category_id": cat_map["home-decor"].id,
                "image_url": "/static/images/urn_vase.jpg",
                "is_featured": False,
                "eco_material": "Split Natural Bamboo Fibers"
            },
            {
                "title": "Vacuum Insulated Bamboo Thermal Flask (500ml)",
                "description": "Double-wall food-grade 304 stainless steel vacuum flask clad in authentic hand-finished natural grain bamboo. Keeps beverages piping hot for 12 hours or chilled for 24 hours. Includes stainless steel tea infuser filter.",
                "price": 799.00,
                "stock": 45,
                "category_id": cat_map["kitchenware"].id,
                "image_url": "/static/images/flask.jpg",
                "is_featured": True,
                "eco_material": "Natural Moso Bamboo & 304 Stainless Steel"
            },
            {
                "title": "Vintage Bamboo Cane Lounge Armchair",
                "description": "Handcrafted bohemian accent armchair featuring an arched sunburst fan backrest, supportive wraparound arms, and non-slip rubber floor caps. Masterfully constructed by traditional cane craftsmen.",
                "price": 3499.00,
                "stock": 9,
                "category_id": cat_map["furniture"].id,
                "image_url": "/static/images/armchair.jpg",
                "is_featured": True,
                "eco_material": "Solid Bamboo Poles & Flexible Cane Weave"
            },
            {
                "title": "Boho Bamboo Cane Hanging Swing Chair (Jhula)",
                "description": "Luxurious suspended cane swing chair with geometric mandala backrest pattern and heavy-duty load-bearing bamboo loop frame. Designed for serene indoor reading corners, sunrooms, or shaded patios.",
                "price": 4899.00,
                "stock": 6,
                "category_id": cat_map["furniture"].id,
                "image_url": "/static/images/swing_chair.jpg",
                "is_featured": True,
                "eco_material": "Heavy-Duty Heat-Treated Bamboo Cane"
            },
            {
                "title": "Bamboo Cane Mudda Lounge Chair & Stool Set",
                "description": "Complete 2-piece lounge ensemble including an ergonomic high-back bamboo cane armchair and a matching geometric mudda table/footstool. Perfect for creating a sustainable sanctuary at home.",
                "price": 4299.00,
                "stock": 8,
                "category_id": cat_map["furniture"].id,
                "image_url": "/static/images/chair_set.jpg",
                "is_featured": False,
                "eco_material": "Organic Bamboo & Cane Bindings"
            },
            {
                "title": "Biodegradable Charcoal Bamboo Toothbrushes (4-Pack)",
                "description": "Pack of 4 eco-conscious organic bamboo toothbrushes with smooth water-resistant handles and ultra-soft activated charcoal-infused bristles. 100% biodegradable and zero-plastic packaging.",
                "price": 199.00,
                "stock": 70,
                "category_id": cat_map["personal-care"].id,
                "image_url": "/static/images/toothbrush.jpg",
                "is_featured": False,
                "eco_material": "Compostable Moso Bamboo & Charcoal Bristles"
            },
        ]

        created_products = []
        for prod in products_data:
            existing = db.query(Product).filter(Product.title == prod["title"]).first()
            if not existing:
                existing = Product(**prod)
                db.add(existing)
                db.commit()
                db.refresh(existing)
            else:
                existing.price = prod["price"]
                existing.eco_material = prod["eco_material"]
                db.commit()
            created_products.append(existing)

        # 4. Seed initial sample order for Customer
        if db.query(Order).count() == 0 and customer:
            sample_order = Order(
                user_id=customer.id,
                status="Processing",
                total_price=1448.00,
                shipping_address="12, Gandhi Nagar, Near New Bus Stand, Salem - 636004, Tamil Nadu",
                customer_name=customer.name,
                customer_email=customer.email,
                customer_phone="+91 98653 56650",
                notes="Please call before delivery."
            )
            db.add(sample_order)
            db.commit()
            db.refresh(sample_order)

            # Add OrderItems
            item1 = OrderItem(
                order_id=sample_order.id,
                product_id=created_products[0].id,  # Tray
                quantity=1,
                price=created_products[0].price
            )
            item2 = OrderItem(
                order_id=sample_order.id,
                product_id=created_products[3].id,  # Flask
                quantity=1,
                price=created_products[3].price
            )
            db.add_all([item1, item2])
            db.commit()
            print("[OK] Sample customer order seeded")

        print("[OK] Database successfully seeded with categories, products, and default accounts.")
    except Exception as e:
        print(f"[ERROR] Error during database seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
