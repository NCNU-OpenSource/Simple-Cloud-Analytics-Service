from django.urls import path
from . import views
urlpatterns = [
    path('login/',views.login),
    path('logout/',views.logout),
    path('index/',views.index),
    path('tensorflow_test/',views.tensorflow_test),
    path('NeuralNetwork/',views.NeuralNetwork),
    path('kmeans/',views.kmeans),
    path('call_help/',views.call_help),
    path('send_result_back/',views.send_result_back),
    path('worker_check_status/',views.worker_check_status),
]