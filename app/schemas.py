from pydantic import BaseModel, Field
from typing import Optional, List

class ChatRequest(BaseModel):
    user: str = Field(..., examples=["gilang"])
    message: str = Field(..., examples=["Ukuran apa saja untuk Air Max 90?"])

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
