"""
Search service for finding similar items in database
based on extracted information from AI
"""
from typing import Dict, List
from django.db.models import Q
from .models import Item, Tag


class ItemSearchService:
    """Service for searching similar items in database"""
    
    @staticmethod
    def search_similar_items(extracted_data: Dict, max_results: int = 10) -> List[Item]:
        """
        Search for similar items in database based on AI extracted information
        
        Args:
            extracted_data: Dictionary containing extracted item information
                {
                    "type": "LOST" or "FOUND",
                    "title": "Item title",
                    "description": "Description",
                    "tags": ["tag1", "tag2"],
                    "latitude": float or None,
                    "longitude": float or None
                }
            max_results: Maximum number of results to return
            
        Returns:
            List of similar Item objects
        """
        item_type = extracted_data.get('type', 'LOST')
        tags = extracted_data.get('tags', [])
        latitude = extracted_data.get('latitude')
        longitude = extracted_data.get('longitude')
        title = extracted_data.get('title', '')
        description = extracted_data.get('description', '')
        
        # Start with base query - search for opposite type
        # If user lost something, search in found items and vice versa
        opposite_type = 'FOUND' if item_type == 'LOST' else 'LOST'
        queryset = Item.objects.filter(
            status='ACTIVE',
            type=opposite_type
        )
        
        # Build search query
        search_query = Q()
        
        # Search by title and description keywords
        keywords = ItemSearchService._extract_keywords(title, description)
        for keyword in keywords:
            search_query |= Q(title__icontains=keyword) | Q(description__icontains=keyword)
        
        if search_query:
            queryset = queryset.filter(search_query)
        
        # Filter by tags if available
        if tags:
            tag_objects = Tag.objects.filter(name__in=tags)
            if tag_objects.exists():
                queryset = queryset.filter(tags__in=tag_objects).distinct()
        
        # Filter by location if coordinates are available
        if latitude is not None and longitude is not None:
            # Search within approximately 0.01 degree radius (~1km)
            lat_range = 0.01
            lon_range = 0.01
            queryset = queryset.filter(
                latitude__gte=latitude - lat_range,
                latitude__lte=latitude + lat_range,
                longitude__gte=longitude - lon_range,
                longitude__lte=longitude + lon_range
            )
        
        # Order by most recent first
        queryset = queryset.order_by('-created_at')
        
        # Limit results
        return list(queryset[:max_results])
    
    @staticmethod
    def _extract_keywords(title: str, description: str) -> List[str]:
        """
        Extract important keywords from title and description
        Removes common words and returns meaningful terms
        """
        # Combine title and description
        text = f"{title} {description}".lower()
        
        # Common stop words to ignore (English)
        stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'my', 'your', 'his', 'her', 'its', 'our', 'their', 'lost', 'found',
            'item', 'near', 'around', 'yesterday', 'today', 'color'
        }
        
        # Split into words and clean
        words = text.split()
        keywords = []
        
        for word in words:
            # Remove punctuation
            word = ''.join(char for char in word if char.isalnum())
            # Keep words that are longer than 2 characters and not stop words
            if len(word) > 2 and word not in stop_words:
                keywords.append(word)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        return unique_keywords[:10]  # Return max 10 keywords
    
    @staticmethod
    def get_match_score(extracted_data: Dict, item: Item) -> float:
        """
        Calculate a match score between extracted data and an item
        Score ranges from 0 to 1, where 1 is a perfect match
        
        Args:
            extracted_data: Dictionary containing extracted information
            item: Item object from database
            
        Returns:
            Float score between 0 and 1
        """
        score = 0.0
        max_score = 0.0
        
        # Check tags match (weight: 0.4)
        max_score += 0.4
        tags = extracted_data.get('tags', [])
        if tags and item.tags.exists():
            item_tag_names = [tag.name for tag in item.tags.all()]
            matching_tags = len(set(tags) & set(item_tag_names))
            score += (matching_tags / len(tags)) * 0.4
        
        # Check keyword match in title/description (weight: 0.4)
        max_score += 0.4
        keywords = ItemSearchService._extract_keywords(
            extracted_data.get('title', ''),
            extracted_data.get('description', '')
        )
        item_text = f"{item.title} {item.description}".lower()
        matching_keywords = sum(1 for kw in keywords if kw in item_text)
        if keywords:
            score += (matching_keywords / len(keywords)) * 0.4
        
        # Check location proximity (weight: 0.2)
        max_score += 0.2
        latitude = extracted_data.get('latitude')
        longitude = extracted_data.get('longitude')
        if latitude is not None and longitude is not None:
            lat_diff = abs(item.latitude - latitude)
            lon_diff = abs(item.longitude - longitude)
            distance = (lat_diff + lon_diff) / 2  # Simple distance metric
            # Close proximity gets higher score (distance < 0.01 = ~1km)
            if distance < 0.01:
                score += 0.2 * (1 - min(distance / 0.01, 1))
        
        return score / max_score if max_score > 0 else 0.0
