from django.db import models


class Prompt(models.Model):
    name = models.CharField(unique=True, null=False)
    description = models.CharField()
    score = models.IntegerField(default=0, null=False)

    category = models.ForeignKey("Category", on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)


class Category(models.Model):
    name = models.CharField(unique=True, null=False)
    description = models.CharField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)
