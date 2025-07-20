import re
from django.contrib.auth.models import User
from . import constants as const, messages as msg 
from profiles.models import Country, City


class UserValidator:
    
    def __init__(self) -> None:
        self.error_messages = list()
    
    def validate_name(self, name: str) -> bool:
        if not name or not isinstance(name, str):
            self.error_messages.append("Name is required and must be a string")
            return False
        # Allow single or multiple parts, alphabetic characters and spaces only
        if not re.match(r'^[A-Za-z\s]+$', name.strip()):
            self.error_messages.append("Name can only contain alphabetic characters and spaces")
            return False
        return True

    def validate_nickname(self, nickname: str) -> bool:
        if not nickname or not isinstance(nickname, str):
            self.error_messages.append("Nickname is required and must be a string")
            return False
        if len(nickname) > 20:
            self.error_messages.append("Nickname must be 20 characters or less")
            return False
        if not re.match(r'^[A-Za-z0-9_]+$', nickname):
            self.error_messages.append("Nickname can only contain alphanumeric characters and underscores")
            return False
        return True


    def validate_country_and_city(self, country_name: str, city_name: str) -> bool:
        if not country_name or not isinstance(country_name, str):
            self.error_messages.append("Country name is required and must be a string")
            return False
        if not city_name or not isinstance(city_name, str):
            self.error_messages.append("City name is required and must be a string")
            return False
        
        # Create or get Country
        country, created = Country.objects.get_or_create(name=country_name.strip())
        
        # Create or get City
        city, created = City.objects.get_or_create(
            name=city_name.strip(),
            country=country
        )
        
        return True, city  # Return True and the City instance
        
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
    
    
        
    
    
    @property
    def errors(self) -> list:
        return list(set(self.error_messages))
