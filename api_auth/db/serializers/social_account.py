import pydantic as pd

from core.enums import OAuthTypesEnum


class SocialAccountCreateSerializer(pd.BaseModel):
    user_id: str
    social_name: OAuthTypesEnum
    social_id: str
