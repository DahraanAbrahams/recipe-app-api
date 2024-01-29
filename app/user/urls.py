"""
URL mappings for the User API
"""

from django.urls import path

from user import views

app_name = 'user' #We define app_name to equal 'user'. CREATE_USER_URL = reverse('user:create') will be looking for this mapping

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'), #Any req to 'create/' will be handled by the CreateUserView view that we created in view
]
