from rest_framework_simplejwt.tokens import RefreshToken
from . import lifetime


class TokenHandler:
    
    def __get_token_bearer_by_user(self, user) -> RefreshToken:
        return RefreshToken.for_user(user)
    
    def __get_token_bearer_by_refresh_token(self, refresh_token) -> RefreshToken:
        return RefreshToken(refresh_token)
    
    def __get_token_data(self, bearer: RefreshToken) -> dict:
        access_token = str(bearer.access_token)
        refresh_token = str(bearer)
        return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'access_token_lifetime_remaining': lifetime.get_token_lifetime_remaining(access_token) if access_token else 0,
        'refresh_token_lifetime_remaining': lifetime.get_token_lifetime_remaining(refresh_token) if refresh_token else 0,
    }
    
    def get_token_data_by_user(self, user) -> dict:
        token_bearer = self.__get_token_bearer_by_user(user)
        return self.__get_token_data(token_bearer).copy()
    
    def get_token_data_by_refresh_token(self, refresh_token) -> dict:
        token_bearer = self.__get_token_bearer_by_refresh_token(refresh_token)
        return self.__get_token_data(token_bearer).copy()