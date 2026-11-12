from fastapi import FastAPI

from app.routers import products, users

tags_metadata = [
    {"name": "Товары", "description": "Каталог: просмотр с фильтрами, создание, изменение и удаление товаров."},
    {"name": "Пользователи", "description": "Регистрация и управление пользователями магазина."},
]

app = FastAPI(
    title="Каталог магазина API",
    description=(
        "REST API интернет-магазина: каталог товаров с фильтрацией и пагинацией и управление пользователями. "
        "Все ответы и ошибки — в формате JSON; при ошибке возвращается поле `detail` с описанием."
    ),
    version="1.0.0",
    openapi_tags=tags_metadata,
)

app.include_router(products.router)
app.include_router(users.router)
