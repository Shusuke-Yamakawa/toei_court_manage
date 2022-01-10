from django.urls import path

from . import views
from .views import index_views,inquiry_views,toei_views,draw_views,get_views


app_name = 'toei'
urlpatterns = [
    path('', index_views.IndexView.as_view(), name="index"),
    path('inquiry/', inquiry_views.InquiryView.as_view(), name="inquiry"),
    path('toei-list/', toei_views.ToeiListView.as_view(), name="toei_list"),
    path('toei-detail/<int:pk>/', toei_views.ToeiDetailView.as_view(), name="toei_detail"),
    path('toei-create/', toei_views.ToeiCreateView.as_view(), name="toei_create"),
    path('toei-update/<int:pk>/', toei_views.ToeiUpdateView.as_view(), name="toei_update"),
    path('toei-delete/<int:pk>/', toei_views.ToeiDeleteView.as_view(), name="toei_delete"),
    path('draw-list/', draw_views.DrawListView.as_view(), name="draw_list"),
    path('get-list/', get_views.GetListView.as_view(), name="get_list"),
    path('get-detail/<int:pk>/', get_views.GetDetailView.as_view(), name="get_detail"),
    path('get-create/', get_views.GetCreateView.as_view(), name="get_create"),
    path('get-update/<int:pk>/', get_views.GetUpdateView.as_view(), name="get_update"),
    path('get-delete/<int:pk>/', get_views.GetDeleteView.as_view(), name="get_delete"),
]
