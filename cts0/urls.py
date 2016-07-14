from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',

    url(r'^$', views.index),
    url(r'^add/(\d+)/(\d+)/$', views.add, name='add'),
    url(r'^QueryOneWeek/$', views.QueryOneWeek, name='QueryOneWeek'),
    
)