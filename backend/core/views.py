from rest_framework import viewsets, permissions, filters, generics
from django_filters.rest_framework import DjangoFilterBackend
from .models import Item, Tag
from .serializers import ItemSerializer, MapItemSerializer, TagSerializer
from .permissions import IsOwnerOrReadOnly

class TagListView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.filter(status='ACTIVE')
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {'tags': ['exact'], 'type': ['exact']}
    search_fields = ['title', 'description']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Geo-filtering logic (simple box approximation)
        min_lat = self.request.query_params.get('min_lat')
        max_lat = self.request.query_params.get('max_lat')
        min_lon = self.request.query_params.get('min_lon')
        max_lon = self.request.query_params.get('max_lon')

        if min_lat and max_lat and min_lon and max_lon:
            queryset = queryset.filter(
                latitude__gte=min_lat, latitude__lte=max_lat,
                longitude__gte=min_lon, longitude__lte=max_lon
            )
        
        return queryset.order_by('-created_at')

class MapDataView(generics.ListAPIView):
    queryset = Item.objects.filter(status='ACTIVE')
    serializer_class = MapItemSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None