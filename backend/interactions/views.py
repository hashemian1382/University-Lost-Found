from rest_framework import generics, permissions, exceptions
from .models import Comment, Report
from .serializers import CommentSerializer, ReportSerializer
from core.models import Item

class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class ItemCommentsListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        item_id = self.kwargs['item_id']
        # Only fetch top-level comments; serializer handles recursion
        return Comment.objects.filter(item_id=item_id, parent__isnull=True).order_by('-created_at')

class ReportCreateView(generics.CreateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]