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
    API endpoint for chatbot service that extracts structured information
    from natural language descriptions and searches for similar items
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Process user's natural language description, extract info, and find similar items
        
        Request body:
        {
            "description": "User's description of lost or found item",
            "search": true  // Optional: set to false to skip search
        }
        
        Response:
        {
            "extracted_info": {
                "type": "LOST" or "FOUND",
                "title": "Item title",
                "description": "Detailed description",
                "location_description": "Location description",
                "latitude": float or null,
                "longitude": float or null,
                "tags": ["tag1", "tag2", ...]
            },
            "similar_items": [...],  // Array of similar items found
            "total_matches": 5       // Number of matches found
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
        should_search = request.data.get('search', True)  # Default to True
        
        print(f"\n=== CHATBOT REQUEST ===")
        print(f"User: {request.user}")
        print(f"Description: {user_description[:100]}...")
        print(f"Should search: {should_search}")
        
        try:
            # Initialize AI service and extract information
            print("Step 1: Initializing ChatBotService...")
            chatbot_service = ChatBotService()
            print("Step 2: Calling extract_item_info...")
            result = chatbot_service.extract_item_info(user_description)
            print(f"Step 3: Got result - success: {result.get('success')}")
            
            if not result['success']:
                print(f"ERROR: AI extraction failed - {result.get('error')}")
                return Response(
                    {
                        'error': 'Failed to process description',
                        'details': result.get('error', 'Unknown error')
                    },
                    status=http_status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            print("Step 4: Extracting data from result...")
            extracted_data = result['data']
            print(f"Step 5: Data keys: {extracted_data.keys()}")
            
            # Validate extracted info
            print("Step 6: Validating with ChatBotResponseSerializer...")
            response_serializer = ChatBotResponseSerializer(data=extracted_data)
            if not response_serializer.is_valid():
                print(f"ERROR: Validation failed - {response_serializer.errors}")
                return Response(
                    {
                        'error': 'Invalid response from AI',
                        'details': response_serializer.errors
                    },
                    status=http_status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            print("Step 7: Validation successful!")
            
            # If search is disabled, return only extracted info
            if not should_search:
                print("Step 8: Search disabled, returning extracted info only")
                return Response(
                    response_serializer.data,
                    status=http_status.HTTP_200_OK
                )
            
            # Search for similar items in database
            print("Step 8: Initializing ItemSearchService...")
            search_service = ItemSearchService()
            print("Step 9: Searching for similar items...")
            similar_items = search_service.search_similar_items(extracted_data)
            print(f"Step 10: Found {len(similar_items)} similar items")
            
            # Calculate match scores for each item
            print("Step 11: Calculating match scores...")
            for item in similar_items:
                item.match_score = search_service.get_match_score(extracted_data, item)
            
            # Sort by match score (highest first)
            print("Step 12: Sorting items...")
            similar_items.sort(key=lambda x: x.match_score, reverse=True)
            
            # Serialize similar items
            print("Step 13: Serializing similar items...")
            similar_items_serializer = SimilarItemSerializer(similar_items, many=True)
            
            # Prepare complete response
            print("Step 14: Preparing complete response...")
            complete_response = {
                'extracted_info': response_serializer.data,
                'similar_items': similar_items_serializer.data,
                'total_matches': len(similar_items)
            }
            
            print("Step 15: SUCCESS! Returning response.")
            return Response(
                complete_response,
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

