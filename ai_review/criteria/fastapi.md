# FastAPI

Актуально для проектов с реализацией API-сервиса на FastAPI

## Критерии

### Для Production доступ к документации API-ограничен

Либо через явное указание None при инициализации приложения
```python
app = FastAPI(
    docs_url=None, 
    redoc_url=None, 
    openapi_url=None,
)
```

Либо с требованием аутентификации для /docs, /redoc, /openapi.json
```python
docs_router = APIRouter(dependencies=[Depends(get_current_superuser)])

@docs_router.get("/docs", include_in_schema=False)
async def get_swagger_documentation() -> fastapi.responses.HTMLResponse:
    """Protected Swagger UI endpoint"""
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")
```

Это помогает защитить конфиденциальные сведения об API от посторонних лиц.


### Используются uvloop и httptools

После установки этих зависимостей uvicorn автоматически начнет их использовать:
- uvloop для замены стандартного asyncio event loop
- httptools для замены HTTP-парсера


### Для получение данных из Websocket рекомендуется использовать `async for`

Это более короткий и современный синтаксис

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    async for data in websocket.iter_text():
        ...
```


### Для тестирования рекомендуется использовать AsyncClient из httpx

Для работы lifespan-событий следует применять библиотеку asgi-lifespan
```python
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport

@pytest.fixture(scope="session")
async def client():
    async with LifespanManager(app) as manager:
        async with AsyncClient(transport=ASGITransport(app=manager.app)) as client:
            yield client
```


### Для хранения объектов, создаваемых при старте приложения, рекомендуется использовать Lifespan State

Например, инициализируемым при старте приложения объектом может быть модель машинного обучения

Доступен такой объект будет из request.state

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, TypedDict, cast

from fastapi import FastAPI, Request


class State(TypedDict):
    model: LinearRegression

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[State]:
    model = load_model()
    yield {"model": model}

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root(request: Request) -> dict[str, Any]:
    model = cast(LinearRegression, request.state.model)
    prediction = model.predict()
    ...
```


### Длительные синхронные операции не должны выполняться в асинхронных хэндлерах эндпоинтов

FastAPI может обрабатывать синхронные хэндлеры в отдельном пуле потоков

Если хэндлер обозначен как async и содержит длительную синхронную операцию, то она заблокирует весь цикл обработки событий


### CPU-требовательные задачи следует выполнять за пределами приложения FastAPI

Генерация предсказания большой модели следует выполнять через отложенные задачи.
Это возможно реализовать через библиотеки arq, Celery и подобные


### Синхронные задачи обрабатываются в асинхронном эндпоинте в отдельном потоке

Критично для старых синхронных SDK
```python
from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool

app = FastAPI()


@app.get("/")
async def call_my_sync_library():
    client = SyncAPIClient()
    await run_in_threadpool(client.make_request, data=1)
```


### Для валидации схем запросов и ответов используются все доступные возможности Pydantic

Pydantic позволяет использовать для валидации regex, enum, email validation

```python
from enum import StrEnum
from pydantic import AnyUrl, BaseModel, EmailStr, Field


class MusicBand(StrEnum):
   AEROSMITH = "AEROSMITH"
   QUEEN = "QUEEN"
   ACDC = "AC/DC"


class UserBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=128)
    username: str = Field(min_length=1, max_length=128, pattern="^[A-Za-z0-9-_]+$")
    email: EmailStr
    age: int = Field(ge=18, default=None) 
    favorite_band: MusicBand | None = None
    website: AnyUrl | None = None
```


### Для полей схем запросов и ответов указаны описания

Pydantic позволяет использовать для валидации regex, enum, email validation

```python
from pydantic import BaseModel, Field, EmailStr

class UserResponse(BaseModel):
    first_name: str = Field(min_length=1, max_length=128, description="Имя пользователя")
    email: EmailStr = Field(description="Электронная почта пользователя")
    age: int = Field(ge=18, description="Возраст пользователя")
```


### Для всех эндпоинтов используется декларативная валидация через Pydantic, включая query-параметры, path-параметры и тело запроса

FastAPI автоматически валидирует данные на основе аннотаций типов. Это исключает ручную проверку и гарантирует, что в эндпоинт попадают только корректные данные.

```python
from fastapi import FastAPI, Query, Path
from pydantic import BaseModel, Field

app = FastAPI()

class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)

@app.post("/items/{item_id}")
async def create_item(
    item_id: int = Path(..., ge=1, description="ID товара"),
    q: str | None = Query(None, max_length=50, description="Поисковый запрос"),
    item: ItemCreate = ...
): ...
```


### Для управления зависимостями (БД, текущий пользователь, клиенты API) используется система Depends

Это позволяет избежать дублирования кода, упрощает тестирование и делает код более модульным и читаемым.

```python
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db
from .auth import get_current_user

app = FastAPI()

@app.get("/users/me")
async def read_users_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    ...
```


### Обработка ошибок централизована через кастомные исключения и обработчики исключений

Для единообразного формата ответов об ошибках рекомендуется определить собственные исключения и добавить обработчики с помощью @app.exception_handler.

```python
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse

class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )
```


### Все маршруты сгруппированы в APIRouter по функциональному признаку

Это улучшает читаемость и поддерживаемость кода. В основном файле приложения только подключаются роутеры.

```python
# routers/users.py
from fastapi import APIRouter
router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
async def get_users(): ...

# main.py
from routers import users
app.include_router(users.router)
```


### Используется HTTPException с понятным сообщением для клиентских ошибок

Не использовать просто raise Exception, а выбрасывать HTTPException с соответствующим кодом и деталями.

```python
from fastapi import HTTPException

if not user:
    raise HTTPException(status_code=404, detail="User not found")
```
