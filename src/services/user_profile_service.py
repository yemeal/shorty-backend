from uuid import UUID

from src.utils import AbstractAsyncRepository, AbstractAsyncUOW, Specification
from src.core.exceptions import DomainErrors
from src.models import UserProfile
from src.schemas.user_profile import UserProfileUpdate


def find_user_profile_by_user_id(user_id: UUID) -> Specification:
    return Specification(
        UserProfile.user_id == user_id,
    )


class UserProfileService:
    def __init__(
        self,
        uow: AbstractAsyncUOW,
        repo: AbstractAsyncRepository[UserProfile],
    ) -> None:
        self._uow = uow
        self._repo = repo

    async def get_user_profile_by_user_id(self, user_id: UUID) -> UserProfile:
        user_profile = await self._repo.find_one(find_user_profile_by_user_id(user_id))
        if not user_profile:
            raise DomainErrors.UserProfile.NOT_FOUND_BY_USER_ID(user_id=user_id)
        return user_profile

    async def update_user_profile(
        self, 
        user_id: UUID, 
        user_profile_update: UserProfileUpdate
    ) -> UserProfile:
        data = user_profile_update.model_dump(exclude_unset=True)
        async with self._uow:
            profile_to_update = await self.get_user_profile_by_user_id(user_id)
            for field_name, value in data.items():
                setattr(profile_to_update, field_name, value)
            return await self._repo.update(profile_to_update)
