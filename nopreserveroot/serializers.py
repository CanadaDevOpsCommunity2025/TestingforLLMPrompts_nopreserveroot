from rest_framework.serializers import ModelSerializer

from nopreserveroot.models import Category, Prompt


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        exclude = ["updated_at"]


class PromptSerializer(ModelSerializer):
    class Meta:
        model = Prompt
        exclude = ["updated_at"]
