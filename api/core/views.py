from rest_framework import filters, generics, pagination, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from taggit.models import Tag

from .models import Comment, Post, User
from .serializers import (
    CommentSerializer,
    ContactSerializer,
    PostSerializer,
    RegisterSerializer,
    TagSerializer,
    UserSerializer,
)
from .tasks import send_feedback_email


class PageNumberSetPagination(pagination.PageNumberPagination):
    page_size = 6
    page_size_query_param = "page_size"
    ordering = "created_at"


class PostViewSet(viewsets.ModelViewSet):
    search_fields = ["h1"]
    filter_backends = (filters.SearchFilter,)
    serializer_class = PostSerializer
    queryset = Post.objects.all().order_by("-created_at")
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]
    pagination_class = PageNumberSetPagination


class TagDetailView(generics.ListAPIView):
    serializer_class = PostSerializer
    pagination_class = PageNumberSetPagination
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        tag_slug = self.kwargs["tag_slug"].lower()
        tag = Tag.objects.get(slug=tag_slug)
        return Post.objects.filter(tags=tag)


class TagView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class AsideView(generics.ListAPIView):
    queryset = Post.objects.all().order_by("-created_at")[:5]
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]


class FeedBackView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ContactSerializer

    def post(self, request, *args, **kwargs) -> Response:
        serializer_class = ContactSerializer(data=request.data)
        if serializer_class.is_valid():
            data = serializer_class.validated_data
            name = data.get("name")
            from_email = data.get("email")
            subject = data.get("subject")
            message = data.get("message")
            send_feedback_email.delay(
                subject=f"От {name} | {subject} | email: {from_email}",
                message=message,
                from_email=from_email,
            )
            return Response({"success": "Sent"}, status=status.HTTP_200_OK)
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "message": "Пользователь успешно создан",
            }
        )


class ProfileView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs) -> Response:
        return Response(
            {
                "user": UserSerializer(
                    request.user, context=self.get_serializer_context()
                ).data,
            }
        )


class AddCommentView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]


class GetCommentsView(generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        post_slug = self.kwargs["post_slug"].lower()
        post = Post.objects.get(slug=post_slug)
        return Comment.objects.filter(post=post)


class SubscribeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
                user.subscribed_to_newsletter = True
                user.save()
                return Response(
                    {"message": "Subscribed to feed successfully"},
                    status=status.HTTP_200_OK,
                )
            except User.DoesNotExist:
                return Response(
                    {"message": "User does not exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"message": "User ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UnsubscribeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
                user.subscribed_to_newsletter = False
                user.save()
                return Response(
                    {"message": "Unsubscribed to feed successfully"},
                    status=status.HTTP_200_OK,
                )
            except User.DoesNotExist:
                return Response(
                    {"message": "User does not exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"message": "User ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
