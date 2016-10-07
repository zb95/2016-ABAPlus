from django.conf.urls import url

from . import views

app_name = 'aba_plus_django'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^results$', views.ResultsView.as_view(), name='results'),
]