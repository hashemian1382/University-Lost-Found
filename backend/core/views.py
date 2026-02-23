# backend/core/views.py
import traceback
from rest_framework import viewsets, permissions, filters, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status
from django_filters.rest_framework import DjangoFilterBackend
from .models import Item, Tag
from .serializers import (
    ItemSerializer, MapItemSerializer, TagSerializer,
    ChatBotRequestSerializer, ChatBotResponseSerializer,
    ChatBotSearchResponseSerializer, SimilarItemSerializer
)
from .permissions import IsOwnerOrReadOnly
from .ai_service import ChatBotService
from .search_service import ItemSearchService

class TagListView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.filter(status='ACTIVE')
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        'tags': ['exact', 'in'],
        'type': ['exact']
    }
    search_fields = ['title', 'description']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        
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


class ChatBotView(APIView):
    """
    API endpoint for chatbot service that finds related items
    by sending all items and user description to AI
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Process user's natural language description and find related items using AI
        
        Request body:
        {
            "description": "User's description of lost or found item"
        }
        
        Response:
        {
            "related_items": [...],     // Array of related items found
            "total_matches": 5,          // Number of matches found
            "explanation": "Brief explanation of why these items were selected"
        }
        """
        # Validate request
        request_serializer = ChatBotRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            return Response(
                request_serializer.errors,
                status=http_status.HTTP_400_BAD_REQUEST
            )
        
        user_description = request_serializer.validated_data['description']
        
        print(f"\n=== CHATBOT REQUEST (NEW APPROACH) ===")
        print(f"User: {request.user}")
        print(f"Description: {user_description[:100]}...")
        
        try:
            # Step 1: Fetch all active items from database
            print("Step 1: Fetching all active items from database...")
            all_items = Item.objects.filter(status='ACTIVE').select_related('author').prefetch_related('tags')
            print(f"Step 2: Found {all_items.count()} active items")
            
            # Step 2: Prepare items data for AI
            print("Step 3: Preparing items data for AI...")
            items_data = []
            for item in all_items:
                items_data.append({
                    'id': item.id,
                    'title': item.title,
                    'description': item.description,
                    'type': item.type,
                    'tags': [tag.name for tag in item.tags.all()],
                    'location_description': f"Lat: {item.latitude}, Lon: {item.longitude}"
                })
            print(f"Step 4: Prepared {len(items_data)} items for AI")
            
            # Step 3: Initialize AI service and find related items
            print("Step 5: Initializing ChatBotService...")
            chatbot_service = ChatBotService()
            print("Step 6: Calling find_related_items...")
            result = chatbot_service.find_related_items(user_description, items_data)
            print(f"Step 7: Got result - success: {result.get('success')}")
            
            if not result['success']:
                print(f"ERROR: AI matching failed - {result.get('error')}")
                return Response(
                    {
                        'error': 'Failed to find related items',
                        'details': result.get('error', 'Unknown error')
                    },
                    status=http_status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Step 4: Get the related item IDs from AI response
            print("Step 8: Extracting related item IDs from result...")
            related_item_ids = result['data']['related_item_ids']
            explanation = result['data'].get('explanation', 'AI matched these items based on similarity.')
            print(f"Step 9: AI found {len(related_item_ids)} related items")
            
            # Step 5: Fetch the actual items from database
            print("Step 10: Fetching related items from database...")
            related_items = Item.objects.filter(
                id__in=related_item_ids,
                status='ACTIVE'
            ).select_related('author').prefetch_related('tags')
            
            # Preserve the order from AI (by match relevance)
            print("Step 11: Ordering items by AI relevance...")
            items_dict = {item.id: item for item in related_items}
            ordered_items = [items_dict[item_id] for item_id in related_item_ids if item_id in items_dict]
            print(f"Step 12: Ordered {len(ordered_items)} items")
            
            # Step 6: Serialize the related items
            print("Step 13: Serializing related items...")
            related_items_serializer = SimilarItemSerializer(ordered_items, many=True)
            
            # Step 7: Prepare response
            print("Step 14: Preparing response...")
            response_data = {
                'related_items': related_items_serializer.data,
                'total_matches': len(ordered_items),
                'explanation': explanation
            }
            
            print("Step 15: SUCCESS! Returning response.")
            return Response(
                response_data,
                status=http_status.HTTP_200_OK
            )
            
        except ValueError as e:
            # Handles missing API key error
            print(f"ERROR: ValueError - {e}")
            traceback.print_exc()
            return Response(
                {'error': str(e)},
                status=http_status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            # Catch any unexpected errors
            print(f"ERROR: Exception - {e}")
            print(f"Exception type: {type(e).__name__}")
            traceback.print_exc()
            return Response(
                {
                    'error': 'An unexpected error occurred',
                    'details': str(e),
                    'type': type(e).__name__
                },
                status=http_status.HTTP_500_INTERNAL_SERVER_ERROR
            )

