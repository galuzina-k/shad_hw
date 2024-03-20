import pytest
from fastapi import status
from sqlalchemy import select

from src.models import sellers, books


@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {"first_name": "Evpatiy", "last_name": "Kolovratiy", "e_mail": "biba@edu.boba.ru", "password": "biba_boba_123"}
    response = await async_client.post("/api/v1/sellers/", json=data)
    
    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data == {
    "first_name": "Evpatiy",
    "last_name": "Kolovratiy",
    "e_mail": "biba@edu.boba.ru",
    "id" : 1
    }


@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    data1 = {"first_name": "Evpatiy", "last_name": "Kolovratiy", "e_mail": "biba@edu.boba.ru", "password": "biba_boba_123"}
    data2 = {"first_name": "Bella", "last_name": "Petrovna", "e_mail": "sobachka@sobachka.ru", "password": "sobachka_123"}
    
    seller1 = sellers.Seller(**data1)
    seller2 = sellers.Seller(**data2)

    db_session.add_all([seller1, seller2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["sellers"]) == 2  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "sellers": [
            {"first_name": "Evpatiy", "last_name": "Kolovratiy", "e_mail": "biba@edu.boba.ru", "id": seller1.id},
            {"first_name": "Bella", "last_name": "Petrovna", "e_mail": "sobachka@sobachka.ru", "id": seller2.id}
        ]
    }


@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
    data1 = {"first_name": "Evpatiy", "last_name": "Kolovratiy", "e_mail": "biba@edu.boba.ru", "password": "biba_boba_123"}
    data2 = {"first_name": "Bella", "last_name": "Petrovna", "e_mail": "sobachka@sobachka.ru", "password": "sobachka_123"}
    
    seller1 = sellers.Seller(**data1)
    seller2 = sellers.Seller(**data2)
    
    
    db_session.add_all([seller1, seller2])
    await db_session.flush()
    
    # создаем книги принадлежащие селлеру
    book1 = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller1.id)
    book2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller1.id)


    db_session.add_all([book1, book2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/sellers/{seller1.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {"first_name": "Evpatiy",
                               "last_name": "Kolovratiy",
                               "e_mail": "biba@edu.boba.ru",
                               "id": seller1.id,
                               "books": [
                                   {"title": "Eugeny Onegin", "author": "Pushkin", "year": 2001, "id": book1.id, "count_pages": 104, "seller_id": seller1.id},
                                   {"title": "Mziri", "author": "Lermontov", "year": 1997, "id": book2.id, "count_pages": 104, "seller_id": seller1.id},
                                   ]}


@pytest.mark.asyncio
async def test_delete_selle(db_session, async_client):
    data1 = {"first_name": "Evpatiy", "last_name": "Kolovratiy", "e_mail": "biba@edu.boba.ru", "password": "biba_boba_123"}
    
    seller1 = sellers.Seller(**data1)
    
    
    db_session.add_all([seller1])
    await db_session.flush()
    
    # создаем книги принадлежащие селлеру
    book1 = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller1.id)
    book2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller1.id)


    db_session.add_all([book1, book2])
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{seller1.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()
    
    # удалились книги
    all_sellers = await db_session.execute(select(sellers.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0

    # удалился селлер
    all_books = await db_session.execute(select(books.Book))
    res = all_books.scalars().all()
    assert len(res) == 0


@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    data1 = {"first_name": "Evpatiy", "last_name": "Kolovratiy", "e_mail": "biba@edu.boba.ru", "password": "biba_boba_123"}
    
    seller1 = sellers.Seller(**data1)
    
    
    db_session.add_all([seller1])
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/sellers/{seller1.id}",
        json={ "first_name": "Yaropolk", "last_name": "Yaroslavskiy",
              "e_mail": "biba2@edu.boba.ru",
              "password": "biba_boba_123",
              "id": seller1.id
              }
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(sellers.Seller, seller1.id)
    assert res.first_name == "Yaropolk"
    assert res.last_name == "Yaroslavskiy"
    assert res.e_mail == "biba2@edu.boba.ru"
    assert res.password == "biba_boba_123"
    assert res.id == seller1.id
    
