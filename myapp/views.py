from django.shortcuts import render
from django.conf import settings
from django.utils import timezone
from .models import Post
import os
import pickle
import numpy as np
import pandas as pd
from sklearn import datasets
from sklearn.ensemble import RandomForestRegressor
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.http import JsonResponse, HttpResponse
import joblib

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'myapp/post_list.html', {'posts': posts})

@require_POST
def predict(request):
    print(request.POST)
    people_rank_text = request.POST.getlist('people_rank_arr[]')
    button_idx_list = []
    for text in people_rank_text:
        button_idx_list.append(int(text[5:]))
    #people_rank = []
    #for text in people_rank_text:
    #    people_rank.append(int(text[5:]))
    answers = request.POST.getlist('anwer_arr[]')
    #print(people_rank)
    mood = request.POST['mood']
    mbti = request.POST['mbti']
    if mbti=="istj":
        mbti_num=0
    elif mbti=="istp":
        mbti_num=1
    elif mbti=="isfj":
        mbti_num=2
    elif mbti=="isfp":
        mbti_num=3
    elif mbti=="intj":
        mbti_num=4
    elif mbti=="intp":
        mbti_num=5
    elif mbti=="infj":
        mbti_num=6
    elif mbti=="infp":
        mbti_num=7
    elif mbti=="estj":
        mbti_num=8
    elif mbti=="estp":
        mbti_num=9
    elif mbti=="esfj":
        mbti_num=10
    elif mbti=="esfp":
        mbti_num=11
    elif mbti=="entj":
        mbti_num=12
    elif mbti=="entp":
        mbti_num=13
    elif mbti=="enfj":
        mbti_num=14
    elif mbti=="enfp":
        mbti_num=15
    age = int(request.POST['age'])
    num_all = int(request.POST['num_all'])
    people_rank = [i+1 for i in range(num_all)]
    print(people_rank)
    people_rank = 1-(np.array(people_rank)/num_all)
    people_rank = list(people_rank)
    path = os.path.join(settings.MODEL_ROOT, "model_big.pkl")
    model = joblib.load(path)
    #age, mood, people_rank, mbti
    x_input = pd.DataFrame({
        "age":[age for i in range(num_all)],
        "mood":[mood for i in range(num_all)],
        "people_rank":people_rank,
        "mbti_num":[mbti_num for i in range(num_all)]
        })
    print(x_input)
    x_input = x_input[["age","mood","people_rank","mbti_num"]]
    print(x_input)
    predict = model.predict(x_input).tolist()
    print(predict)
    predict_set = sorted(predict)
    predict_set.reverse()
    predict_idx = []
    for i in predict_set:
        predict_idx.append(predict_set.index(i)+1)
    print(predict_idx)
    predict_best = button_idx_list[predict_idx.index(1)]
    predict_answer = "alert"+str(predict_best)
    button_idx_list.remove(predict_best)
    predict_wrong = ["alert"+str(i) for i in button_idx_list]
    print(predict_answer)
    print(predict_wrong)
    context={'success':True, 'predict':predict, 'rank':predict_idx, 'best':predict_best, 'none':predict_wrong}
    return HttpResponse(json.dumps(context), content_type="application/json")


        