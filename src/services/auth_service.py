from src.core.exceptions import (
    UserWithEmailExistsException,
    UserWithUsernameExistsException,
    UserWithEmailNotFoundException,
    IncorrectEmailOrPasswordException,
    TokenException,
    UserWithIdNotFoundException,
    TokenExpiredException,
)
from src.schemas import AuthResponse, UserResponse
from src.utils import (
    AbstractAsyncRepository,
    AbstractAsyncUOW,
    TokenServiceProtocol,
    UserServiceProtocol,
)
from src.utils.protocols import PasswordHasherProtocol
from src.models import User

# TODO invalidate old refresh-token when you refresh tokens


class AuthService:
    def __init__(
        self,
        uow: AbstractAsyncUOW,
        repo: AbstractAsyncRepository[User],
        user_service: UserServiceProtocol,
        token_service: TokenServiceProtocol,
        password_hasher: PasswordHasherProtocol,
    ) -> None:
        self._uow = uow
        self._repo = repo
        self._user_service = user_service
        self._token_service = token_service
        self._password_hasher = password_hasher

    def _create_refresh_and_access_tokens(self, user) -> dict[str, str]:
        access_token = self._token_service.issue_token(
            user, token_type="access"
        )
        refresh_token = self._token_service.issue_token(
            user, token_type="refresh"
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
        }


    async def register(
        self,
        username: str,
        email: str,
        password: str,
    ) -> dict[str, User | dict[str, str]]:
        """
        1. Uniqueness check
        2. Password hashing
        3. Saving
        """
        hashed_password = self._password_hasher.hash(password)
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
        )

        try:
            new_user = await self._user_service.add_new_user(new_user)
        except UserWithEmailExistsException:
            raise
        except UserWithUsernameExistsException:
            raise

        tokens = self._create_refresh_and_access_tokens(new_user)

        return {
            "user": new_user,
            "tokens": tokens,
        }


    async def login(
        self,
        email: str,
        password: str,
    ) -> dict[str, str]:
        try:
            user = await self._user_service.get_user_by_email(email)
            if not self._password_hasher.verify(
                password, user.hashed_password
            ):
                raise IncorrectEmailOrPasswordException()
            access_token = self._token_service.issue_token(
                user, token_type="access"
            )
            refresh_token = self._token_service.issue_token(
                user, token_type="refresh"
            )
        except UserWithEmailNotFoundException:
            raise IncorrectEmailOrPasswordException()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
        }

    async def refresh(
        self,
        refresh_token: str,
    ) -> dict[str, str]:
        try:
            payload = self._token_service.decode_token(
                refresh_token, token_type="refresh"
            )
            _id = payload.get("sub")
            user = await self._user_service.get_user_by_id(_id)
            access_token = self._token_service.issue_token(
                user, token_type="access"
            )
            new_refresh_token = self._token_service.issue_token(
                user, token_type="refresh"
            )
        except TokenExpiredException:
            raise
        except TokenException:
            raise
        except UserWithIdNotFoundException:
            raise

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "Bearer",
        }

    async def logout(
        self,
        refresh_token: str | None = None,
    ):
        # TODO logout when db for refresh tokens will be implemented
        pass
