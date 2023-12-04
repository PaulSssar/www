# urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from ritual import views

from .views import LoginView, RegistrationView, ReviewExecuterViewSet, RatingViewSet, ChatMessageView, \
    UserDetailView, RequestPasswordResetEmailAPIView, ExecutorListView, ExecutorTGUpdateView, SimpleServiceList, \
    ClientAdminChatAPIView, UnreadMessagesAPIView, SendMessageAPIView

urlpatterns = [
    path('services/', SimpleServiceList.as_view(), name='service-list'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('reviews/<int:executor_id>/', ReviewExecuterViewSet.as_view(), name='executor-reviews'),
    path('ratings/<int:executor_id>/', RatingViewSet.as_view(), name='executor-ratings'),

    path('user/', UserDetailView.as_view(), name='user-detail'),

    path('request_password_reset/', RequestPasswordResetEmailAPIView.as_view(), name='request_password_reset'),

    path('executors/', ExecutorListView.as_view(), name='executors-list'),
    path('executor/update-tg/', ExecutorTGUpdateView.as_view(), name='executor-update-tg'),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    path('messages/', ClientAdminChatAPIView.as_view(), name='client_admin_chat'),
    path('send-message/', SendMessageAPIView.as_view(), name='send_message'),

    # URL для получения списка непрочитанных сообщений
    path('unread-messages/', UnreadMessagesAPIView.as_view(), name='unread_messages'),
]

