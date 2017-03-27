from django.conf.urls import url
from posts_app.user import views

urlpatterns = [
	url(r'^(?P<nickname>.*)/create$', views.create),
	url(r'^(?P<nickname>.*)/profile$', views.profile),
]