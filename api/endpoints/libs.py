from django.contrib.auth.models import User
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import views, status, permissions
from rest_framework_simplejwt.tokens import TokenError