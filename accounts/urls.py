from django.urls import path
from .views import ChangeDefaultWalletView, Login, PromoteDemoteUser, Register, TransactionView, WalletListView


urlpatterns = [
    path('register/', Register.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('users/<int:pk>/', PromoteDemoteUser.as_view()),
    path('wallets/', WalletListView.as_view()),
    path('transaction/', TransactionView.as_view()),
    path('wallets/<int:pk>/', ChangeDefaultWalletView.as_view())
]
