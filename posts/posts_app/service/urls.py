from django.conf.urls import url
from posts_app.service import views

urlpatterns = [
	url(r'^clear$', views.clear),
	url(r'^status$', views.status),
]