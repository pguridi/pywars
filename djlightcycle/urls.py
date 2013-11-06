from django.conf.urls import patterns, include, url

from registration.backends.default.views import RegistrationView
from registration.forms import RegistrationFormUniqueEmail

class RegistrationViewUniqueEmail(RegistrationView):
    form_class = RegistrationFormUniqueEmail

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^accounts/register$', RegistrationViewUniqueEmail.as_view(), name='registration_register'),
    url(r'^$', 'tournament.views.index', name='index'),
    url(r'^(?P<match_id>\d+)$', 'tournament.views.index', name='view_match'),
    url(r'^scoreboard$', 'tournament.views.scoreboard', name='scoreboard'),
    url(r'^mybots$', 'tournament.views.mybots', name='mybots'),
    url(r'^about$', 'tournament.views.about', name='about'),
    url(r'^save_buffer$', 'tournament.views.save_buffer', name='save_buffer'),
    url(r'^publish_bot$', 'tournament.views.publish_bot', name='publish_bot'),
    url(r'^challenge$', 'tournament.views.challenge', name='challenge'),
    #url(r'^update_bot', 'tournament.views.update_bot', name='upload'),
    url(r'^main-match$', 'tournament.views.main_match', name='main_match'),
    url(r'^my-matches$', 'tournament.views.my_matches', name='my_matches'),
    url(r'^test-match$', 'tournament.views.random_test_match', name='test_match'),
    url(r'^get-match/(\d+)$', 'tournament.views.get_match', name='get_match'),
    url(r'^bot_code/(\d+)$', 'tournament.views.bot_code', name='bot_code'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^pOZmwsMZmuGfYS11/', include(admin.site.urls)),
    (r'^accounts/', include('registration.backends.default.urls')),
)
