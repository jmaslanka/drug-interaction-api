from rest_framework import serializers

from .models import Drug, Interaction


class DrugSearchSerializer(serializers.Serializer):
    name = serializers.CharField()


class DrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drug
        fields = (
            'id',
            'rxcui',
            'name',
            'synonym',
            'language',
            'suppress',
            'umlscui',
        )


class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = (
            'source',
            'severity',
            'description',
        )