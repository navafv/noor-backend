from rest_framework.routers import DefaultRouter
from .views import RoleViewSet, UserViewSet, HistoricalUserViewSet

router = DefaultRouter()
router.register("roles", RoleViewSet, basename="role")
router.register("users", UserViewSet, basename="user")
router.register("history/users", HistoricalUserViewSet, basename="user-history")

urlpatterns = router.urls
