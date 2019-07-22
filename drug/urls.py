from django.urls import path

from .views import (
    DrugSearchView,
    DrugInteractionRankingView,
    DrugInteractionSearchView,
)


app_name = 'drug'
urlpatterns = [
    path('search/', DrugSearchView.as_view(), name='drug-search'),
    path(
        'interactions/',
        DrugInteractionSearchView.as_view(),
        name='interactions',
    ),
    path(
        'ranking/',
        DrugInteractionRankingView.as_view(),
        name='ranking',
    ),
]
