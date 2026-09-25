from django.core.exceptions import ValidationError
from django.urls import reverse
from django.test import TestCase

from thrill_frame_app.models import (
    PhotoSession,
    User,
    VideoComment,
    VideoWork,
    validate_youtube_input,
)


class ModelBusinessLogicTests(TestCase):
    def test_youtube_validator_accepts_id_and_rejects_invalid_value(self):
        validate_youtube_input("dQw4w9WgXcQ")
        validate_youtube_input("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

        with self.assertRaises(ValidationError):
            validate_youtube_input("not-a-youtube-video")

    def test_video_work_extracts_youtube_id_and_thumbnail(self):
        video = VideoWork.objects.create(
            title="Demo video",
            video_url="https://youtu.be/dQw4w9WgXcQ",
        )

        self.assertEqual(video.youtube_id, "dQw4w9WgXcQ")
        self.assertEqual(
            video.thumbnail_url,
            "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
        )

    def test_photo_session_normalizes_google_drive_urls(self):
        self.assertEqual(
            PhotoSession.normalize_google_drive_url(
                "https://drive.google.com/file/d/example-id/view"
            ),
            "https://lh3.googleusercontent.com/d/example-id",
        )
        self.assertEqual(
            PhotoSession.normalize_google_drive_url(
                "https://example.com/cover.jpg"
            ),
            "https://example.com/cover.jpg",
        )


class InteractionViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="viewer", password="password")
        cls.video = VideoWork.objects.create(
            title="Demo video",
            video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        )
        cls.photo = PhotoSession.objects.create(
            title="Demo photo session",
            drive_folder_url="https://drive.google.com/drive/folders/demo",
        )

    def test_authenticated_user_can_toggle_video_like(self):
        self.client.force_login(self.user)
        url = reverse(
            "thrill_frame_app:toggle_like", kwargs={"video_id": self.video.id}
        )

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["liked"])
        self.assertEqual(self.video.likes.count(), 1)

        response = self.client.post(url)
        self.assertFalse(response.json()["liked"])
        self.assertEqual(self.video.likes.count(), 0)

    def test_photo_like_only_accepts_post(self):
        self.client.force_login(self.user)
        url = reverse(
            "thrill_frame_app:photo_like", kwargs={"pk": self.photo.id}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(self.photo.likes.count(), 0)

        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["liked"])
        self.assertEqual(self.photo.likes.count(), 1)

    def test_authenticated_user_can_add_video_comment(self):
        self.client.force_login(self.user)
        url = reverse(
            "thrill_frame_app:add_comment", kwargs={"video_id": self.video.id}
        )

        response = self.client.post(url, {"text": "A useful comment"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        self.assertTrue(
            VideoComment.objects.filter(
                video=self.video, user=self.user, text="A useful comment"
            ).exists()
        )

    def test_anonymous_user_cannot_toggle_video_like(self):
        url = reverse(
            "thrill_frame_app:toggle_like", kwargs={"video_id": self.video.id}
        )

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("thrill_frame_app:login"), response["Location"])

    def test_invalid_login_does_not_create_user(self):
        response = self.client.post(
            reverse("thrill_frame_app:login"),
            {"username": "new-user", "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="new-user").exists())

    def test_login_rejects_external_redirect(self):
        response = self.client.post(
            reverse("thrill_frame_app:login"),
            {
                "username": "viewer",
                "password": "password",
                "next": "https://example.com/",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("thrill_frame_app:home"))

    def test_missing_parent_comment_does_not_fail(self):
        self.client.force_login(self.user)
        url = reverse(
            "thrill_frame_app:add_comment", kwargs={"video_id": self.video.id}
        )

        response = self.client.post(url, {"text": "Reply", "parent_id": 99999})

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(VideoComment.objects.get(text="Reply").parent)
