import requests
from django_setup import *
from profiles import models
from tqdm import tqdm


def main(): 
    url = 'http://192.168.10.33:7979/countries.json'
    countries = requests.get(url).json()

    if input('Clear Country and City Tables? (yes/no): ').lower() == 'yes':
        print('Clearing Country and City Tables...')
        models.Country.objects.all().delete()
        print('Cleared.')

    print('\nPreparing new countries and cities...')
    for data in countries:
        print('Adding country:', data['name'])
        country = models.Country.objects.create(name=data['name'])
        for city in tqdm(
            data['cities'], desc=f'Adding cities to {data["name"]}', unit=' city', leave=True):
            city = models.City(country=country, name=city['name'])
            city.save()

    print('\nTotal countries:', models.Country.objects.count())
    print('Total cities:', models.City.objects.count())


if __name__ == '__main__':
    main()