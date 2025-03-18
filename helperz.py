# region Session
from icecream import ic
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.session_verifier import SessionVerifier
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from uuid import UUID, uuid4
from pydantic import BaseModel
from fastapi import HTTPException
from enum import Enum
from icecream import ic

#endregionfrom fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.session_verifier import SessionVerifier
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from uuid import UUID, uuid4
from pydantic import BaseModel
from fastapi import HTTPException


# region Session

class SessionData(BaseModel):
    usr: str

cookie_params = CookieParameters(
    secure=False,  # Set to True in production with HTTPS
    httponly=True,
    samesite="lax"
)

# Uses UUID
cookie = SessionCookie(
    cookie_name="session_id",
    identifier="general_verifier",
    auto_error=True,
    secret_key="erguierngieorgnioergnoerigneriognerouignerognerig",  # Change this to a strong secret in production
    cookie_params=cookie_params,
)

backend = InMemoryBackend[UUID, SessionData]()

class BasicVerifier(SessionVerifier[UUID, SessionData]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: InMemoryBackend[UUID, SessionData],
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: SessionData) -> bool:
        """If the session exists, it is valid"""
        ic("verify_session")
        ic(model)
        return True

verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=True,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="invalid session - are u sure you are logged in?"),
)


# endregion




class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None