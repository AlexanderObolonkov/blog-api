from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_newsletter_email(user_id, post_title, post_slug):
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        user = User.objects.get(pk=user_id)
        unsubscribe_newsletter_url = (
            f"{settings.FRONTEND_URL}/unsubscribe/newsletter/{user.id}"
        )

        subject = f"Новый Пост: {post_title}"
        from_email = settings.EMAIL_HOST_USER
        message = f"""
        <p>Привет, {user.username}!</p>
        <p>Новый пост "{post_title}" был опубликован.</p>
        <p>Подробнее по ссылке: {settings.FRONTEND_URL}/posts/{post_slug}</p>

        <p>Если вы хотите отписаться от уведомлений о выходе новых постой, перейдите по следующей ссылке:</p>
        <p><a href="{unsubscribe_newsletter_url}">Отписаться от всех рассылок</a></p>
        """

        send_mail(
            subject,
            "",
            from_email,
            [user.email],
            fail_silently=False,
            html_message=message,
        )
    except User.DoesNotExist:
        print(f"User with id {user_id} does not exist")


@shared_task
def send_feedback_email(subject, message, from_email):
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.EMAIL_HOST_USER],
        fail_silently=False,
    )
