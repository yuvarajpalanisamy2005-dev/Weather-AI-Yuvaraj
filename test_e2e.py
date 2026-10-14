import json
import urllib.request
import urllib.parse
import http.cookiejar

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("==================================================")
    print("  RUNNING DECOUPLED FULL-STACK VERIFICATION TEST  ")
    print("==================================================")

    # 1. Test Static Frontend Serving
    with urllib.request.urlopen(f"{BASE_URL}/") as response:
        assert response.status == 200
        html = response.read().decode('utf-8')
        assert "Rukumani Bamboo Shop" in html or "Bamboo" in html
        print("[PASS] 1. Static Frontend served successfully (index.html)")

    # 2. Test GET /api/products
    with urllib.request.urlopen(f"{BASE_URL}/api/products") as response:
        assert response.status == 200
        products = json.loads(response.read().decode('utf-8'))
        assert len(products) >= 8
        assert any(p["title"] == "Handcrafted Bamboo Serving Platter Tray" for p in products)
        assert any(p["title"] == "Vintage Bamboo Cane Lounge Armchair" for p in products)
        print(f"[PASS] 2. Products API returned {len(products)} products mapped to images")

    # 3. Test GET /api/products/1
    with urllib.request.urlopen(f"{BASE_URL}/api/products/1") as response:
        assert response.status == 200
        prod = json.loads(response.read().decode('utf-8'))
        assert prod["id"] == 1
        assert prod["price"] > 0
        assert prod["stock"] > 0
        print(f"[PASS] 3. Single Product API: '{prod['title']}' (${prod['price']}, Stock: {prod['stock']})")

    # 4. Test GET /api/categories
    with urllib.request.urlopen(f"{BASE_URL}/api/categories") as response:
        assert response.status == 200
        cats = json.loads(response.read().decode('utf-8'))
        assert len(cats) >= 4
        cat_names = [c["name"] for c in cats]
        assert "Furniture" in cat_names
        assert "Kitchenware & Dining" in cat_names
        print(f"[PASS] 4. Categories API returned: {', '.join(cat_names)}")

    # 5. Test POST /api/cart/validate
    cart_data = json.dumps({
        "items": [
            {"product_id": 1, "quantity": 2},
            {"product_id": 4, "quantity": 1}
        ]
    }).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}/api/cart/validate",
        data=cart_data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        cart_res = json.loads(response.read().decode('utf-8'))
        assert cart_res["is_valid"] is True
        assert cart_res["subtotal"] > 0
        assert cart_res["total"] > 0
        print(f"[PASS] 5. Real-time Cart Validation API: Subtotal=${cart_res['subtotal']}, Total=${cart_res['total']}")

    # 6. Test POST /api/checkout
    chk_data = json.dumps({
        "customer_name": "Elena Green",
        "customer_email": "elena.green@example.com",
        "customer_phone": "+1 (555) 432-1098",
        "shipping_address": "45 Bamboo Way, Eco Valley, OR 97201",
        "notes": "Please place in front garden porch",
        "items": [
            {"product_id": 1, "quantity": 1},
            {"product_id": 2, "quantity": 1}
        ]
    }).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}/api/checkout",
        data=chk_data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        order = json.loads(response.read().decode('utf-8'))
        order_id = order["id"]
        assert order["status"] == "Processing"
        assert len(order["items"]) == 2
        print(f"[PASS] 6. Atomic Checkout placed Order #{order_id} (Total: ${order['total_price']})")

    # 7. Test GET /api/orders/{order_id}
    with urllib.request.urlopen(f"{BASE_URL}/api/orders/{order_id}") as response:
        assert response.status == 200
        order_data = json.loads(response.read().decode('utf-8'))
        assert order_data["id"] == order_id
        assert order_data["status"] == "Processing"
        print(f"[PASS] 7. Order Tracking API confirmed Order #{order_id}")

    # 8. Test POST /api/auth/login (Admin)
    login_data = json.dumps({
        "email": "admin@bamboobliss.com",
        "password": "admin123"
    }).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}/api/auth/login",
        data=login_data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        auth_res = json.loads(response.read().decode('utf-8'))
        token = auth_res["access_token"]
        assert token is not None
        assert auth_res["user"]["is_admin"] is True
        print("[PASS] 8. Admin authenticated with JWT Bearer Token")

    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # 9. Test GET /api/admin/stats
    req = urllib.request.Request(f"{BASE_URL}/api/admin/stats", headers=auth_headers)
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        stats = json.loads(response.read().decode('utf-8'))
        assert stats["total_revenue"] > 0
        assert stats["total_orders"] >= 2
        print(f"[PASS] 9. Admin Stats API: Revenue=${stats['total_revenue']}, Orders={stats['total_orders']}")

    # 10. Test GET /api/admin/orders
    req = urllib.request.Request(f"{BASE_URL}/api/admin/orders", headers=auth_headers)
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        orders_list = json.loads(response.read().decode('utf-8'))
        assert len(orders_list) >= 2
        print(f"[PASS] 10. Admin Orders API returned {len(orders_list)} customer orders")

    # 11. Test POST /api/admin/orders/{id}/status
    status_data = json.dumps({"status": "Shipped"}).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}/api/admin/orders/{order_id}/status",
        data=status_data,
        headers=auth_headers
    )
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        res = json.loads(response.read().decode('utf-8'))
        assert res["status"] == "Shipped"
        print(f"[PASS] 11. Admin updated Order #{order_id} status to 'Shipped'")

    # 12. Test POST /api/admin/products (Create)
    prod_create_data = json.dumps({
        "title": "Artisanal Bamboo Tea Coaster Set (6-Pack)",
        "description": "Natural hand-carved bamboo tea coasters with water-resistant cork base.",
        "price": 18.50,
        "stock": 35,
        "category_id": 2,
        "image_url": "/images/tray.jpg",
        "is_featured": True,
        "eco_material": "100% Solid Moso Bamboo"
    }).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}/api/admin/products",
        data=prod_create_data,
        headers=auth_headers
    )
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        new_prod = json.loads(response.read().decode('utf-8'))
        new_prod_id = new_prod["id"]
        assert new_prod["title"] == "Artisanal Bamboo Tea Coaster Set (6-Pack)"
        print(f"[PASS] 12. Admin created Product #{new_prod_id}")

    # 13. Test PUT /api/admin/products/{id} (Update Stock)
    stock_update_data = json.dumps({"stock": 50}).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}/api/admin/products/{new_prod_id}",
        data=stock_update_data,
        headers=auth_headers,
        method="PUT"
    )
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        updated = json.loads(response.read().decode('utf-8'))
        assert updated["stock"] == 50
        print(f"[PASS] 13. Admin updated Product #{new_prod_id} stock to 50 units")

    # 14. Test DELETE /api/admin/products/{id}
    req = urllib.request.Request(
        f"{BASE_URL}/api/admin/products/{new_prod_id}",
        headers=auth_headers,
        method="DELETE"
    )
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        print(f"[PASS] 14. Admin deleted Product #{new_prod_id} successfully")

    # 15. Test POST /api/auth/register (Customer)
    import time
    reg_email = f"eco_user_{int(time.time())}@example.com"
    reg_data = json.dumps({
        "name": "David Eco",
        "email": reg_email,
        "password": "securepassword123"
    }).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}/api/auth/register",
        data=reg_data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        reg_res = json.loads(response.read().decode('utf-8'))
        assert reg_res["user"]["email"] == reg_email
        print(f"[PASS] 15. Customer registration API verified ({reg_email})")

    print("\n==================================================")
    print("      ALL 15 FULL-STACK TESTS PASSED (100%)       ")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
