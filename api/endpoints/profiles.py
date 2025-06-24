from .libs import *
from interface import profiles, validators
from .. import messages as msg


class ProfileAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.user = request.user
        self.profile = profiles.ProfileHandler(self.user)
        self.method_prefix = 'update_'
    
    def get(self, request: Request, method: str) -> Response:
        return Response(
            profiles.ProfileHandler.__dict__[method].fget(
                self.profile), status=status.HTTP_200_OK)
        
    def post(self, request: Request, method: str) -> Response:
        response = getattr(self.profile, self.method_prefix+method)(**request.data)
        if response is not None:
            return Response(response, status=status.HTTP_200_OK)
        return Response(dict(errors=self.profile.errors))


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