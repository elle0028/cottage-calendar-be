"""cottageCalendar URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from rest_framework import routers
from scheduler import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
# router.register(r'notes', views.NoteViewSet)
# router.register(r'dates', views.DateViewSet)

urlpatterns = [
    # path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
    path('date/<str:id>', views.getDateById),
    path('date', views.createDate),
    path('notes', views.createNote),
    path('note/<int:id>', views.getNote),
    # url(r'^.*', TemplateView.as_view(template_name="home.html"), name="home")
    re_path(r'^$', TemplateView.as_view(template_name="home.html"))
]
