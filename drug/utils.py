from json.decoder import JSONDecodeError
import requests
from typing import Union

from .models import Drug
from .serializers import DrugSerializer, InteractionSerializer


def api_get_request(url: str) -> Union[None, dict]:
    try:
        response = requests.get(url, timeout=1.5)
        if not response.ok:
            return None

        return response.json()
    except (requests.RequestException, JSONDecodeError):
        return None


def fetch_drugs(name: str) -> list:
    BASE_URL = 'https://rxnav.nlm.nih.gov/REST/drugs.json'
    url = f'{BASE_URL}?name={name}'
    raw_data = api_get_request(url)
    data = []

    if not (
        raw_data and
        raw_data.get('drugGroup') and
        raw_data['drugGroup'].get('conceptGroup')
    ):
        return []

    for group in raw_data['drugGroup']['conceptGroup']:
        if group.get('tty') in ['SCD', 'SDB'] and \
                group.get('conceptProperties'):
            data.extend(group['conceptProperties'])

    data = [
        {
            'rxcui': drug.get('rxcui'),
            'name': drug.get('name'),
            'synonym': drug.get('synonym'),
            'language': drug.get('language'),
            'suppress': drug.get('suppress'),
            'umlscui': drug.get('umlscui'),
        } for drug in data
    ]

    # exclude the ones we already have
    ids = Drug.objects.filter(
        rxcui__in=[i.get('rxcui') for i in data]
    ).values_list('rxcui', flat=True)

    data = [drug for drug in data if drug['rxcui'] not in ids]

    serializer = DrugSerializer(data=data, many=True)
    if serializer.is_valid():
        serializer.save()
        return serializer.data

    return []


def fetch_interactions(first, second):
    BASE_URL = 'https://rxnav.nlm.nih.gov/REST/interaction/list.json'
    url = f'{BASE_URL}?rxcuis={first.rxcui}+{second.rxcui}'
    raw_data = api_get_request(url)
    data = []

    if not (raw_data and raw_data.get('fullInteractionTypeGroup')):
        return []

    group = 'fullInteractionTypeGroup'

    for drug_data in raw_data[group][0]['fullInteractionType']:
        for interaction in drug_data['interactionPair']:
            data.append({
                'source': raw_data[group][0]['sourceName'],
                'description': interaction['description'],
                'severity': interaction['severity'],
            })

    # remove duplicates by converting dict to set
    data = [dict(t) for t in {tuple(i.items()) for i in data}]

    serializer = InteractionSerializer(data=data, many=True)
    if serializer.is_valid():
        interactions = serializer.save()
        [i.drugs.set([first, second]) for i in interactions]
        return serializer.data

    return []
