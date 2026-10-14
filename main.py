
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from Database import *
from Schema import (
    UserCreate,
    UserOut,
    ProductCreate,
    ProductOut,
    CartItemCreate,
    CartItemOut,
    OrderOut
)

app = FastAPI(title="E-Commerce Shopping API")


# Home route
@app.get("/")
def home():
    return {"message": "Welcome to E-Commerce API"}


# Create user
@app.post("/users", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    rec = db.query(User).filter(
        User.email == user.email
    ).first()

    if rec:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(name=user.name, email=user.email)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# Get all users
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


# Add product
@app.post("/products")
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    if product.price < 0 or product.stock < 0:
        raise HTTPException(
            status_code=400,
            detail="Price and stock cannot be negative"
        )

    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


# Get all products
@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


# Add product to cart
@app.post("/cart")
def add_to_cart(
    item: CartItemCreate,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.id == item.user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    product = db.query(Product).filter(
        Product.id == item.product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if item.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero"
        )

    if item.quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail="Not enough stock available"
        )

    cart_item = CartItem(
        user_id=item.user_id,
        product_id=item.product_id,
        quantity=item.quantity
    )

    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)

    return cart_item


# View a user's cart
@app.get("/cart/{user_id}")
def get_cart(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return db.query(CartItem).filter(
        CartItem.user_id == user_id
    ).all()


# Create order from cart

@app.post("/orders/{user_id}")
def create_order(user_id: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cart_items = db.query(CartItem).filter(
        CartItem.user_id == user_id
    ).all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total = 0  # Initialize total before using it

    # Check products and calculate total
    for cart_item in cart_items:
        product = db.query(Product).filter(
            Product.id == cart_item.product_id
        ).first()

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        if cart_item.quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {product.name}"
            )

        total += product.price * cart_item.quantity

    # Create order
    new_order = Order(
        user_id=user_id,
        total_amount=total,
        status="Placed"
    )

    db.add(new_order)
    db.flush()

    # Create order items and reduce stock
    for cart_item in cart_items:
        product = db.query(Product).filter(
            Product.id == cart_item.product_id
        ).first()

        order_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=cart_item.quantity,
            price=product.price
        )

        db.add(order_item)
        product.stock -= cart_item.quantity

    # Remove ordered items from cart
    for cart_item in cart_items:
        db.delete(cart_item)

    db.commit()
    db.refresh(new_order)

    return new_order
