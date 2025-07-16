import json, datetime
from django.contrib.auth.models import User
from profiles import models
from . import validators, sanitizers


class ProfileHandler:
    
    def __init__(self, user: User) -> None:
        self.user = user
        self.error_messages = list()      
    
    @property
    def primary(self) -> dict:
        return dict(
            id=self.user.id,
            name=self.user.get_full_name(),
            nickname=self.user.nickname.name,
            bio=self.user.bio.content,
            email=self.user.email,
            birthdate=self.user.birth_date.timestamp_ms
        )
    
    @property
    def birthdate(self) -> dict:
        return dict(
            user_id=self.user.id,
            date=self.user.birth_date.timestamp_ms
        )
    
    @property
    def pics(self) -> dict:
        return dict(
            user_id=self.user.id,
            profile_pic_url=self.user.pics.profile_pic_url.url if hasattr(self.user, 'pics') and self.user.pics.profile_pic_url else None
            
        )
    
    @property
    def address(self) -> dict:
        country = city = str()
        if self.user.address.city is not None:
            city = self.user.address.city.name
            country = self.user.address.city.country.name
        return dict(
            user_id=self.user.id,
            country=country,
            city=city,
            post_code=self.user.address.post_code,
            details=self.user.address.details,
        )
    
    @property
    def has_addr_data(self) -> bool:
        addr = self.address
        values = [bool(v) for v in list(addr.values())]
        return sum(values) == values.__len__()
    
    @property
    def details(self) -> dict:
        return dict(
            id=self.user.id,
            has_addr_data=self.has_addr_data,
            primary=self.primary,
            pics=self.pics,
            # birth_date=self.birthdate,
            address=self.address
        )
        
    @property
    def errors(self) -> list:
        return list(set(self.error_messages))
        
    def validate_country_and_city(self, country_name: str, city_name: str) -> bool:
        validator = validators.UserValidator()
        is_valid = validator.validate_country_and_city(country_name, city_name)
        return is_valid, validator.errors
    
    def validate_primary(self, name: str, nickname: str) -> bool:
        validator = validators.UserValidator()
        A, B = validator.validate_name(name), validator.validate_nickname(nickname)
        return A and B, validator.errors
    
    def update_name(self, name: str) -> None:
        self.user.first_name, self.user.last_name = sanitizers.Sanitizer.get_names(name)
        self.user.save()
    
    def update_nickname(self, nickname: str) -> None:
        self.user.nickname.name = nickname
        self.user.nickname.save()
    
        
    def update_birthdate(self, date: str | int) -> dict | None:
        try:
            if isinstance(date, str):
                # Parse YYYY-MM-DD format
                birthdate = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            elif isinstance(date, int):
                # Parse millisecond timestamp
                birthdate = datetime.datetime.fromtimestamp(date / 1000).date()
            else:
                self.error_messages.append("Birthdate must be a timestamp (integer) or YYYY-MM-DD string")
                return None
            self.user.birth_date.date = birthdate
            self.user.birth_date.save()
            return self.birthdate
        except ValueError:
            self.error_messages.append("Invalid birthdate format. Use YYYY-MM-DD or millisecond timestamp")
            return None
    
    def update_primary(self, name: str, nickname: str, birthdate: int) -> dict | None:
        is_valid, errors = self.validate_primary(name, nickname)
        self.error_messages += errors
        if is_valid:
            self.update_name(name)
            self.update_nickname(nickname)
            self.update_birthdate(birthdate)
            return self.primary
    
    def update_address(
        self, country: str, city: str, post_code: str, details: str) -> dict | None:
        if self.validate_country_and_city(country, city):
            city = models.City.objects.get(country__name=country, name=city)
            self.user.address.city = city
            self.user.address.post_code = post_code
            self.user.address.details = details
            self.user.address.save()
            return self.address
    
    def pretty_print(self) -> None:
        print(json.dumps(self.detailed_profile, indent=4))
