# 🎋 Rukumani Bamboo Shop - Master Project Documentation & Operation Manual

A production-ready, decoupled e-commerce web application dedicated to handcrafted bamboo furniture, hanging swings, cane sofa sets, and eco-friendly homeware from **Rukumani Bamboo Shop**, Konganapuram, Salem, Tamil Nadu.

---

## 📑 Table of Contents

1. [🖥️ Live Server Execution & Terminal Overview](#️-live-server-execution--terminal-overview)
2. [🌟 Store Highlights & Workshop Details](#-store-highlights--workshop-details)
3. [🏗️ Decoupled Architecture & System Flow](#️-decoupled-architecture--system-flow)
4. [💰 Product Catalog & Indian Rupee (INR / ₹) Pricing](#-product-catalog--indian-rupee-inr---pricing)
5. [💳 Multi-Payment & Card Checkout Engine](#-multi-payment--card-checkout-engine)
6. [🔐 Authentication, Roles & Session Management](#-authentication-roles--session-management)
7. [📂 Project Directory Layout](#-project-directory-layout)
8. [🚀 Step-by-Step Execution Guide](#-step-by-step-execution-guide)
9. [📡 Complete REST API Reference](#-complete-rest-api-reference)
10. [🧪 Automated End-to-End Testing](#-automated-end-to-end-testing)
11. [🛠️ Terminal Logs Analysis & Troubleshooting](#️-terminal-logs-analysis--troubleshooting)

---

## 🖥️ Live Server Execution & Terminal Overview

The server runs on **FastAPI** with **Uvicorn** and auto-reloading enabled.

### Terminal Startup Command:
```powershell
cd backend
python run.py
```

### Live Runtime Behavior & Log Flow:
```text
[*] Starting Bamboo Bliss Backend on http://127.0.0.1:8000 ...
INFO:     Will watch for changes in these directories: ['E:\\Development two\\backend']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process using WatchFiles
INFO:     Started server process
INFO:     Waiting for application startup.
[OK] Product images copied to frontend/images/
[OK] Backend database seeded successfully
INFO:     Application startup complete.

# Live HTTP Traffic & API Transactions:
INFO:     GET / HTTP/1.1 200 OK                        # Storefront loaded
INFO:     GET /api/categories HTTP/1.1 200 OK          # Categories fetched
INFO:     GET /api/products HTTP/1.1 200 OK            # Product catalog fetched
INFO:     POST /api/auth/register HTTP/1.1 200 OK      # Customer registered
INFO:     POST /api/cart/validate HTTP/1.1 200 OK      # Real-time stock checked
INFO:     GET /checkout.html HTTP/1.1 200 OK           # Checkout page loaded
INFO:     POST /api/auth/logout HTTP/1.1 200 OK        # Safe sign out
```

---

## 🌟 Store Highlights & Workshop Details

- **Business Name**: `Rukumani Bamboo Shop`
- **Location**: Moolapathai, Omalur to Sankagiri Main Road, Konganapuram, Edappadi Tk, Salem Dt - 637101, Tamil Nadu.
- **Phone & WhatsApp**: `+91 98653 56650`
- **Workshop Direct Hours**: Monday – Sunday: `8:00 AM – 9:00 PM`
- **Key Offerings**:
  - Direct artisan workshop pricing with zero middleman markup.
  - Reinforced, seasoned bamboo with organic non-toxic finishes.
  - On-time safe delivery across Tamil Nadu with protective packaging.
  - Free delivery on orders over **₹999**.

---

## 🏗️ Decoupled Architecture & System Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser Client (HTML5/JS)                │
│                                                             │
│   • Storefront (index.html)    • Product View (product.html)│
│   • Shopping Bag (cart.html)   • Checkout (checkout.html)   │
│   • Order History (orders.html)• Admin Hub (admin.html)     │
└──────────────┬───────────────────────────────▲──────────────┘
               │ HTTP / JSON API               │ Response Data
               ▼                               │
┌──────────────────────────────────────────────┴──────────────┐
│                    FastAPI Backend (Uvicorn)                │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ CORS Middleware & JWT Auth Dependency               │   │
│   └──────────────────────────┬──────────────────────────┘   │
│                              │                              │
│   ┌──────────────────────────▼──────────────────────────┐   │
│   │ REST API Routers:                                   │   │
│   │  • /api/auth         • /api/products                │   │
│   │  • /api/categories   • /api/cart (Validation)      │   │
│   │  • /api/checkout     • /api/orders                  │   │
│   │  • /api/admin        • /images (Static Mount)       │   │
│   └──────────────────────────┬──────────────────────────┘   │
│                              │ SQLAlchemy ORM               │
│                              ▼                              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ SQLite Database (`bamboo_store.db`)                 │   │
│   │ (Users, Categories, Products, Orders, OrderItems)   │   │
│   └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 💰 Product Catalog & Indian Rupee (INR / ₹) Pricing

All products in the database use Indian Rupee (₹) rates with image mapping:

| ID | Product Title | Category | Workshop Price | Stock | Image File |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | Handcrafted Bamboo Serving Platter Tray | Kitchenware & Dining | **₹649** | 28 | `tray.jpg` |
| **2** | Artisanal Woven Bamboo & Cane Mudda Stool | Furniture | **₹1,299** | 16 | `mudda_stool.jpg` |
| **3** | Contoured Amphora Bamboo Vase & Urn | Home Decor | **₹899** | 14 | `urn_vase.jpg` |
| **4** | Vacuum Insulated Bamboo Thermal Flask (500ml) | Kitchenware & Dining | **₹799** | 45 | `flask.jpg` |
| **5** | Vintage Bamboo Cane Lounge Armchair | Furniture | **₹3,499** | 9 | `armchair.jpg` |
| **6** | Boho Bamboo Cane Hanging Swing Chair (Jhula) | Furniture | **₹4,899** | 6 | `swing_chair.jpg` |
| **7** | Bamboo Cane Mudda Lounge Chair & Stool Set | Furniture | **₹4,299** | 8 | `chair_set.jpg` |
| **8** | Biodegradable Charcoal Toothbrushes (4-Pack) | Personal Care | **₹199** | 70 | `toothbrush.jpg` |

---

## 🛒 Streamlined Express Checkout Engine

The `/checkout.html` page provides a fast, frictionless ordering experience:

1. **Customer Contact Info**: Full Name, Email Address, Mobile / WhatsApp number.
2. **Delivery Destination**: Door number, Street address, City (Salem), State (Tamil Nadu), Pincode (637101), and custom artisan delivery notes.
3. **Real-Time Stock Check (`POST /api/cart/validate`)**: Verifies item availability before checkout.
4. **Atomic Order Placement (`POST /api/checkout`)**: Deducts inventory atomically in SQLite transaction.
5. **Confirmation & Live Tracking**: Instantly clears bag and routes to `/orders.html?id=<order_id>`.

---

## 🔐 Authentication, Roles & Session Management

- **Hashing**: Passwords encrypted with `bcrypt`.
- **JWT**: Stateless tokens signed with `HS256`.
- **Global `window.API` Export**: Guaranteed execution for all inline event handlers.
- **Fail-Safe Sign Out**: `API.logout()` wipes `bamboo_jwt_token`, `bamboo_user_data`, `sessionStorage`, and expired cookies, redirecting immediately to `/login.html`.

### Default Demo Logins:
| Role | Email | Password | Privileges |
| :--- | :--- | :--- | :--- |
| **Store Admin** | `admin@bamboobliss.com` | `admin123` | Full access to `/admin.html`, product CRUD, order status updates |
| **Customer** | `customer@bamboobliss.com` | `password123` | Bag checkout, order history, delivery tracking |

---

## 📂 Project Directory Layout

```
e:\Development two\
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, static mounts, CORS, router inclusion
│   │   ├── config.py            # SQLite database path & JWT secret configs
│   │   ├── database.py          # SQLAlchemy connection & session dependency
│   │   ├── models/              # User, Category, Product, Order, OrderItem models
│   │   ├── schemas/             # Pydantic validation schemas
│   │   ├── routers/             # auth, products, categories, cart, checkout, orders, admin
│   │   └── utils/
│   │       ├── auth.py          # Password hashing & JWT issuance
│   │       └── seed.py          # Auto-seeding catalog (INR) & image copier
│   ├── requirements.txt         # Dependencies
│   ├── run.py                   # Server startup runner (Port 8000)
│   └── bamboo_store.db          # Active SQLite database file
│
├── frontend/
│   ├── index.html               # Storefront with Salem branding & WhatsApp buttons
│   ├── product.html             # Product details with INR price & WhatsApp buy
│   ├── cart.html                # Full cart with INR calculation & promo code
│   ├── checkout.html            # 3-step checkout with Card details & UPI
│   ├── orders.html              # Customer order history & 4-step delivery tracker
│   ├── login.html               # Login with 1-click demo filler buttons
│   ├── register.html            # Account registration
│   ├── admin.html               # Admin Dashboard (KPIs, Products CRUD, Orders)
│   ├── css/custom.css           # Styling & animations
│   ├── js/
│   │   ├── api.js               # Centralized REST API client & JWT token manager
│   │   ├── cart.js              # Bag state, user dropdown & toast notifications
│   │   └── admin.js             # Admin dashboard controller
│   └── images/                  # Master bamboo product photos
│
├── images/                      # Raw original images
├── test_e2e.py                  # 15-point End-to-End automated test suite
└── README.md                    # Complete project documentation
```

---

## 🚀 Step-by-Step Execution Guide

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Start the Backend Server
```powershell
cd backend
python run.py
```

### 3. Open in Browser
- 🛍️ **Storefront**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- 👑 **Admin Portal**: [http://127.0.0.1:8000/admin.html](http://127.0.0.1:8000/admin.html)
- 📦 **Order Tracking**: [http://127.0.0.1:8000/orders.html](http://127.0.0.1:8000/orders.html)
- 📖 **Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📡 Complete REST API Reference

| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Register new customer account | Public |
| `POST` | `/api/auth/login` | Authenticate email/password & issue JWT | Public |
| `GET` | `/api/auth/me` | Return current logged-in profile | Bearer Token |
| `POST` | `/api/auth/logout` | Terminate session & clear cookies | Public |
| `GET` | `/api/categories` | List all product categories | Public |
| `GET` | `/api/products` | Query products (`?category=...`, `?q=...`) | Public |
| `GET` | `/api/products/{id}` | Get product details by ID | Public |
| `POST` | `/api/cart/validate` | Verify inventory stock in real-time | Public |
| `POST` | `/api/checkout` | Deduct stock atomically & create Order | Customer / User |
| `GET` | `/api/orders` | List orders for current user | Customer / User |
| `GET` | `/api/orders/{id}` | Get order details & tracking status | Customer / User |
| `GET` | `/api/admin/stats` | Lifetime revenue, orders & low stock counts | Admin |
| `POST` | `/api/admin/products` | Create new bamboo product | Admin |
| `PUT` | `/api/admin/products/{id}`| Update product price, stock or details | Admin |
| `DELETE` | `/api/admin/products/{id}`| Delete product from catalog | Admin |
| `GET` | `/api/admin/orders` | Retrieve all customer orders | Admin |
| `PUT` | `/api/admin/orders/{id}/status` | Update fulfillment state (`Pending`..`Delivered`) | Admin |

---

## 🧪 Automated End-to-End Testing

Run the automated integration test suite:

```powershell
python test_e2e.py
```

### Verified Scenarios:
1. ✅ Frontend static file delivery
2. ✅ Product search & category filtering
3. ✅ Single product detail retrieval
4. ✅ Customer user registration & JWT generation
5. ✅ Cart stock validation for valid & over-limit quantities
6. ✅ Atomic checkout & inventory reduction in database
7. ✅ Order history & status progression
8. ✅ Admin dashboard stats & product CRUD operations
9. ✅ Admin order status updating

---

## 🛠️ Terminal Logs Analysis & Troubleshooting

### Understanding Server Logs:
- `200 OK`: Request succeeded.
- `304 Not Modified`: Cached static resource (CSS/JS/images) reused for optimal speed.
- `WatchFiles detected changes ... Reloading`: Auto-reloader updated python modules without requiring server restart.

### Quick Database Reset:
To restore default starter data:
```powershell
Remove-Item backend/bamboo_store.db -ErrorAction SilentlyContinue
python backend/run.py
```

---

## 🌿 Credits & License
- **Workshop**: Rukumani Bamboo Shop, Konganapuram, Salem, Tamil Nadu.
- **Stack**: FastAPI + SQLAlchemy ORM + SQLite + Tailwind CSS + Vanilla JS.
