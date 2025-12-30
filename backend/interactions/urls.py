from django.urls import path
from .views import CommentCreateView, ItemCommentsListView, ReportCreateView

urlpatterns = [
    path('comments/add/', CommentCreateView.as_view(), name='add-comment'),
    path('items/<int:item_id>/comments/', ItemCommentsListView.as_view(), name='item-comments'),
    path('report/', ReportCreateView.as_view(), name='report-content'),
]