from django.urls import path

from .views import DrugSearchView, DrugInteractionSearch


app_name = 'drug'
urlpatterns = [
    path('search/', DrugSearchView.as_view(), name='drug-search'),
    path(
        'interactions/',
        DrugInteractionSearch.as_view(),
        name='interactions',
    ),
]
