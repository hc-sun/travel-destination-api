from django.urls import path, include
from rest_framework.routers import DefaultRouter
from destination import views


app_name = 'destination'

'''
register the viewset with the router
it will automatically generate the urls for viewset
for example:
api/destination/ ^destinations/(?P<pk>[^/.]+)/$ [name='destination-detail']
'''
router = DefaultRouter()
router.register('destinations', views.DestinationViewSet)
router.register('tags', views.TagViewSet)
router.register('features', views.FeatureViewSet)
urlpatterns = [
    path('', include(router.urls))
]
