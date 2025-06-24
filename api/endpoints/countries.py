from .libs import *
from profiles import models


class CountriesAPI(views.APIView):
    
    def get(self, request: Request) -> Response:
        return Response(dict(
            countries=[c.name for c in models.Country.objects.all()]
        ), status=status.HTTP_200_OK)


class citiesAPI(views.APIView):
    
    def post(self, request: Request) -> Response:
        country_name = request.data.get('country_name')
        return Response(
            dict(
                country_name=country_name, cities=[c.name for c in models.City.objects.filter(
                    country__name=country_name).all()]),
        status=status.HTTP_200_OK
    )