from datetime import date, datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone as tz
from utils import constants as const, keygen


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        verbose_name_plural = 'Countries'
    
    def __str__(self) -> str:
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities')
    
    class Meta:
        verbose_name_plural = 'Cities'
    
    
    def __str__(self) -> str:
        return f'{self.name}, {self.country.name}'

    @property
    def display_name(self) -> str:
        return self.__str__() 


class Nickname(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, default='')


class Bio(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='bio')    
    content = models.TextField(default='')
    

class Pic(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pics')
    profile_pic_url = models.TextField(default='')
    cover_pic_url = models.TextField(default='')
    
    def __str__(self) -> str:
        return self.user.email 


class BirthDate(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='birth_date')
    date = models.DateField(null=True, blank=True, default=None)
    
    @property
    def date_str(self) -> str | None:
        if self.date is not None:
            return self.date.strftime(const.DATE_STR_FORMAT_1)
    
    @property
    def timestamp_ms(self) -> int | None:
        if self.date is not None:
            return int(datetime.combine(self.date, datetime.min.time()).timestamp() * 1000)
        
    def __str__(self) -> str:
        return f'{self.user.email} | {self.user.username} | {self.date_str}'


class Address(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='address', null=True, blank=True, default=None)
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, null=True, blank=True, default=None)
    post_code = models.CharField(max_length=15, null=True, blank=True, default='')
    details = models.TextField(null=True, blank=True, default='')
    
    class Meta:
        verbose_name_plural = 'User Address'
    
    def __str__(self) -> str:
        return self.user.email + ' | ' + self.user.username
    

class AuthCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='codes')
    otp = models.CharField(max_length=4, default='') 
    verification_code = models.CharField(max_length=4, default='')
    is_email_verified = models.BooleanField(default=False)
    
    def __generate_code(self):
        kg = keygen.KeyGen()
        return kg.num_key(key_len=4)
    
    def change_otp(self):
        self.otp = self.__generate_code()
        self.save()
    
    def change_verification_code(self):
        self.verification_code = self.__generate_code()
        self.save()
    
    def send_otp(self):
        try:
            self.change_otp()
            # self.send_code('OTP')
            return True
        except: return False
    
    def send_verification_code(self):
        try:
            self.change_verification_code()
            # self.send_code('verification code')
            return True
        except: return False
    
    def verify_auth_code(self, code_type: str, code: str) -> bool:
        print(f'verifying: {self.__dict__[code_type]} == {code}')
        return self.__dict__[code_type] == code
        
    def verify_email(self, code: str) -> bool:
        if self.verify_auth_code('verification_code', code):
            self.is_email_verified = True; self.save()
            return True
        return False
    
    def verify_otp(self, code: str) -> bool:
        return self.verify_auth_code('otp', code)
    
    @classmethod
    def verify_email_before_login(cls, email: str, code: str) -> bool:
        user = User.objects.filter(email=email).first()
        if user is not None:
            return user.codes.verify_email(code)
        return False
    
    @classmethod
    def verify_otp_before_login(cls, email: str, code: str) -> bool:
        user = User.objects.filter(email=email).first()
        if user is not None:
            return user.codes.verify_otp(code)
        return False

    def save(self, *args, **kwargs):
        if not self.otp:
            self.otp = self.__generate_code()
        if not self.verification_code:
            self.verification_code = self.__generate_code()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.user.email


class Follow(models.Model):
    followed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers')
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following')
    
    @classmethod
    def get_followers(cls, user: User) -> models.QuerySet:
        follower_ids = [follow.follower.id for follow in cls.objects.filter(followed=user)]
        return User.objects.filter(id__in=follower_ids)
    
    def save(self, *args, **kwargs) -> None:
        # A user can't follow itself
        if self.followed == self.follower:
            raise ValueError('A user cannot follow itself')
        
        # Avoid follow pair duplication
        if self.__class__.objects.filter(
            follower=self.follower, followed=self.followed).exists():
            raise ValueError('Follow duplication')
        
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f'{self.followed.username} followed by {self.follower.username}'
    