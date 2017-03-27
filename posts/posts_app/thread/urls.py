from django.conf.urls import url
from posts_app.thread import views

urlpatterns = [
	url(r'^(?P<thread_slug>.*)/create$', views.create),
	url(r'^(?P<thread_slug>.*)/details$', views.details),
	url(r'^(?P<thread_slug>.*)/posts$', views.slug_posts),
	url(r'^(?P<thread_slug>.*)/vote$', views.vote),
]