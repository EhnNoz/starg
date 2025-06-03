from django.urls import path, include
# from .views import (
#     StoryModelListCreateAPIView,
#     StoryModelRetrieveUpdateDestroyAPIView,
#     TopicListAPIView
# )
from .views import StoryModelViewSet, TopicViewSet, StateStoryModelViewSet, InstagramPageViewSet, CategoryViewSet, \
    DayAnalysisViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'storymodel', StoryModelViewSet, basename='storymodel')
router.register(r'topics', TopicViewSet, basename='topic')
router.register(r'stats', StateStoryModelViewSet, basename='stats')
router.register(r'instagram-pages', InstagramPageViewSet, basename='instagram-page')
router.register(r'category', CategoryViewSet, basename='category')
router.register(r'dayanalysis', DayAnalysisViewSet, basename='dayanalysis')


urlpatterns = [
    path('', include(router.urls)),
]

# urlpatterns = [
#     path('topics/', TopicListAPIView.as_view(), name='topic-list'),
#     path('storymodel/', StoryModelViewSet.as_view(), name='storymodel')
#     # path('storymodel/', StoryModelListCreateAPIView.as_view(), name='storymodel-list-create'),
#     # path('storymodel/<int:pk>/', StoryModelRetrieveUpdateDestroyAPIView.as_view(), name='storymodel-retrieve-update-destroy'),
# ]