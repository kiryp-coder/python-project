import strawberry
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from strawberry.fastapi import GraphQLRouter

from app.database import get_session
from app.models import Product


@strawberry.type(description="Покупатель (без почты — только публичные данные)")
class BuyerType:
    id: int
    name: str


@strawberry.type(description="Заказ, в который входит товар")
class OrderType:
    id: int
    total_price: float
    buyer: BuyerType


@strawberry.type(description="Товар каталога")
class ProductType:
    id: int
    name: str
    price: float
    category: str
    stock: int
    model: strawberry.Private[Product]

    @strawberry.field(description="Заказы с этим товаром. Загружаются из базы, только если поле запрошено.")
    def orders(self) -> list[OrderType]:
        return [
            OrderType(id=order.id, total_price=order.total_price, buyer=BuyerType(id=order.user.id, name=order.user.name))
            for order in self.model.orders
        ]


def to_product_type(product):
    return ProductType(
        id=product.id,
        name=product.name,
        price=product.price,
        category=product.category,
        stock=product.stock,
        model=product,
    )


@strawberry.type
class Query:
    @strawberry.field(description="Список товаров. Фильтры необязательные: категория и максимальная цена.")
    def products(
        self, info: strawberry.Info, category: str | None = None, max_price: float | None = None
    ) -> list[ProductType]:
        query = select(Product).order_by(Product.id)
        if category is not None:
            query = query.where(Product.category == category)
        if max_price is not None:
            query = query.where(Product.price <= max_price)

        session = info.context["session"]
        return [to_product_type(product) for product in session.scalars(query)]

    @strawberry.field(description="Один товар по id или null, если его нет.")
    def product(self, info: strawberry.Info, id: int) -> ProductType | None:
        product = info.context["session"].get(Product, id)
        return to_product_type(product) if product else None


schema = strawberry.Schema(query=Query)


def get_context(session: Session = Depends(get_session)):
    return {"session": session}


graphql_router = GraphQLRouter(schema, context_getter=get_context)
