from django.urls import path
from . import views

app_name = 'membership'
urlpatterns = [
    path('', views.index, name='index'),
    #path('<int:member_id>/', views.detail, name='detail'),
    path('<int:member_id>/recharge/', views.recharge, name='recharge'),
    path('<int:member_id>/start_usage/', views.start_usage, name='start_usage'),
    path('<int:usage_id>/usage/', views.usage, name='usage'),
    path('<int:usage_id>/end_usage/', views.end_usage, name='end_usage'),
    path('<int:member_id>/delete/', views.delete_member, name='delete_member'),
    path('add_member/', views.add_member, name='add_member'),
    path('<int:member_id>/edit/', views.edit_member, name='edit_member'),
    path('memberlist/', views.member_list, name='member_list'),
    path('edit_member/<int:member_id>/', views.edit_member, name='edit_member'),
    path('delete_member/<int:member_id>/', views.delete_member, name='delete_member'),
    path('search/', views.search_member, name='search_member'),
    path('timer/', views.timer_view, name='timer'),
    path('pool_tables/', views.pool_table_view, name='pool_tables'),
    path('deposit/', views.deposit, name='deposit'),
    path('consume/', views.consume, name='consume'),
    path('get_table_status/', views.get_table_status, name='get_table_status'), 
    path('<int:member_id>/', views.member_detail, name='detail'),
]
