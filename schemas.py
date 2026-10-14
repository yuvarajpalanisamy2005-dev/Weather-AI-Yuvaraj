from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

# ----------------- User Schemas -----------------
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    id: int
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ----------------- Category Schemas -----------------
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    image_url: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class CategoryOut(CategoryBase):
    id: int
    product_count: Optional[int] = 0

    class Config:
        from_attributes = True


# ----------------- Product Schemas -----------------
class ProductBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: str
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    category_id: int
    image_url: str
    is_featured: bool = False
    eco_material: Optional[str] = "100% Organic Bamboo"

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    is_featured: Optional[bool] = None
    eco_material: Optional[str] = None

class ProductOut(ProductBase):
    id: int
    created_at: datetime
    category: Optional[CategoryBase] = None

    class Config:
        from_attributes = True


# ----------------- Cart & Checkout Validation -----------------
class CartItemInput(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)

class CartValidateRequest(BaseModel):
    items: List[CartItemInput]

class CartItemValidationResult(BaseModel):
    product_id: int
    title: str
    price: float
    requested_quantity: int
    available_stock: int
    is_available: bool
    image_url: str
    item_subtotal: float

class CartValidationResponse(BaseModel):
    is_valid: bool
    items: List[CartItemValidationResult]
    subtotal: float
    shipping: float
    tax: float
    total: float
    errors: List[str] = []


# ----------------- Order Schemas -----------------
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)

class OrderCreate(BaseModel):
    shipping_address: str = Field(..., min_length=5)
    customer_name: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    customer_phone: Optional[str] = None
    notes: Optional[str] = None
    items: List[OrderItemCreate]

class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    product: Optional[ProductOut] = None

    class Config:
        from_attributes = True

class OrderUpdateStatus(BaseModel):
    status: str = Field(..., pattern="^(Pending|Processing|Shipped|Delivered|Cancelled)$")

class OrderOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    status: str
    total_price: float
    shipping_address: str
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    items: List[OrderItemOut] = []

    class Config:
        from_attributes = True
