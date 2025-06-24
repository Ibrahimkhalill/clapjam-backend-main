from .libs import *
from interface import auth, profiles
from profiles import models as profile_models
from .. import lifetime, messages as msg, tokens


class RegisterAPI(views.APIView):
    
    def post(self, request: Request) -> Response:
        name = request.data.get('name')
        email = request.data.get('email')
        password = request.data.get('password')
        
        existing_user = User.objects.filter(email=email).first()
        """
        If a user exists with this email, accessed by -> `request.data.get('email')`,
        BUT the existing user email is NOT verified, delete this user,
        and let the user signup again, from scratch.
        """
        if (existing_user is not None) and (not existing_user.codes.is_email_verified):
            # delete unverified existing user
            existing_user.delete()
        
        # initiate signup from scratch
        handler = auth.AuthHandler()
        created_user = handler.setup_user(name, email, password) 
        if created_user is not None:
            profile = profiles.ProfileHandler(created_user)
            return Response(profile.primary, status=status.HTTP_200_OK)
        return Response(dict(errors=handler.errors), status=status.HTTP_400_BAD_REQUEST)


class LoginAPI(views.APIView):
    
    def post(self, request: Request) -> Response:
        existing_user = User.objects.filter(email=request.data.get('email')).first()
        """
        If a user exists with this email, accessed by -> `request.data.get('email')`,
        BUT the existing user email is NOT verified, delete this user,
        and let the user signup again, from scratch.
        """
        if (existing_user is not None) and (not existing_user.codes.is_email_verified):
            # delete unverified existing user
            existing_user.delete()
            # let the frontend dev know
            return Response(dict(errors=[msg.UNVERIFIED_USER]), status=status.HTTP_404_NOT_FOUND)
            
        handler = auth.AuthHandler()
        user = handler.authenticate_with_email(**request.data)
        if user is not None:
            token_handler = tokens.TokenHandler()
            token_data = token_handler.get_token_data_by_user(user)
            token_data['user_id'] = user.id
            profile = profiles.ProfileHandler(user)
            token_data['has_addr_data'] = profile.has_addr_data
            return Response(token_data, status=status.HTTP_200_OK)
        return Response(dict(errors=handler.errors), status=status.HTTP_401_UNAUTHORIZED)
    

class TokenLifetimeAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request: Request) -> Response:
        return Response(
            lifetime.get_token_remaining_days_with_request(request), status=status.HTTP_200_OK)    
            
        
class RefreshTokenAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            return Response(dict(errors=[msg.REFRESH_TOKEN_NOT_PROVIDED]), status=status.HTTP_400_BAD_REQUEST)

        try:
            token_handler = tokens.TokenHandler()
            token_data = token_handler.get_token_data_by_refresh_token(refresh_token)
            token_data['user_id'] = request.user.id
            return Response(token_data, status=status.HTTP_200_OK)
        except TokenError as e:
            return Response(dict(errors=[msg.INVALID_REFRESH_TOKEN]), status=status.HTTP_401_UNAUTHORIZED)
        

class EmailVerificationAPI(views.APIView):
    
    def post(self, request: Request) -> Response:
        if not request.user.is_authenticated: 
            if profile_models.AuthCode.verify_email_before_login(**request.data):
               return Response(dict(message=msg.EMAIL_VERIFIED), status=status.HTTP_200_OK)
            return Response(dict(errors=[msg.INVALID_CODE]), status=status.HTTP_401_UNAUTHORIZED) 
        return Response(dict(errors=[msg.ALREADY_LOGGED_IN]), status=status.HTTP_400_BAD_REQUEST)


class OTPRequestAPI(views.APIView):
    
    def post(self, request: Request) -> Response:
        if not request.user.is_authenticated:
            email = request.data.get('email')
            user = User.objects.filter(email=email).first()
            if user is not None:
                if user.codes.send_otp():
                    return Response(dict(email=email, message=msg.OTP_SENT), status=status.HTTP_200_OK)
                return Response(dict(errors=[msg.OTP_SENDING_FAILED]), status=status.HTTP_400_BAD_REQUEST)
            return Response(dict(errors=[msg.NO_EMAIL_USER]), status=status.HTTP_404_NOT_FOUND)
        return Response(dict(errors=[msg.ALREADY_LOGGED_IN]), status=status.HTTP_400_BAD_REQUEST)
        

class OTPVerificationAPI(views.APIView):
    
    def post(self, request: Request) -> Response:
        if not request.user.is_authenticated: 
            if profile_models.AuthCode.verify_otp_before_login(**request.data):
                user = User.objects.get(email=request.data.get('email'))
                profile = profiles.ProfileHandler(user)
                response = dict(user_id=user.id, message=msg.OTP_VERIFIED, has_addr_data=profile.has_addr_data)
                tokens_handler = tokens.TokenHandler()
                token_data = tokens_handler.get_token_data_by_user(user)
                response.update(token_data)
                return Response(response, status=status.HTTP_200_OK)
            return Response(dict(errors=[msg.INVALID_CODE]), status=status.HTTP_401_UNAUTHORIZED) 
        return Response(dict(errors=[msg.ALREADY_LOGGED_IN]), status=status.HTTP_400_BAD_REQUEST)
     