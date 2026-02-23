from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.ai_service import ChatBotService
from core.models import Item, Tag
from core.permissions import IsOwnerOrReadOnly
from core.search_service import ItemSearchService
from core.serializers import ItemSerializer


User = get_user_model()


class CoreBackendTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(email="owner@example.com", password="Pass12345")
        self.other = User.objects.create_user(email="other@example.com", password="Pass12345")
        self.tag_keys = Tag.objects.create(name="Keys")
        self.tag_electronics = Tag.objects.create(name="Electronics")

    def _create_item(self, **kwargs):
        defaults = {
            "title": "Lost Keys",
            "description": "Silver keys near engineering building",
            "latitude": 35.0,
            "longitude": 51.0,
            "type": "LOST",
            "status": "ACTIVE",
            "author": self.owner,
        }
        defaults.update(kwargs)
        return Item.objects.create(**defaults)

    def test_tag_str(self):
        self.assertEqual(str(self.tag_keys), "Keys")

    def test_item_str(self):
        item = self._create_item(title="Macbook")
        self.assertEqual(str(item), "Macbook")

    def test_permission_allows_safe_method(self):
        permission = IsOwnerOrReadOnly()
        request = Mock(method="GET", user=self.other)
        item = self._create_item(author=self.owner)
        self.assertTrue(permission.has_object_permission(request, None, item))

    def test_permission_denies_non_owner_write(self):
        permission = IsOwnerOrReadOnly()
        request = Mock(method="PATCH", user=self.other)
        item = self._create_item(author=self.owner)
        self.assertFalse(permission.has_object_permission(request, None, item))

    def test_item_serializer_author_name_uses_full_name(self):
        self.owner.first_name = "John"
        self.owner.last_name = "Doe"
        self.owner.save()
        item = self._create_item(author=self.owner)
        serializer = ItemSerializer(item)
        self.assertEqual(serializer.data["author_name"], "John Doe")

    def test_item_serializer_author_name_fallback_to_email_prefix(self):
        item = self._create_item(author=self.owner)
        serializer = ItemSerializer(item)
        self.assertEqual(serializer.data["author_name"], "owner")

    def test_item_create_sets_author(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            reverse("item-list"),
            {
                "title": "Found Wallet",
                "description": "Brown wallet",
                "latitude": 10.0,
                "longitude": 20.0,
                "type": "FOUND",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        item = Item.objects.get(id=response.data["id"])
        self.assertEqual(item.author, self.owner)

    def test_item_queryset_bbox_filter(self):
        in_box = self._create_item(title="Inside", latitude=10.5, longitude=20.5, type="LOST")
        self._create_item(title="Outside", latitude=40.0, longitude=70.0, type="LOST")
        response = self.client.get(
            reverse("item-list"),
            {
                "min_lat": 10.0,
                "max_lat": 11.0,
                "min_lon": 20.0,
                "max_lon": 21.0,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [row["id"] for row in response.data]
        self.assertIn(in_box.id, ids)
        self.assertEqual(len(ids), 1)

    def test_map_data_view_returns_lightweight_fields(self):
        self._create_item()
        response = self.client.get(reverse("map-data"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        first = response.data[0]
        self.assertSetEqual(set(first.keys()), {"id", "latitude", "longitude", "type"})

    def test_tag_list_view_public(self):
        response = self.client.get(reverse("tag-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_extract_keywords_removes_stop_words_and_duplicates(self):
        keywords = ItemSearchService._extract_keywords(
            "Lost lost blue wallet",
            "the wallet was in the library and wallet was blue",
        )
        self.assertIn("blue", keywords)
        self.assertIn("wallet", keywords)
        self.assertNotIn("the", keywords)
        self.assertEqual(keywords.count("wallet"), 1)

    def test_search_similar_items_uses_opposite_type_and_title_priority(self):
        found_match = self._create_item(
            title="Blue Wallet",
            description="Found in library",
            type="FOUND",
            author=self.other,
        )
        self._create_item(
            title="Random Item",
            description="blue wallet text in description only",
            type="FOUND",
            author=self.other,
        )
        results = ItemSearchService.search_similar_items(
            {"type": "LOST", "title": "Blue Wallet", "description": "", "tags": []},
            max_results=5,
        )
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0].id, found_match.id)

    def test_search_similar_items_with_tags_and_location(self):
        nearby = self._create_item(
            title="Phone",
            description="Found smartphone",
            type="FOUND",
            latitude=35.001,
            longitude=51.001,
            author=self.other,
        )
        nearby.tags.add(self.tag_electronics)

        far = self._create_item(
            title="Phone Far",
            description="Found smartphone",
            type="FOUND",
            latitude=40.0,
            longitude=50.0,
            author=self.other,
        )
        far.tags.add(self.tag_electronics)

        results = ItemSearchService.search_similar_items(
            {
                "type": "LOST",
                "title": "phone",
                "description": "smartphone",
                "tags": ["Electronics"],
                "latitude": 35.0,
                "longitude": 51.0,
            },
            max_results=10,
        )
        self.assertIn(nearby.id, [x.id for x in results])
        self.assertNotIn(far.id, [x.id for x in results])

    def test_get_match_score_range(self):
        item = self._create_item(title="Blue Wallet", description="Leather wallet near gate")
        item.tags.add(self.tag_keys)
        score = ItemSearchService.get_match_score(
            {
                "title": "Blue Wallet",
                "description": "Leather wallet",
                "tags": ["Keys"],
                "latitude": 35.0,
                "longitude": 51.0,
            },
            item,
        )
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)

    @override_settings(USE_MOCK_AI=True)
    def test_chatbot_validate_and_clean_result_sanitizes_fields(self):
        with patch("core.ai_service.os.getenv") as mock_getenv:
            mock_getenv.side_effect = lambda key, default=None: {
                "GROQ_API_KEY": "test-key",
                "USE_MOCK_AI": "true",
            }.get(key, default)
            service = ChatBotService()
        cleaned = service._validate_and_clean_result(
            {
                "type": "invalid",
                "title": "T" * 300,
                "description": "",
                "location_description": "",
                "latitude": "500",
                "longitude": "not-a-number",
                "tags": ["Electronics", "BadTag"],
            }
        )
        self.assertEqual(cleaned["type"], "LOST")
        self.assertEqual(len(cleaned["title"]), 200)
        self.assertEqual(cleaned["latitude"], None)
        self.assertEqual(cleaned["longitude"], None)
        self.assertEqual(cleaned["tags"], ["Electronics"])

    @override_settings(USE_MOCK_AI=True)
    def test_chatbot_mock_find_related_items_returns_top_matches(self):
        with patch("core.ai_service.os.getenv") as mock_getenv:
            mock_getenv.side_effect = lambda key, default=None: {
                "GROQ_API_KEY": "test-key",
                "USE_MOCK_AI": "true",
            }.get(key, default)
            service = ChatBotService()
        result = service.find_related_items(
            "lost blue wallet in library",
            [
                {"id": 1, "title": "Blue Wallet", "description": "found in library", "type": "FOUND"},
                {"id": 2, "title": "Red Book", "description": "found in class", "type": "FOUND"},
            ],
        )
        self.assertTrue(result["success"])
        self.assertIn(1, result["data"]["related_item_ids"])

    @patch("core.views.ChatBotService")
    def test_chatbot_view_returns_related_items(self, mock_service_cls):
        match_item = self._create_item(title="Blue Wallet", description="Found near library", type="FOUND")
        self.client.force_authenticate(user=self.owner)

        mock_service = mock_service_cls.return_value
        mock_service.find_related_items.return_value = {
            "success": True,
            "data": {"related_item_ids": [match_item.id], "explanation": "matched"},
        }

        response = self.client.post(
            reverse("chatbot"),
            {"description": "I lost a blue wallet"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_matches"], 1)
