from fastapi import FastAPI , HTTPException ,status ,Request
from pydantic import BaseModel
from typing import Optional,Any
from datetime import datetime

app = FastAPI()


class APIResponse(BaseModel):
    statusCode: int
    message: str
    data: Optional[Any] = None
    error: Optional[Any] = None
    timestamp: str
    path: str

def create_response(status_code: int, message: str, data: Any = None, error: Any = None, path: str = ""):
    return APIResponse(
        statusCode=status_code,
        message=message,
        data=data,
        error=error,
        timestamp=datetime.now().isoformat(),
        path=path
    ).model_dump()


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return create_response(
        status_code=exc.status_code,
        message=exc.detail,
        error=status.phrase(exc.status_code),
        path=request.url.path,
    )



orders_db = [
    {"id": 1, "code": "SP001", "status": "PENDING"},
    {"id": 2, "code": "SP002", "status": "DELIVERED"}
]


@app.get("/orders")
def display_orders():
    return orders_db

@app.delete("/orders/{order_id}")
async def cancel_order(order_id: int, request: Request):
    # Bước 1: Tìm kiếm đơn hàng trong DB
    target_order = None
    for order in orders_db:
        if order["id"] == order_id:
            target_order = order
            break

    if not target_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy đơn hàng với mã ID: {order_id}",
        )

    if target_order["status"] == "DELIVERED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể hủy đơn hàng do sản phẩm đã được giao thành công.",
        )

    target_order["status"] = "CANCELLED"

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Hủy đơn hàng thành công.",
        data=target_order,
        error=None,
        path=request.url.path,
    )


