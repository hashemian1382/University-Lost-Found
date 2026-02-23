from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import OTPRequest
from users.serializers import ChangePasswordSerializer, SetPasswordSerializer


User = get_user_model()


class UserBackendTests(APITestCase):
    def test_create_user_requires_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password="Pass1234")

    def test_create_user_hashes_password(self):
        user = User.objects.create_user(email="user@example.com", password="Pass1234")
        self.assertTrue(user.check_password("Pass1234"))

    def test_create_superuser_sets_flags(self):
        admin = User.objects.create_superuser(email="admin@example.com", password="Pass1234")
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_otp_generate_returns_6_digits(self):
        otp = OTPRequest.generate_otp()
        self.assertEqual(len(otp), 6)
        self.assertTrue(otp.isdigit())

    def test_otp_is_valid_when_fresh(self):
        otp = OTPRequest.objects.create(email="a@example.com", otp_code="123456")
        self.assertTrue(otp.is_valid())

    def test_otp_is_invalid_after_5_minutes(self):
        otp = OTPRequest.objects.create(email="a@example.com", otp_code="123456")
        OTPRequest.objects.filter(id=otp.id).update(created_at=timezone.now() - timedelta(minutes=6))
        otp.refresh_from_db()
        self.assertFalse(otp.is_valid())

    def test_set_password_serializer_rejects_weak_password(self):
        serializer = SetPasswordSerializer(
            data={
                "email": "x@example.com",
                "otp_code": "111111",
                "password": "weak",
                "first_name": "A",
                "last_name": "B",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_change_password_serializer_accepts_strong_password(self):
        serializer = ChangePasswordSerializer(
            data={"old_password": "OldPass123", "new_password": "NewPass123"}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    @patch("users.views.send_otp_email", return_value=True)
    def test_send_otp_success(self, _mock_send):
        response = self.client.post(
            reverse("send-otp"),
            {"email": "otp@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(OTPRequest.objects.filter(email="otp@example.com").count(), 1)

    @patch("users.views.send_otp_email", return_value=False)
    def test_send_otp_email_failure_returns_500(self, _mock_send):
        response = self.client.post(
            reverse("send-otp"),
            {"email": "otp@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_verify_otp_success_marks_verified(self):
        otp = OTPRequest.objects.create(email="v@example.com", otp_code="222222", is_verified=False)
        response = self.client.post(
            reverse("verify-otp"),
            {"email": "v@example.com", "otp_code": "222222"},
            format="json",
        )
        otp.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(otp.is_verified)

    def test_verify_otp_rejects_expired_code(self):
        otp = OTPRequest.objects.create(email="v@example.com", otp_code="222222", is_verified=False)
        OTPRequest.objects.filter(id=otp.id).update(created_at=timezone.now() - timedelta(minutes=10))
        response = self.client.post(
            reverse("verify-otp"),
            {"email": "v@example.com", "otp_code": "222222"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_set_password_creates_user_and_deletes_verified_otp(self):
        OTPRequest.objects.create(email="new@example.com", otp_code="333333", is_verified=True)
        response = self.client.post(
            reverse("set-password"),
            {
                "email": "new@example.com",
                "otp_code": "333333",
                "password": "StrongPass123",
                "first_name": "New",
                "last_name": "User",
            },
            format="json",
        )
        user = User.objects.get(email="new@example.com")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(user.check_password("StrongPass123"))
        self.assertEqual(OTPRequest.objects.filter(email="new@example.com").count(), 0)

    def test_change_password_requires_correct_old_password(self):
        user = User.objects.create_user(email="cp@example.com", password="OldPass123")
        self.client.force_authenticate(user=user)
        response = self.client.post(
            reverse("change-password"),
            {"old_password": "WrongPass123", "new_password": "NewPass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_success(self):
        user = User.objects.create_user(email="cp@example.com", password="OldPass123")
        self.client.force_authenticate(user=user)
        response = self.client.post(
            reverse("change-password"),
            {"old_password": "OldPass123", "new_password": "NewPass123"},
            format="json",
        )
        user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(user.check_password("NewPass123"))

    def test_profile_requires_authentication(self):
        response = self.client.get(reverse("user-profile"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_update_works_for_authenticated_user(self):
        user = User.objects.create_user(email="profile@example.com", password="Pass12345")
        self.client.force_authenticate(user=user)
        response = self.client.patch(
            reverse("user-profile"),
            {"first_name": "Ali", "phone_number": "09000000000"},
            format="json",
        )
        user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.first_name, "Ali")
