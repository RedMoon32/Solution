from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=100, null=True)
    directors = models.ManyToManyField("Director", related_name="directors")
    siren = models.IntegerField()

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()


class Director(models.Model):
    name = models.CharField(max_length=100, null=True)
    date_of_birth = models.CharField(max_length=100, null=True)
    companies = models.ManyToManyField("Company", related_name="companies")

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()
