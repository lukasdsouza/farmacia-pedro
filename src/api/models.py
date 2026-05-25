from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    nome_completo: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    nome_completo: str
    created_at: str


class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    email: str = Field(..., min_length=5, max_length=128)
    password: str = Field(..., min_length=6, max_length=128)
    role: str = Field("funcionario")
    nome_completo: str = Field("", max_length=128)

    @field_validator("role")
    @classmethod
    def role_valid(cls, v):
        if v not in ("gestor", "funcionario"):
            raise ValueError("role deve ser 'gestor' ou 'funcionario'")
        return v


class UpdateUserRequest(BaseModel):
    email: Optional[str] = Field(None, max_length=128)
    role: Optional[str] = None
    is_active: Optional[bool] = None
    nome_completo: Optional[str] = Field(None, max_length=128)
    password: Optional[str] = Field(None, min_length=6, max_length=128)

    @field_validator("role")
    @classmethod
    def role_valid(cls, v):
        if v is not None and v not in ("gestor", "funcionario"):
            raise ValueError("role deve ser 'gestor' ou 'funcionario'")
        return v


class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    category: str
    price: float
    avg_cost: float
    stock: int


class OrderItemResponse(BaseModel):
    product_id: int
    sku: str
    name: str
    qty: int
    price: float


class OrderResponse(BaseModel):
    id: int
    status: str
    created_at: str
    customer: str
    total: float
    items: List[OrderItemResponse] = []


class UpdateOrderStatusRequest(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def status_valid(cls, v):
        valid = {"pendente", "processando", "enviado", "entregue", "cancelado"}
        if v not in valid:
            raise ValueError(f"status deve ser um de: {', '.join(valid)}")
        return v


class CustomerOrderResponse(BaseModel):
    id: int
    session_id: str
    customer_name: str
    customer_phone: str
    items_json: str
    delivery_type: str
    delivery_address: str
    taxa_entrega: float
    status: str
    total: float
    notes: str
    created_at: str
    updated_at: str


class UpdateCustomerOrderRequest(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def status_valid(cls, v):
        valid = {"pendente", "confirmado", "em_preparo", "pronto", "entregue", "cancelado"}
        if v not in valid:
            raise ValueError(f"status deve ser um de: {', '.join(valid)}")
        return v


class CustomerRegisterRequest(BaseModel):
    nome: str = Field(..., min_length=2, max_length=128)
    email: str = Field(..., min_length=5, max_length=128)
    telefone: str = Field("", max_length=20)
    senha: str = Field(..., min_length=6, max_length=128)
    endereco_rua: str = Field("", max_length=200)
    endereco_numero: str = Field("", max_length=20)
    endereco_complemento: str = Field("", max_length=100)
    endereco_bairro: str = Field("", max_length=100)
    endereco_cidade: str = Field("Rio de Janeiro", max_length=100)


class CustomerLoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=128)
    senha: str = Field(..., min_length=1, max_length=128)


class CustomerTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    customer: "CustomerResponse"


class CustomerResponse(BaseModel):
    id: int
    nome: str
    email: str
    telefone: str
    endereco_rua: str
    endereco_numero: str
    endereco_complemento: str
    endereco_bairro: str
    endereco_cidade: str
    created_at: str


class CustomerUpdateRequest(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=128)
    telefone: Optional[str] = Field(None, max_length=20)
    senha: Optional[str] = Field(None, min_length=6, max_length=128)
    endereco_rua: Optional[str] = Field(None, max_length=200)
    endereco_numero: Optional[str] = Field(None, max_length=20)
    endereco_complemento: Optional[str] = Field(None, max_length=100)
    endereco_bairro: Optional[str] = Field(None, max_length=100)
    endereco_cidade: Optional[str] = Field(None, max_length=100)


class ChatMessageRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=128)
    text: str = Field(..., min_length=1, max_length=2048)
    customer_id: Optional[int] = None


class ChatMessageResponse(BaseModel):
    ok: bool
    reply: str
    session_id: str


class DashboardStats(BaseModel):
    total_products: int
    low_stock_count: int
    pending_orders: int
    todays_orders: int
    total_customer_orders: int
    pending_customer_orders: int
    revenue_today: float
    top_products: List[Dict[str, Any]] = []
