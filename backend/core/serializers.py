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
