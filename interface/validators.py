import re
from django.contrib.auth.models import User
from . import constants as const, messages as msg 
from profiles.models import Country, City


class UserValidator:
    
    def __init__(self) -> None:
        self.error_messages = list()
    
    def validate_name(self, name: str) -> bool: 
        is_valid = re.match(const.NAME_REGEX, name)
        if not is_valid: self.error_messages.append(msg.INVALID_NAME)
        return is_valid
    
    def validate_nickname(self, nickname=str) -> bool: 
        is_valid = re.match(const.NICKNAME_REGEX, nickname)
        if not is_valid: self.error_messages.append(msg.INVALID_NICKNAME)
        return is_valid
        
    def validate_email(self, email: str) -> bool:
        is_unique = not User.objects.filter(email=email).exists()
        is_valid = re.match(const.EMAIL_REGEX, email)
        if not is_unique: self.error_messages.append(msg.DUPLICATE_EMAIL_MESSAGE)
        if not is_valid: self.error_messages.append(msg.INVALID_EMAIL_MESSAGE)
        return is_unique and is_valid
    
    def validate_password(self, password: str) -> bool:
        is_valid = password.__len__() >= 8
        if not is_valid: self.error_messages.append(msg.PASSWORD_MESSAGE)
        return is_valid
    
    def validate_same_password(self, password: str, confirm_password: str) -> str:
        is_valid = password == confirm_password
        if not is_valid: self.error_messages.append(self.PWD_MUST_BE_SAME)
        return is_valid
    
    def validate_password_len(self, password: str) -> bool:
        is_valid = password.__len__() >= 8
        if not is_valid: self.error_messages.append(self.PWD_TOO_SHORT)
        return is_valid
    
    def validate_changing_password(self, password: str, confirm_password: str) -> bool:
        a,b = self.validate_password_len(password), self.validate_same_password(password, confirm_password) 
        return a and b      
    
    def validate_country(self, country_name: str) -> bool:
        is_valid = Country.objects.filter(name=country_name).exists()
        if not is_valid: self.error_messages.append(msg.NO_COUNTRY)
        return is_valid
    
    def validate_city(self, country_name: str, city_name: str) -> bool:
        is_valid = City.objects.filter(country__name=country_name, name=city_name).exists()
        if not is_valid: self.error_messages.append(msg.NO_CITY)
        return is_valid
        
    def validate_country_and_city(self, country_name: str, city_name: str) -> bool:
        a,b = self.validate_country(country_name), self.validate_city(country_name, city_name)
        return a and b 
    
    @property
    def errors(self) -> list:
        return list(set(self.error_messages))
