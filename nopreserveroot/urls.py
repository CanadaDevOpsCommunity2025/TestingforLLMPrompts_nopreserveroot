from rest_framework import routers
from nopreserveroot.views import CategoryViewSet, PromptViewSet

router = routers.SimpleRouter()
router.register("categories", CategoryViewSet)
router.register("prompts", PromptViewSet)
urlpatterns = router.urls
