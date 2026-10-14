import os
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import (
    FastAPI, Request, Depends, HTTPException, status,
    Form, Response, Query
)
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc

from database import engine, get_db, Base
from models import User, Category, Product, Order, OrderItem
from schemas import (
    UserCreate, UserLogin, UserOut,
    ProductCreate, ProductUpdate, ProductOut,
    CategoryCreate, CategoryOut,
    CartValidateRequest, CartValidationResponse, CartItemValidationResult,
    OrderCreate, OrderOut, OrderUpdateStatus
)
from auth import (
    hash_password, verify_password, create_access_token,
    get_current_user_optional, get_current_user, get_current_admin
)
from seed_data import seed_database


# Lifespan event handler for startup seed and teardown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables exist and seed default catalog on startup
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield


app = FastAPI(
    title="Bamboo Bliss Store",
    description="Artisanal & Sustainable Bamboo Products E-Commerce Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Mount Static Files & Jinja2 Templates
os.makedirs("static/images", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ==============================================================================
# STOREFRONT WEB PAGES (Jinja2)
# ==============================================================================

@app.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    category: Optional[str] = Query(None, description="Category slug filter"),
    q: Optional[str] = Query(None, description="Search query"),
    db: Session = Depends(get_db)
):
    current_user = get_current_user_optional(request, db)
    categories = db.query(Category).all()

    query = db.query(Product).options(joinedload(Product.category))

    current_category_name = None
    if category:
        selected_cat = db.query(Category).filter(Category.slug == category).first()
        if selected_cat:
            query = query.filter(Product.category_id == selected_cat.id)
            current_category_name = selected_cat.name

    if q:
        search_fmt = f"%{q.strip()}%"
        query = query.filter(
            (Product.title.ilike(search_fmt)) |
            (Product.description.ilike(search_fmt)) |
            (Product.eco_material.ilike(search_fmt))
        )

    products = query.order_by(desc(Product.is_featured), Product.id).all()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "current_user": current_user,
            "categories": categories,
            "products": products,
            "current_category_slug": category,
            "current_category_name": current_category_name,
            "search_query": q
        }
    )


@app.get("/products/{product_id}", response_class=HTMLResponse)
def product_detail(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    current_user = get_current_user_optional(request, db)
    product = db.query(Product).options(joinedload(Product.category)).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    related_products = db.query(Product).filter(
        Product.category_id == product.category_id,
        Product.id != product.id
    ).limit(4).all()

    return templates.TemplateResponse(
        request=request,
        name="product.html",
        context={
            "current_user": current_user,
            "product": product,
            "related_products": related_products
        }
    )


@app.get("/cart", response_class=HTMLResponse)
def view_cart(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user_optional(request, db)
    return templates.TemplateResponse(
        request=request,
        name="cart.html",
        context={
            "current_user": current_user
        }
    )


@app.get("/checkout", response_class=HTMLResponse)
def checkout_page(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user_optional(request, db)
    return templates.TemplateResponse(
        request=request,
        name="checkout.html",
        context={
            "current_user": current_user
        }
    )


@app.get("/orders", response_class=HTMLResponse)
def customer_orders(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user_optional(request, db)
    
    if not current_user:
        return RedirectResponse(url="/login?next=/orders", status_code=302)

    orders = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product)
    ).filter(Order.user_id == current_user.id).order_by(desc(Order.created_at)).all()

    return templates.TemplateResponse(
        request=request,
        name="orders.html",
        context={
            "current_user": current_user,
            "orders": orders,
            "single_order": None
        }
    )


@app.get("/orders/{order_id}", response_class=HTMLResponse)
def single_order_confirmation(
    order_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    current_user = get_current_user_optional(request, db)
    order = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product),
        joinedload(Order.user)
    ).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return templates.TemplateResponse(
        request=request,
        name="orders.html",
        context={
            "current_user": current_user,
            "orders": None,
            "single_order": order
        }
    )


# ==============================================================================
# AUTHENTICATION ROUTES (Web & API)
# ==============================================================================

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user_optional(request, db)
    if current_user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"current_user": None}
    )


@app.post("/login")
def login_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "current_user": None,
                "error": "Invalid email or password. Please check your credentials."
            },
            status_code=400
        )

    # Generate JWT
    token = create_access_token({"sub": str(user.id), "email": user.email, "is_admin": user.is_admin})

    # Set Cookie and redirect
    response = RedirectResponse(url="/admin" if user.is_admin else "/", status_code=302)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        max_age=60 * 60 * 24 * 7,
        samesite="lax"
    )
    return response


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user_optional(request, db)
    if current_user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"current_user": None}
    )


@app.post("/register")
def register_post(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    clean_email = email.strip().lower()
    existing = db.query(User).filter(User.email == clean_email).first()
    if existing:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "current_user": None,
                "error": "An account with this email already exists. Please sign in."
            },
            status_code=400
        )

    new_user = User(
        name=name.strip(),
        email=clean_email,
        hashed_password=hash_password(password),
        is_admin=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": str(new_user.id), "email": new_user.email, "is_admin": False})
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        max_age=60 * 60 * 24 * 7,
        samesite="lax"
    )
    return response


@app.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token")
    return response


# ==============================================================================
# CART VALIDATION & CHECKOUT APIS
# ==============================================================================

