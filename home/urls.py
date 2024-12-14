from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('quiz/', views.quiz, name='quiz'),
    path('api/get-quiz/', views.get_quiz, name='get_quiz'),
    path('api/submit-answer/', views.submit_answer, name='submit_answer'),
    path('quiz-summary/', views.quiz_summary, name='quiz_summary'),
]
