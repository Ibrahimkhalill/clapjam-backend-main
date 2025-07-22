from .libs import *
from interface import profiles, validators
from .. import messages as msg
from profiles.models import Nickname, Bio, Pic, BirthDate, Address, Follow
from rest_framework.views import APIView
import logging

logger = logging.getLogger(__name__)

# class ProfileAPI(views.APIView):
#     permission_classes = [permissions.IsAuthenticated]
    
#     def initial(self, request, *args, **kwargs):
#         super().initial(request, *args, **kwargs)
#         self.user = request.user
#         self.profile = profiles.ProfileHandler(self.user)
#         self.method_prefix = 'update_'
    
#     def get(self, request: Request, method: str) -> Response:
#         return Response(
#             profiles.ProfileHandler.__dict__[method].fget(
#                 self.profile), status=status.HTTP_200_OK)
        
#     def post(self, request: Request, method: str) -> Response:
#         response = getattr(self.profile, self.method_prefix+method)(**request.data)
#         if response is not None:
#             return Response(response, status=status.HTTP_200_OK)
#         return Response(dict(errors=self.profile.errors))

class UserProfileAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id) -> Response:
        try:
            user = User.objects.get(id=user_id)
            profile_data = {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.get_full_name() or user.username,
                "nickname": user.nickname.name if hasattr(user, 'nickname') else None,
                "bio": user.bio.content if hasattr(user, 'bio') else None,
                "profile_pic_url": user.pics.profile_pic_url.url if hasattr(user, 'pics') and user.pics.profile_pic_url else None,
                "birth_date": user.birth_date.date_str if hasattr(user, 'birth_date') and user.birth_date.date else None,
                "address": None,
                "is_following": Follow.objects.filter(follower=request.user, followed=user).exists() if user != request.user else False,
                "viewer_is_user": user == request.user
            }
            if hasattr(user, 'address') and user.address:
                profile_data["address"] = {
                    "city": user.address.city.display_name if user.address.city else None,
                    "post_code": user.address.post_code,
                    "country": user.address.city.country.name if user.address.city else None,
                    "details": user.address.details
                }
            return Response(
                profile_data,
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error fetching user profile: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class ProfileAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        try:
            handler = profiles.ProfileHandler(request.user)
            return Response(handler.details, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching profile: {str(e)}")
            return Response(
                {"errors": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request: Request) -> Response:
        try:
            handler = profiles.ProfileHandler(request.user)
            errors = []

            # Update primary info (name, nickname, birthdate)
            name = request.data.get('name')
            nickname = request.data.get('nickname')
            birthdate = request.data.get('birthdate')  # Expect timestamp_ms
            print(f"Received data: name={name}, nickname={nickname}, birthdate={birthdate}")
            if any([name, nickname, birthdate]):
                primary_result = handler.update_primary(name, nickname, birthdate)
                if not primary_result:
                    errors.extend(handler.errors)

            # Update address
            country = request.data.get('country')
            city = request.data.get('city')
            post_code = request.data.get('post_code')
            details = request.data.get('details')
            if any([country, city, post_code, details]):
                is_valid, addr_errors = handler.validate_country_and_city(country, city)
                if is_valid:
                    address_result = handler.update_address(country, city, post_code, details)
                    if not address_result:
                        errors.extend(handler.errors)
                else:
                    errors.extend(addr_errors)

            # Update profile picture
            profile_pic = request.FILES.get('profile_pic')
            if profile_pic:
                request.user.pics.profile_pic_url = profile_pic
                request.user.pics.save()

            if errors:
                return Response(
                    {"error": errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(handler.details, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            return Response(
                {"errors": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PwdChangeAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request: Request) -> Response:
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        handler = validators.UserValidator()
        is_valid = handler.validate_changing_password(password, confirm_password)
        if is_valid:
            request.user.set_password(password)
            request.user.save()
            return Response(dict(message=msg.PWD_CHANGE_SUCCESS), status=status.HTTP_200_OK)
        return Response(dict(errors=handler.errors), status=status.HTTP_400_BAD_REQUEST)
        

class EditBio(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request: Request) -> Response:
        content = request.data.get('text')
        self.user.bio.content = content
        self.user.bio.save()
        return Response(dict())