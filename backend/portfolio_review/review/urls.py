# Define all the url to the application

from django.urls import path # specify all paths on app
from . import views

# list of url patterns
urlpatterns = [
    # first page user sees is index.html
    path('', views.index, name='index'), # view.index is importing the index ftn from views.py 
    path('submit-url', views.submit_url, name='submit-url'),
    path('feedback', views.feedback, name='feedback')
]