from django.db import models


class Drug(models.Model):
    rxcui = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=250)
    synonym = models.CharField(max_length=250, blank=True)
    language = models.CharField(max_length=10)
    suppress = models.CharField(max_length=10)
    umlscui = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.rxcui} {self.name}'


class Interaction(models.Model):
    drugs = models.ManyToManyField(Drug, related_name='interactions')
    source = models.CharField(max_length=30)
    severity = models.CharField(max_length=20)
    description = models.CharField(max_length=250)

    def __str__(self):
        return f'{self.source} {self.severity}'
