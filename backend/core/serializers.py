# backend/core/serializers.py
from rest_framework import serializers
from .models import Item, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class ItemSerializer(serializers.ModelSerializer):
    author_email = serializers.ReadOnlyField(source='author.email')
    author_name = serializers.SerializerMethodField()
    tags_details = TagSerializer(source='tags', many=True, read_only=True)

    class Meta:
        model = Item
        fields = '__all__'
        read_only_fields = ['author', 'created_at', 'updated_at', 'status', 'tags_details']

    def get_author_name(self, obj):
        if obj.author.first_name and obj.author.last_name:
            return f"{obj.author.first_name} {obj.author.last_name}"
        return obj.author.email.split('@')[0]

class MapItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'latitude', 'longitude', 'type']


# Chatbot Serializers
class ChatBotRequestSerializer(serializers.Serializer):
    """Serializer for chatbot input - user's description of lost/found item"""
    description = serializers.CharField(
        required=True,
        allow_blank=False,
        help_text="User's natural language description of the lost or found item"
    )

class ChatBotResponseSerializer(serializers.Serializer):
    """Serializer for chatbot output - structured item information"""
    type = serializers.ChoiceField(
        choices=['LOST', 'FOUND'],
        help_text="Whether the item is lost or found"
    )
    title = serializers.CharField(
        max_length=200,
        help_text="Short title for the item"
    )
    description = serializers.CharField(
        help_text="Detailed description of the item"
    )
    location_description = serializers.CharField(
        allow_blank=True,
        help_text="Description of where the item was lost or found"
    )
    latitude = serializers.FloatField(
        required=False,
        allow_null=True,
        help_text="Latitude coordinate if location is known"
    )
    longitude = serializers.FloatField(
        required=False,
        allow_null=True,
        help_text="Longitude coordinate if location is known"
    )
    tags = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of relevant tags for the item"
    )


class SimilarItemSerializer(serializers.ModelSerializer):
    """Serializer for similar items found in search results"""
    author_email = serializers.ReadOnlyField(source='author.email')
    author_name = serializers.SerializerMethodField()
    tags_details = TagSerializer(source='tags', many=True, read_only=True)
    match_score = serializers.FloatField(read_only=True, required=False)
    
    class Meta:
        model = Item
        fields = [
            'id', 'title', 'description', 'image', 'latitude', 'longitude',
            'type', 'author', 'author_email', 'author_name', 'tags_details',
            'created_at', 'match_score'
        ]
    
    def get_author_name(self, obj):
        if obj.author.first_name and obj.author.last_name:
            return f"{obj.author.first_name} {obj.author.last_name}"
        return obj.author.email.split('@')[0]


class ChatBotSearchResponseSerializer(serializers.Serializer):
    """Serializer for chatbot response with extracted info and similar items"""
    extracted_info = ChatBotResponseSerializer()
    similar_items = SimilarItemSerializer(many=True)
    total_matches = serializers.IntegerField()

