from django.conf.urls import url
from posts_app.post import views

urlpatterns = [
	url(r'^(?P<post_id>.*)/details$', views.details),
]