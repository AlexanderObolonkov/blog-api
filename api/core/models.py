from ckeditor_uploader.fields import RichTextUploadingField
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from taggit.managers import TaggableManager
from unidecode import unidecode  # noqa: F401


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

        subject = f"Новый Пост: {self.title}"
        from_email = settings.EMAIL_HOST_USER

        for user in newsletter_subscribers:
            unsubscribe_newsletter_url = (
                f"{settings.FRONTEND_URL}/unsubscribe/newsletter/{user.id}"
            )

            message = f"""
            <p>Привет, {user.username}!</p>
            <p>Новый пост "{self.title}" был опубликован.</p>
            <p>Подробнее по ссылке: {settings.FRONTEND_URL}/posts/{self.slug}</p>

            <p>Если вы хотите отписаться от уведомлений о выходе новых постой, перейдите по следующей ссылке:</p>
            <p><a href="{unsubscribe_newsletter_url}">Отписаться от всех рассылок</a> (Ссылка: {unsubscribe_newsletter_url})</p>
            """

            send_mail(
                subject,
                "",
                from_email,
                [user.email],
                fail_silently=False,
                html_message=message,
            )


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
