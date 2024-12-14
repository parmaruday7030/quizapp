from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .models import *
import random

def home(request):
    context = {'categories': Category.objects.all()}
    if request.GET.get('category'):
        return redirect(f"/quiz/?category={request.GET.get('category')}")
    return render(request, 'home.html', context)

def quiz(request):
    context = {'category': request.GET.get('category')}
    return render(request, 'quiz.html', context)

def get_quiz(request):
    try:
        question_objs = Question.objects.all()
        if request.GET.get('category'):
            question_objs = question_objs.filter(category__category_name__icontains=request.GET.get('category'))
        question_objs = list(question_objs)
        random.shuffle(question_objs)
        data = []
        for question_obj in question_objs:
            data.append({
                "uid": question_obj.uid,
                "category": question_obj.category.category_name,
                "question": question_obj.question,
                "marks": question_obj.marks,
                "answers": question_obj.get_answers()
            })
        payload = {
            'status': True,
            'data': data
        }
        return JsonResponse(payload)
    except Exception as e:
        print(e)
        return HttpResponse("Something Went Wrong")

def submit_answer(request):
    try:
        question_uid = request.POST.get('question_uid')
        selected_answer = request.POST.get('selected_answer')
        session_id = request.POST.get('session_id')

        print(f"Received question_uid: {question_uid}, selected_answer: {selected_answer}, session_id: {session_id}")

        question = Question.objects.get(uid=question_uid)
        correct_answer = Answer.objects.filter(question=question, is_correct=True).first()

        score_obj, created = Score.objects.get_or_create(session_id=session_id)

        if selected_answer == correct_answer.answer:
            score_obj.correct_answers += 1
            score_obj.total_score += question.marks
            message = "Correct Answer!"
        else:
            score_obj.incorrect_answers += 1
            message = "Incorrect Answer."

        score_obj.save()

        payload = {
            'status': True,
            'message': message,
            'correct_answers': score_obj.correct_answers,
            'incorrect_answers': score_obj.incorrect_answers,
            'total_score': score_obj.total_score
        }
        return JsonResponse(payload)
    except Question.DoesNotExist:
        print(f"Question with UID {question_uid} does not exist.")
        return JsonResponse({'status': False, 'message': 'Question not found.'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': False, 'message': 'Something Went Wrong'})

    
def submit_quiz(request):
    if request.method == 'POST':
        try:
            # Get data from the POST request
            data = json.loads(request.body)
            session_id = data.get('session_id')
            answers = data.get('answers')  # answers will be a dictionary with question UID as key

            total_score = 0
            correct_answers = []
            incorrect_answers = []

            # Process answers and calculate score
            for question_uid, selected_answer in answers.items():
                question = Question.objects.get(uid=question_uid)
                correct_answer = question.get_correct_answer()  # assuming this method returns the correct answer
                if selected_answer == correct_answer:
                    total_score += question.marks
                    correct_answers.append(question_uid)
                else:
                    incorrect_answers.append(question_uid)

            # Prepare the response payload
            response_data = {
                'status': True,
                'data': {
                    'total_score': total_score,
                    'correct_answers': correct_answers,
                    'incorrect_answers': incorrect_answers
                }
            }
            return JsonResponse(response_data)

        except Exception as e:
            print(str(e))
            return JsonResponse({'status': False, 'message': 'Error processing the quiz submission.'})    

def quiz_summary(request):
    try:
        session_id = request.GET.get('session_id')
        score_obj = Score.objects.get(session_id=session_id)

        context = {
            'correct_answers': score_obj.correct_answers,
            'incorrect_answers': score_obj.incorrect_answers,
            'total_score': score_obj.total_score
        }
        return render(request, 'summary.html', context)
    except Score.DoesNotExist:
        return HttpResponse("Session not found")

