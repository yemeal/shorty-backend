from uuid import UUID

from src.core.exceptions import (
    UserWithEmailNotFoundException,
    UserWithIdNotFoundException,
    UserWithUsernameNotFoundException,
    UserWithEmailExistsException,
    UserWithUsernameExistsException,
    CreatingException,
)
from src.utils import AbstractAsyncRepository, AbstractAsyncUOW
from src.utils import Specification
from src.models import User


def find_user_by_email(email: str) -> Specification[User]:
    return Specification[User](User.email == email, User.is_active == True)


def find_user_by_username(username: str) -> Specification[User]:
    return Specification[User](
        User.username == username, User.is_active == True
    )


def find_user_by_id(_id: UUID) -> Specification[User]:
    return Specification[User](User.id == _id, User.is_active == True)


class UserService:
    def __init__(
        self,
        uow: AbstractAsyncUOW,
        repo: AbstractAsyncRepository[User],
    ) -> None:
        self._uow = uow
        self._repo = repo

    async def get_user_by_email(self, email: str) -> User:
        async with self._uow:
            user = await self._repo.find_one(find_user_by_email(email))
            if not user:
                raise UserWithEmailNotFoundException()
            return user

    async def get_user_by_id(self, user_id: UUID) -> User:
        async with self._uow:
            user = await self._repo.find_one(find_user_by_id(user_id))
            if not user:
                raise UserWithIdNotFoundException()
            return user

    async def get_user_by_username(self, username: str) -> User:
        async with self._uow:
            user = await self._repo.find_one(
                find_user_by_username(username)
            )
            if not user:
                raise UserWithUsernameNotFoundException()
            return user

    async def get_profile(self, user_id: UUID) -> "UserProfile":
        async with self._uow:
            # TODO Вынести мейби в отдельный сервис
            return {"user_id": user_id, "status": "NotImplemented"}

    async def check_email_exists(self, email: str) -> bool:
        try:
            await self.get_user_by_email(email)
        except UserWithEmailNotFoundException:
            return False
        return True

    async def check_username_exists(self, username: str) -> bool:
        try:
            await self.get_user_by_username(username)
        except UserWithUsernameNotFoundException:
            return False
        return True

    async def add_new_user(self, new_user: User) -> User:
        try:
            async with self._uow:
                user = await self._repo.add(new_user)
        except CreatingException:
            if await self.check_email_exists(new_user.email):
                raise UserWithEmailExistsException(new_user.email)

            if await self.check_username_exists(new_user.username):
                raise UserWithUsernameExistsException(new_user.username)

        return user