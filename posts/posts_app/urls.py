from django.conf.urls import include, url

urlpatterns = [
	url(r'^forum/', include('posts_app.forum.urls')),
	url(r'^user/', include('posts_app.user.urls')),
	url(r'^post/', include('posts_app.post.urls')),
	url(r'^thread/', include('posts_app.thread.urls')),
	url(r'^service/', include('posts_app.service.urls')),
]