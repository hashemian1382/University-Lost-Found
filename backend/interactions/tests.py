from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Item
from interactions.models import Comment, Report
from interactions.serializers import CommentSerializer, ReportSerializer


User = get_user_model()


class InteractionsBackendTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.author = User.objects.create_user(email="author@example.com", password="Pass12345")
        self.other = User.objects.create_user(email="other@example.com", password="Pass12345")
        self.item = Item.objects.create(
            title="Lost Phone",
            description="iPhone near library",
            latitude=35.0,
            longitude=51.0,
            type="LOST",
            author=self.author,
        )

    def test_comment_str(self):
        c = Comment.objects.create(item=self.item, author=self.author, text="hello")
        self.assertIn("author@example.com", str(c))

    def test_add_comment_requires_authentication(self):
        response = self.client.post(
            reverse("add-comment"),
            {"item": self.item.id, "text": "test comment"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_comment_sets_author(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.post(
            reverse("add-comment"),
            {"item": self.item.id, "text": "test comment"},
            format="json",
        )
        comment = Comment.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(comment.author, self.other)

    def test_item_comments_lists_only_top_level(self):
        parent = Comment.objects.create(item=self.item, author=self.author, text="parent")
        Comment.objects.create(item=self.item, author=self.other, text="reply", parent=parent)
        response = self.client.get(reverse("item-comments", kwargs={"item_id": self.item.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], parent.id)

    def test_comment_serializer_includes_replies_recursively(self):
        parent = Comment.objects.create(item=self.item, author=self.author, text="parent")
        child = Comment.objects.create(item=self.item, author=self.other, text="child", parent=parent)
        serialized = CommentSerializer(parent).data
        self.assertEqual(serialized["replies"][0]["id"], child.id)
        self.assertEqual(serialized["replies"][0]["text"], "child")

    def test_report_serializer_creates_item_report(self):
        request = self.factory.post("/api/report/")
        request.user = self.other
        serializer = ReportSerializer(
            data={"reason": "SPAM", "content_type_str": "item", "object_id": self.item.id},
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        report = serializer.save()
        self.assertEqual(report.content_object, self.item)

    def test_report_serializer_rejects_invalid_content_type(self):
        request = self.factory.post("/api/report/")
        request.user = self.other
        serializer = ReportSerializer(
            data={"reason": "SPAM", "content_type_str": "post", "object_id": 1},
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        with self.assertRaises(ValidationError):
            serializer.save()

    def test_report_unique_together_prevents_duplicate_report(self):
        ctype = ContentType.objects.get_for_model(Item)
        Report.objects.create(reporter=self.other, reason="SPAM", content_type=ctype, object_id=self.item.id)
        with self.assertRaises(IntegrityError):
            Report.objects.create(
                reporter=self.other, reason="FAKE", content_type=ctype, object_id=self.item.id
            )

    def test_report_threshold_deletes_item_after_5_reports(self):
        ctype = ContentType.objects.get_for_model(Item)
        users = [self.author, self.other]
        for idx in range(3):
            users.append(User.objects.create_user(email=f"user{idx}@example.com", password="Pass12345"))

        for u in users:
            Report.objects.create(reporter=u, reason="SPAM", content_type=ctype, object_id=self.item.id)

        self.item.refresh_from_db()
        self.assertEqual(self.item.status, "DELETED")

    def test_report_threshold_hides_comment_after_5_reports(self):
        comment = Comment.objects.create(item=self.item, author=self.author, text="unsafe")
        ctype = ContentType.objects.get_for_model(Comment)
        reporters = [self.author, self.other]
        for idx in range(3):
            reporters.append(User.objects.create_user(email=f"c{idx}@example.com", password="Pass12345"))

        for u in reporters:
            Report.objects.create(reporter=u, reason="SPAM", content_type=ctype, object_id=comment.id)

        comment.refresh_from_db()
        self.assertEqual(comment.text, "[This comment has been hidden due to reports]")

    def test_report_below_threshold_does_not_delete_item(self):
        ctype = ContentType.objects.get_for_model(Item)
        Report.objects.create(reporter=self.author, reason="SPAM", content_type=ctype, object_id=self.item.id)
        Report.objects.create(reporter=self.other, reason="SPAM", content_type=ctype, object_id=self.item.id)
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, "ACTIVE")

    def test_report_endpoint_requires_auth(self):
        response = self.client.post(
            reverse("report-content"),
            {"reason": "SPAM", "content_type_str": "item", "object_id": self.item.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_report_endpoint_creates_report(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.post(
            reverse("report-content"),
            {"reason": "SPAM", "content_type_str": "item", "object_id": self.item.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Report.objects.count(), 1)
