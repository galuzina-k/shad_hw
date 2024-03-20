from pydantic import BaseModel
from .books import ReturnedBook

__all__ = ["IncomingSeller", "ReturnedSeller", "ReturnedAllSellers", "ReturnedSellerWithBooks"]


class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: str



# Класс для валидации входящих данных. Только он содерджит пароль, но не содержит id
class IncomingSeller(BaseSeller):
    password: str

# Класс, валидирующий исходящие данные. Он содержит id, но не содержит пароля.
class ReturnedSeller(BaseSeller):
    id: int
    # books: ReturnedAllBooks
    
class ReturnedSellerWithBooks(BaseSeller):
    id: int
    books: list[ReturnedBook]

class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]
