from .models import Activity, Person, Location, Relation, WorldBorder
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import dateutil.parser
from django.http import HttpResponse
from django.shortcuts import render_to_response, render, redirect
from django.template import loader
from itertools import chain
from vectorformats.Formats import Django, GeoJSON
import datetime

# def map_view(request):
#     template = loader.get_template('MapView.html')
#     return HttpResponse(template.render(request))

def map_view(request):
    ly = WorldBorder.objects.filter(name='Canada')
    djf = Django.Django(geodjango='mpoly', properties=['name'])
    geoj = GeoJSON.GeoJSON()
    my_geojson = geoj.encode(djf.decode(ly))
    return render(request, "MapView.html", {'my_geojson': my_geojson})

@csrf_exempt
def add_record_view(request):
    hash = request.POST['hash']
    activity_type = request.POST.get('activity_type', '')
    activity_data = request.POST.get('activity_data', '')
    person = Person.objects.get(hash=hash)
    time = dateutil.parser.parse(request.POST.get('time', ''))
    owner = request.POST.get('owner', '')
    category = request.POST.get('category', '')

    location_name = request.POST.get('location', '')
    if location_name != '':
        location = Location.objects.get(name=location_name)
        Activity.objects.create(time=time, activity_type=activity_type, activity_data=activity_data, person=person,
                                owner=owner, category=category, location=location)
    else:
        Activity.objects.create(time=time, activity_type=activity_type, activity_data=activity_data, person=person,
                                owner=owner, category=category, )

    return JsonResponse({'message': 'record added! yoohoo!'})
    # return render(request,'add_record.html')


def test_get_info(request):
    return JsonResponse({'message': 'Im alive!! Im working :D'})


def show_person_table(request):
    query_result = Person.objects.all()
    template = loader.get_template('persons_table.html')
    context = {
        'query_result': query_result,
    }
    return JsonResponse(
        {'html': template.render(context, request)}
    )


def show_relations_table(request):
    print(request.GET)
    person_hash = request.GET.get('person_hash')
    result1 = Relation.objects.filter(person_1__hash=person_hash).all()
    result2 = Relation.objects.filter(person_2__hash=person_hash).all()
    result = list(chain(result1, result2))
    print('result--')
    print(result)
    template = loader.get_template('relations_table.html')
    context = {
        'query_result': result,
    }
    return JsonResponse(
        {'html': template.render(context, request)}
    )


def show_report_home(request):
    persons = Person.objects.all()
    locations = Location.objects.all()

    template = loader.get_template('report_home.html')
    context = {
        'persons': persons,
        'locations': locations,
    }

    if request.method == "POST":
        person_hash = request.POST.get('person', '')
        result = Activity.objects.all()
        context['selectperson'] = 'all'
        context['location'] = 'all'

        if person_hash != "all":
            result = Activity.objects.filter(person__hash=person_hash).all().order_by('time')
            context['selectperson'] = Person.objects.filter(hash=person_hash).first()

        location = request.POST.get('location', '')
        if location != "all":
            result = result.filter(location__name=location).all().order_by('time')
            context['location'] = location

        if not request.POST.get('time-from'):
            # default get 3 year range
            from_time = datetime.datetime.now() - datetime.timedelta(days=1096)
        else:
            from_time = dateutil.parser.parse(request.POST.get('time-from', ''))

        if not request.POST.get('time-to'):
            to_time = datetime.datetime.now()
        else:
            to_time = dateutil.parser.parse(request.POST.get('time-to', ''))

        result = result.filter(time__gte=from_time, time__lte=to_time).all().order_by('time')

        # result = Activity.objects.filter(person__hash=person_hash, location__name=location,
        #                                  time__gte=from_time, time__lte=to_time).all()

        context['query_result'] = result
        context['time_from'] = from_time
        context['time_to'] = to_time

    return HttpResponse(template.render(context, request))
