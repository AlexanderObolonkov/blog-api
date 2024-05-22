from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from taggit.managers import TaggableManager
from unidecode import unidecode  # noqa: F401

from .tasks import send_newsletter_email


class User(AbstractUser):
    profile_image = models.ImageField(
        upload_to="profile_images/", null=True, blank=True
    )
    subscribed_to_newsletter = models.BooleanField(default=False)
    subscribed_tags = TaggableManager(blank=True)

    def __str__(self):
        return self.username


class Post(models.Model):
    h1 = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = RichTextUploadingField()
    content = RichTextUploadingField()
    image = models.ImageField(null=True, blank=True, upload_to="posts/")
    created_at = models.DateField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = TaggableManager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.notify_subscribers()

    def notify_subscribers(self):
        newsletter_subscribers = User.objects.filter(subscribed_to_newsletter=True)

        for user in newsletter_subscribers:
            send_newsletter_email.delay(user.id, self.title, self.slug)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    username = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_name"
    )
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):
        return self.text
