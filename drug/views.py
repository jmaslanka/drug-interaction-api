from django.db.models import Count, Window, F
from django.db.models.functions import DenseRank
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Drug, Interaction
from .serializers import (
    DrugSearchSerializer,
    DrugSerializer,
    InteractionSerializer,
)
from .utils import fetch_drugs, fetch_interactions


class DrugSearchView(ListCreateAPIView):
    queryset = Drug.objects.all()
    permission_classes = (AllowAny,)
    authentication_classes = []
    paginator = None

    def get_serializer_class(self):
        if self.request.method.lower() == 'post':
            return DrugSearchSerializer
        return DrugSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        drugs_data = fetch_drugs(serializer.data.get('name'))

        if not drugs_data:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(
            drugs_data,
            status=status.HTTP_201_CREATED,
        )


class DrugInteractionSearchView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        first = self.request.query_params.get('first')
        second = self.request.query_params.get('second')

        if not (first and second):
            return Response(
                {'message': '`first` and `second` id missing.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        drugs = list(Drug.objects.filter(id__in=[first, second]))

        if len(drugs) != 2:
            return Response(
                {'message': 'Invalid drug identifiers.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        interactions = Interaction.objects \
            .filter(drugs=drugs[0]).filter(drugs=drugs[1])

        if interactions:
            return Response(
                InteractionSerializer(interactions, many=True).data,
                status=status.HTTP_200_OK,
            )

        interactions_data = fetch_interactions(drugs[0], drugs[1])

        return Response(
            interactions_data,
            status=status.HTTP_201_CREATED,
        )


class DrugInteractionRankingView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        qs = Drug.objects.prefetch_related('interactions').annotate(
            interactions_count=Count('interactions'),
            rank=Window(
                expression=DenseRank(),
                order_by=F('interactions_count').desc(),
            ),
        ).order_by('rank')[:10]

        return Response(
            [
                {
                    'name': drug.name,
                    'rxcui': drug.rxcui,
                    'interactions_count': drug.interactions_count,
                    'rank': drug.rank,
                } for drug in qs
            ],
            status=status.HTTP_200_OK,
        )
