from django.shortcuts import render
from django.views.generic import TemplateView

import datetime
from decimal import Decimal, ROUND_HALF_UP
import requests
import json


API_BASE_URL = 'http://api.openweathermap.org/data/2.5/'
API_KEY = ''
WEATHER_STATUS_DICT = {'Clear': '晴れ', 'Clouds': '曇り', 'Rain': '雨', 'Snow': '雪'}
ICON_DICT = {'Clear': 'sun-o', 'Clouds': 'cloud', 'Rain': 'umbrella', 'Snow': 'snowflake-o'}


class IndexView(TemplateView):
    template_name = 'weather/index.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = {'results': False}
        search_val = request.POST.get('search', None)
        if search_val is None:
            context['msg'] = 'Type city name.'
            return self.render_to_response(context)

        current_weather_url = API_BASE_URL + "weather/?units=metric&lang=ja&q=" + search_val + "&APPID=" + API_KEY
        forecast_weather_url = API_BASE_URL + "forecast/?units=metric&lang=ja&q=" + search_val + "&APPID=" + API_KEY
        current_weather_res = requests.get(current_weather_url)
        current_weather_json_res = json.loads(current_weather_res.text)

        if current_weather_json_res.get('cod') != 200:
            context['msg'] = 'Something happened. Please retry.'
            return self.render_to_response(context)
        else:
            context['results'] = True
            context['city_name'] = search_val
            context['icon'] = ICON_DICT[current_weather_json_res.get('weather', [])[0].get('main', '')]
            context['weather'] = WEATHER_STATUS_DICT[current_weather_json_res.get('weather', [])[0].get('main', '')]
            context['weather_desc'] = current_weather_json_res.get('weather', [])[0].get('description', '')
            context['temperature'] = Decimal(
                str(current_weather_json_res.get('main', '').get(
                    'temp', ''))).quantize(Decimal('0'), rounding=ROUND_HALF_UP)

        forecast_weather_res = requests.get(forecast_weather_url)
        forecast_weather_json_res = json.loads(forecast_weather_res.text)

        if forecast_weather_json_res.get('cod') != '200':
            context['msg'] = 'Something happened. Please retry.'
            return self.render_to_response(context)
        else:
            context['results'] = True
            context['forecast_lists'] = []
            for data in forecast_weather_json_res['list']:
                context['forecast_lists'].append({
                    'date': str(
                        datetime.datetime.fromtimestamp(data['dt']) + datetime.timedelta(hours=9)),
                    'icon': ICON_DICT[data.get('weather', [])[0].get('main', '')],
                    'weather': WEATHER_STATUS_DICT[data.get('weather', [])[0].get('main', '')],
                    'weather_desc': data.get('weather', [])[0].get('description', ''),
                    'temperature': Decimal(
                str(data.get('main', '').get('temp', ''))).quantize(Decimal('0'), rounding=ROUND_HALF_UP)
                })

        return self.render_to_response(context)
