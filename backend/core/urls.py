from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet, MapDataView, TagListView, ChatBotView

router = DefaultRouter()
router.register(r'items', ItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('map-data/', MapDataView.as_view(), name='map-data'),
    path('tags/', TagListView.as_view(), name='tag-list'),
    path('chatbot/', ChatBotView.as_view(), name='chatbot'),
]