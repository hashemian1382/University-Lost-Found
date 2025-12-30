from rest_framework import serializers
from .models import Item, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class ItemSerializer(serializers.ModelSerializer):
    author_email = serializers.ReadOnlyField(source='author.email')
    
    class Meta:
        model = Item
        fields = '__all__'
        read_only_fields = ['author', 'created_at', 'updated_at', 'status']

class MapItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'latitude', 'longitude', 'type']