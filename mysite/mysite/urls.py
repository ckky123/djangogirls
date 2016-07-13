from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('cts.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('cts.urls')),
)
