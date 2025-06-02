from rest_framework.viewsets import ModelViewSet

from nopreserveroot.models import Category, Prompt
from nopreserveroot.serializers import CategorySerializer, PromptSerializer


class PromptViewSet(ModelViewSet):
    queryset = Prompt.objects.all()
    serializer_class = PromptSerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
