from django.contrib.auth.models import User
from . import validators, messages as msg, constants as const, sanitizers


class AuthHandler:    
    
    def __init__(self) -> None:
        self.error_messages = list()
    
    @property
    def errors(self) -> list:
        return list(set(self.error_messages))
    
    def authenticate_user(self, key: str, value: str, password: str) -> User | None:
        user = User.objects.filter(**{key:value}).first()
        if user is not None:
            if user.check_password(password):
                return user
            self.error_messages.append(msg.WRONG_PWD_MESSAGE)
        else: self.error_messages.append(msg.NO_USER_MESSAGE)
    
    def authenticate_with_email(self, email:str, password: str) -> User | None:
        return self.authenticate_user('email', email, password)
    
    def authenticate_with_username(self, username: str, password: str) -> User | None:
        return self.authenticate_user('username', username, password)
    
    @classmethod
    def create_unique_username(cls, full_name: str, delimiter: str='.') -> str: 
        tail = 0
        merge_username = lambda base_username, tail: f'{base_username}.{tail}'
        base_username = delimiter.join(full_name.split()).lower()[:10]
        username = merge_username(base_username, tail)
        while User.objects.filter(username=username).exists():
            tail += 1; username = merge_username(base_username, tail)
        return username
    
    def validate_reg_data(self, name: str, email: str, password: str) -> bool:
        validator = validators.UserValidator()
        A, B, C = (validator.validate_name(name), 
             validator.validate_email(email), 
             validator.validate_password(password))
        return A and B and C, validator.errors
        
    def prepare_data(self, name: str, email: str, is_superuser: bool=False) -> dict:       
        first_name, last_name = sanitizers.Sanitizer.get_names(name)
        return dict(
            first_name=first_name,
            last_name=last_name,
            username=self.create_unique_username(f'{first_name} {last_name}'),
            email=email,
            is_superuser=is_superuser,
            is_staff=is_superuser
        )
    
    def setup_user(
        self, name: str, email: str, password: str, is_superuser: bool=False) -> User:
        is_validated, errors = self.validate_reg_data(name, email, password)
        self.error_messages += errors
        if is_validated:
            data = self.prepare_data(name, email, is_superuser)
            if not User.objects.filter(**data).exists():
                user = User(**data); user.save()
                user.set_password(password); user.save()
                print('\nCreated user.')
                print('username:', user.username)
                if user.is_superuser:
                    user.codes.verify_email(user.codes.verification_code)
                    print('Email verified.')
                # user.codes.send_verification_code()
                return user
            print('User already exists.')
        else: print('errors:', errors)
    
    
        