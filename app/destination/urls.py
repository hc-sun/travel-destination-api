from django.urls import path, include
from rest_framework.routers import DefaultRouter
from destination import views


app_name = 'destination'
router = DefaultRouter()
# register the viewset with the router
# it will automatically generate the urls for viewset
router.register('destinations', views.DestinationViewSet)
router.register('tags', views.TagViewSet)
urlpatterns = [
    path('', include(router.urls))
]