@app.post("/api/cart/validate", response_model=CartValidationResponse)
def validate_cart_inventory(payload: CartValidateRequest, db: Session = Depends(get_db)):
    """Verifies stock in real-time to prevent overselling."""
    items_result: List[CartItemValidationResult] = []
    errors: List[str] = []
    is_valid = True
    subtotal = 0.0

    for it in payload.items:
        prod = db.query(Product).filter(Product.id == it.product_id).first()
        if not prod:
            errors.append(f"Product #{it.product_id} no longer exists.")
            is_valid = False
            continue

        available = prod.stock
        item_ok = available >= it.quantity and available > 0
        if not item_ok:
            is_valid = False
            if available <= 0:
                errors.append(f"'{prod.title}' is currently out of stock.")
            else:
                errors.append(f"'{prod.title}' only has {available} units available (requested {it.quantity}).")

        line_subtotal = prod.price * it.quantity
        subtotal += line_subtotal

        items_result.append(CartItemValidationResult(
            product_id=prod.id,
            title=prod.title,
            price=prod.price,
            requested_quantity=it.quantity,
            available_stock=prod.stock,
            is_available=item_ok,
            image_url=prod.image_url,
            item_subtotal=line_subtotal
        ))

    shipping = 0.0 if (subtotal > 75.0 or subtotal == 0.0) else 9.99
    tax = round(subtotal * 0.05, 2)
    total = round(subtotal + shipping + tax, 2)

    return CartValidationResponse(
        is_valid=is_valid,
        items=items_result,
        subtotal=round(subtotal, 2),
        shipping=shipping,
        tax=tax,
        total=total,
        errors=errors
    )


@app.post("/api/checkout", response_model=OrderOut)
def checkout_create_order(
    payload: OrderCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Processes order, atomically verifies & decrements stock, records order."""
    if not payload.items:
        raise HTTPException(status_code=400, detail="Cannot place an order with empty cart")

    current_user = get_current_user_optional(request, db)

    # 1. Verify all stock under atomic check
    subtotal = 0.0
    order_items_to_create = []

    for item in payload.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=400,
                detail=f"Product #{item.product_id} not found"
            )
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for '{product.title}'. Only {product.stock} available."
            )
        
        # Deduct stock
        product.stock -= item.quantity
        line_total = product.price * item.quantity
        subtotal += line_total

        order_items_to_create.append({
            "product": product,
            "quantity": item.quantity,
            "price": product.price
        })

    # Calculate final pricing
    shipping = 0.0 if subtotal > 75.0 else 9.99
    tax = round(subtotal * 0.05, 2)
    total_price = round(subtotal + shipping + tax, 2)

    # Create Order
    new_order = Order(
        user_id=current_user.id if current_user else None,
        status="Processing",
        total_price=total_price,
        shipping_address=payload.shipping_address,
        customer_name=payload.customer_name or (current_user.name if current_user else "Customer"),
        customer_email=payload.customer_email or (current_user.email if current_user else "guest@bamboobliss.com"),
        customer_phone=payload.customer_phone,
        notes=payload.notes
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Create OrderItems
    for item_data in order_items_to_create:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item_data["product"].id,
            quantity=item_data["quantity"],
            price=item_data["price"]
        )
        db.add(order_item)

    db.commit()
    db.refresh(new_order)

    # Eagerly load relationship
    full_order = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product)
    ).filter(Order.id == new_order.id).first()

    return full_order


# ==============================================================================
# ADMIN PORTAL & CRUD ROUTES
# ==============================================================================

@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user_optional(request, db)
    if not current_user or not current_user.is_admin:
        return RedirectResponse(url="/login?next=/admin", status_code=302)

    products = db.query(Product).options(joinedload(Product.category)).order_by(Product.id).all()
    categories = db.query(Category).options(joinedload(Category.products)).all()
    orders = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product),
        joinedload(Order.user)
    ).order_by(desc(Order.created_at)).all()

    total_revenue = sum(o.total_price for o in orders if o.status != 'Cancelled')
    low_stock_count = sum(1 for p in products if p.stock < 10)

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "current_user": current_user,
            "products": products,
            "categories": categories,
            "orders": orders,
            "total_revenue": total_revenue,
            "total_orders": len(orders),
            "low_stock_count": low_stock_count
        }
    )


@app.post("/admin/api/products", response_model=ProductOut)
def admin_create_product(
    payload: ProductCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    cat = db.query(Category).filter(Category.id == payload.category_id).first()
    if not cat:
        raise HTTPException(status_code=400, detail="Invalid Category ID")

    new_prod = Product(**payload.model_dump())
    db.add(new_prod)
    db.commit()
    db.refresh(new_prod)
    return new_prod


@app.put("/admin/api/products/{product_id}", response_model=ProductOut)
def admin_update_product(
    product_id: int,
    payload: ProductUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(prod, field, val)

    db.commit()
    db.refresh(prod)
    return prod


@app.delete("/admin/api/products/{product_id}")
def admin_delete_product(
    product_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(prod)
    db.commit()
    return {"detail": "Product deleted successfully"}


@app.post("/admin/api/categories", response_model=CategoryOut)
def admin_create_category(
    payload: CategoryCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    existing = db.query(Category).filter(Category.slug == payload.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category slug already exists")

    new_cat = Category(**payload.model_dump())
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat


@app.post("/admin/api/orders/{order_id}/status")
def admin_update_order_status(
    order_id: int,
    payload: OrderUpdateStatus,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = payload.status
    db.commit()
    return {"order_id": order.id, "status": order.status}


# ==============================================================================
# REST API FOR PRODUCTS & CATEGORIES
# ==============================================================================

@app.get("/api/products", response_model=List[ProductOut])
def get_products_api(
    category: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product).options(joinedload(Product.category))
    if category:
        cat = db.query(Category).filter(Category.slug == category).first()
        if cat:
            query = query.filter(Product.category_id == cat.id)
    if q:
        query = query.filter(Product.title.ilike(f"%{q}%"))
    return query.all()


@app.get("/api/products/{product_id}", response_model=ProductOut)
def get_single_product_api(product_id: int, db: Session = Depends(get_db)):
    prod = db.query(Product).options(joinedload(Product.category)).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod
