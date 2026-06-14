# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.index, name='index'),
    path('go/<int:link_id>/', views.track_click, name='track_click'),
    path('api/suggest/', views.auto_suggest, name='auto_suggest'),
    path('api/bookmark/<int:link_id>/', views.toggle_bookmark, name='toggle_bookmark'),
    path('api/rate/<int:link_id>/', views.rate_link, name='rate_link'),
    path('api/report/<int:link_id>/', views.submit_report, name='submit_report'),
    path('api/feedback/', views.submit_feedback, name='submit_feedback'),
    path('api/bookmarks/', views.get_bookmarks, name='get_bookmarks'),

    # SEO friendly
    path('service/<slug:slug>/', views.service_page, name='service_page'),
    path('category/<slug:slug>/', views.category_page, name='category_page'),

    # Admin (hidden)
    path('secret-admin-portal/', views.admin_login_view, name='admin_login'),
    path('secret-admin-portal/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('secret-admin-portal/logout/', views.admin_logout_view, name='admin_logout'),
    path('secret-admin-portal/export-csv/', views.export_csv, name='export_csv'),
]