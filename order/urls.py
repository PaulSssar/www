from django.urls import include, path
from order.views import CartListView, CartCreateView, OrderListView, UserOrderListView, \
    NotificationListAPIView, NotificationUpdateAPIView, OrderExecutorsListView, AssignExecutorView, \
    PhotoReportUploadView, OrderCreateFromCartAPIView
from rest_framework.routers import DefaultRouter
from ritual.views import UnreadMessagesAPIView, SendMessageAPIView, MarkMessageAsReadAPIView

from .views import CartItemViewSet, CartViewSet

router = DefaultRouter()
router.register(r'cart-items', CartItemViewSet)
router.register(r'carts', CartViewSet)


urlpatterns = [
    # path('cart/', CartListView.as_view(), name='cart-list'),
    # path('cart/create/', CartCreateView.as_view(), name='cart-create'),
    path('create/', OrderCreateFromCartAPIView.as_view(), name='create-order'),
    path('by-city/', OrderListView.as_view(), name='orders-by-city'),
    path('by-user/', UserOrderListView.as_view(), name='orders-by-user'),
    path('<int:order_id>/executors/', OrderExecutorsListView.as_view(), name='order-executors-list'),

    path('notifications/', NotificationListAPIView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/', NotificationUpdateAPIView.as_view(), name='notification-update'),

    path('assign-executor/', AssignExecutorView.as_view(), name='assign-executor'),
    path('<int:order_id>/upload-photos/', PhotoReportUploadView.as_view(), name='upload-photo-reports'),

    # URL для отправки сообщения


    # URL для пометки сообщения как прочитанного
    path('mark-message-as-read/<int:pk>/', MarkMessageAsReadAPIView.as_view(), name='mark_message_as_read'),
    path('', include(router.urls)),
]