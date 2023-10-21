import pydantic as pd

from core.enums import OAuthTypesEnum


class SocialAccountCreateSerializer(pd.BaseModel):
    user_uuid: str
    social_name: OAuthTypesEnum
    social_uuid: str
