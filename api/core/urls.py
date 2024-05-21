from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AddCommentView,
    AsideView,
    FeedBackView,
    GetCommentsView,
    PostViewSet,
    ProfileView,
    RegisterView,
    SubscribeAPIView,
    TagDetailView,
    TagView,
    UnsubscribeAPIView,
)

router = DefaultRouter()
router.register("posts", PostViewSet, basename="posts")

urlpatterns = [
    path("", include(router.urls)),
    path("tags/", TagView.as_view()),
    path("tags/<slug:tag_slug>/", TagDetailView.as_view()),
    path("aside/", AsideView.as_view()),
    path("feedback/", FeedBackView.as_view()),
    path("register/", RegisterView.as_view()),
    path("profile/", ProfileView.as_view()),
    path("comments/", AddCommentView.as_view()),
    path("comments/<slug:post_slug>/", GetCommentsView.as_view()),
    path(
        "subscribe/newsletter/<int:user_id>/",
        SubscribeAPIView.as_view(),
        name="subscribe-newsletter",
    ),
    path(
        "unsubscribe/newsletter/<int:user_id>/",
        UnsubscribeAPIView.as_view(),
        name="unsubscribe-newsletter",
    ),
]
