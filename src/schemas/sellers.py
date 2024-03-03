from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from .books import ReturnedAllBooks

__all__ = ["IncomingSeller", "ReturnedSeller", "ReturnedAllSellers"]


class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: str



# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingSeller(BaseSeller):
    password: str


# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedSeller(BaseSeller):
    id: int

# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedSeller(BaseSeller):
    id: int
    books: ReturnedAllBooks

class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]
