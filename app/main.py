from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.cart.router import router as cart_router
from app.products.router import router as product_router

app = FastAPI()
app.include_router(auth_router, prefix="/api/v1")
app.include_router(product_router, prefix="/api/v1")
app.include_router(cart_router, prefix="/api/v1")
