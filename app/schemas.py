from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    user: str = Field(..., min_length=1, max_length=100, examples=["john_doe"])
    message: str = Field(..., min_length=1, max_length=1000, examples=["Where is my order?"])

class ChatResponse(BaseModel):
    answer: str

class ProductOut(BaseModel):
    product_id: int
    name: str
    description: str
    price: float

class OrderOut(BaseModel):
    order_id: int
    user_name: str
    product_name: str
    status: str

class HealthResponse(BaseModel):
    status: str
    database: str
    version: str
