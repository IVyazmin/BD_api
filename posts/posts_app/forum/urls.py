from django.conf.urls import url
from posts_app.forum import views

urlpatterns = [
	url(r'^create$', views.create_forum),
	url(r'^(?P<forum_slug>.*)/create$', views.create_thread),
	url(r'^(?P<forum_slug>.*)/details$', views.details),
	url(r'^(?P<forum_slug>.*)/threads$', views.threads),
	url(r'^(?P<forum_slug>.*)/users$', views.users),
]
