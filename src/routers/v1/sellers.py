from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from icecream import ic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.models.sellers import Seller
from src.models.books import Book
from src.schemas import IncomingSeller, ReturnedAllSellers, ReturnedSeller, ReturnedSellerWithBooks

sellers_router = APIRouter(tags=["seller"], prefix="/seller")

# Больше не симулируем хранилище данных. Подключаемся к реальному, через сессию.
DBSession = Annotated[AsyncSession, Depends(get_async_session)]



@sellers_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)  # Прописываем модель ответа
async def create_seller(
    seller: IncomingSeller, session: DBSession
):  # прописываем модель валидирующую входные данные и сессию как зависимость.
    # это - бизнес логика. Обрабатываем данные, сохраняем, преобразуем и т.д.
    new_seller = Seller(
        first_name=seller.first_name
        last_name=seller.last_name
        e_mail=seller.e_mail
        password=seller.password
    )
    session.add(new_seller)
    await session.flush()

    return new_seller



@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    # Хотим видеть формат:
    query = select(Seller)
    res = await session.execute(query)
    sellers = res.scalars().all()
    return {"sellers": sellers}


@sellers_router.get("/{seller_id}", response_model=ReturnedSellerWithBooks)
async def get_seller(seller_id: int, session: DBSession):
    res = await session.get(Seller, seller_id)
    
    # Получаем все книги, принадлежащие продавцу
    query = select(Book).where(Book.seller_id == seller_id)
    books = await session.execute(query)
    seller_books = books.scalars().all()
    return {"seller": res, "books": seller_books}


@sellers_router.delete("/{seller_id}")
async def delete_seller(seller_id: int, session: DBSession):
    deleted_seller = await session.get(Seller, seller_id)
  
    if not deleted_seller:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    query = select(Book).where(Book.seller_id == seller_id)
    books = await session.execute(query)
    books_to_delete = books.scalars().all()

    if books_to_delete:
        await session.delete(books_to_delete)
        await session.flush()

    await session.delete(deleted_seller)
    await session.flush() 

    return Response(status_code=status.HTTP_204_NO_CONTENT)  # Response может вернуть текст и метаданные.



@sellers_router.put("/{seller_id}")
async def update_seller(seller_id: int, new_data: ReturnedSeller, session: DBSession):
    # Оператор "морж", позволяющий одновременно и присвоить значение и проверить его.
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = new_data.first_name
        updated_seller.last_name = new_data.last_name
        updated_seller.email = new_data.e_mail

        await session.flush()

        return updated_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)
