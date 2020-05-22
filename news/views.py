from collections import defaultdict
from datetime import datetime as dt
import json
import random

from django.conf import settings
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views import View


def get_news():
    with open(settings.NEWS_JSON_PATH, 'r') as file:
        news = json.load(file)
    return news


class InfoView(View):
    def get(self, request):
        # return HttpResponse('<h1>Coming soon</h1>')
        return redirect('/news/')


class NewsView(View):
    template_name = 'news.html'

    def format_topic(self, news):
        topics = defaultdict(list)
        for topic in news:
            created = dt.strptime(topic['created'], '%Y-%m-%d %H:%M:%S')
            created_date = dt.strptime(topic['created'][:10], '%Y-%m-%d')
            shortcut = {'created': created,
                        'link': topic['link'],
                        'title': topic['title']}
            topics[created_date].append(shortcut)
        return dict(topics)

    def get(self, request, **kwargs):
        news = get_news()
        context = {}
        if 'link' in kwargs:
            link = kwargs['link']
            for topic in news:
                if topic['link'] == link:
                    context['topic'] = topic
                    break
        else:
            if 'q' in request.GET:
                print(request.GET['q'])
                find_str = request.GET['q'].lower()
                find_topics = []
                for topic in news:
                    if topic['text'].lower().find(find_str) > -1:
                        find_topics.append(topic)
                if find_topics:
                    context['news'] = self.format_topic(find_topics)
            else:
                context['news'] = self.format_topic(news)
        return render(request, self.template_name, context=context)

    def post(self, request):
        context = {}
        if request.POST['q']:
            news = get_news()
            find_topics = []
            for topic in news:
                if topic['text'].lower().find(request.POST['q'].lower()) > 0:
                    find_topics.append(topic)
            if find_topics:
                context['news'] = self.format_topic(find_topics)
        return render(request, self.template_name, context)



class CreateView(View):
    template_name = 'create.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        news = get_news()
        created = dt.strftime(dt.now(), '%Y-%m-%d %H:%M:%S')
        link = int(str(random.random()).split('.')[1])
        topic = {'created': created,
                 'text': request.POST['text'],
                 'title': request.POST['title'],
                 'link': link}
        news.append(topic)
        with open(settings.NEWS_JSON_PATH, 'w') as file:
            json.dump(news, file)
        return redirect('/news/')
