from typing import Protocol
from uuid import UUID

from src.models import UserProfile
from src.schemas.user_profile import UserProfileUpdate


class UserProfileServiceProtocol(Protocol):
    async def update_user_profile(
        self,
        user_id: UUID,
        user_profile_update: UserProfileUpdate,
    ) -> UserProfile: ...

    async def get_user_profile_by_user_id(self, user_id: UUID) -> UserProfile: ...

    
