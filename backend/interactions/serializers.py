# backend\interactions\serializers.py
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Comment, Report
from core.models import Item

class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class CommentSerializer(serializers.ModelSerializer):
    author_email = serializers.ReadOnlyField(source='author.email')
    author_name = serializers.SerializerMethodField()
    replies = RecursiveField(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'item', 'author_email', 'author_name', 'text', 'parent', 'created_at', 'replies']
        read_only_fields = ['author_email', 'created_at', 'replies']

    def get_author_name(self, obj):
        if obj.author.first_name and obj.author.last_name:
            return f"{obj.author.first_name} {obj.author.last_name}"
        return obj.author.email.split('@')[0]

class ReportSerializer(serializers.ModelSerializer):
    content_type_str = serializers.CharField(write_only=True)
    
    class Meta:
        model = Report
        fields = ['id', 'reason', 'content_type_str', 'object_id']
    
    def create(self, validated_data):
        c_type_str = validated_data.pop('content_type_str')
        if c_type_str == 'item':
            model_class = Item
        elif c_type_str == 'comment':
            model_class = Comment
        else:
            raise serializers.ValidationError("Invalid content type. Use 'item' or 'comment'.")
            
        validated_data['content_type'] = ContentType.objects.get_for_model(model_class)
        validated_data['reporter'] = self.context['request'].user
        return super().create(validated_data)
