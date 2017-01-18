from .models import Activity, Person, Relation, Location
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render_to_response, render, redirect
from django.template import loader
from django.contrib.gis.geos import Point, WKTWriter, MultiPolygon
from itertools import chain
from vectorformats.Formats import Django, GeoJSON
from geojson import Feature, FeatureCollection
from shapely.geometry import mapping, shape
import dateutil.parser
import datetime
import geojson
import json
import collections

@csrf_exempt
def map_view(request):
    person_hash = request.GET.get('person_hash')
    person = Person.objects.get(hash=person_hash)
    
    feature_points = collections.OrderedDict()
    feature_fences = collections.OrderedDict()
    wkt_w = WKTWriter()

    activity = 1
    # get activity details from 'Location' activities for this person
    loc_activities = Activity.objects.filter(person=person,category="Location").order_by('time')
    loc_list = list(loc_activities)
    locs_added = set()
    j = 0
    journeys = [[]] # build list of lists of separate journeys to then add to ordered dict of features for template to draw
    for l in loc_list:
        # if hit a known location add location not point
        if l.location:
            if str(l.location.name) not in locs_added:
                wkt_fence = wkt_w.write(l.location.fence)
                journeys[j].append({
                    'name':str(l.location.name), 
                    'feature': wkt_fence,
                    'time': str(l.time),
                    'address': str(l.location.address), 
                    'description': str(l.location.description), 
                    'person': str(l.person.name)})
                locs_added.add(str(l.location.name))
            j += 1
            journeys.append([]) # hit a known location so start next journey list

        else:
            pnt = Point((float(l.locLon), float(l.locLat)), srid=3857)
            wkt_feat = wkt_w.write(pnt)
            #feature_points['Activity - ' + str(activity)] = {
            journeys[j].append({
                'name' : 'Journey - ' + str(j),
                'feature': wkt_feat, 
                'time': str(l.time), 
                'locLat': str(l.locLat), 
                'locLon': str(l.locLon), 
                'category': str(l.category), 
                'person': str(l.person.name)})
    
    for i in range(0,len(journeys)):
        if len(journeys[i]) > 0:
            feature_points["journey "+str(i)] = journeys[i]

    # get additional known locations details for this person
    fences = list(Location.objects.filter(person__hash=person_hash))
    for f in fences:
        wkt_fence = wkt_w.write(f.fence)
        if f.name not in feature_points.keys():
           feature_fences[str(f.name)] = [{
               'name' : str(f.name),
               'feature': wkt_fence, 
               'address': str(f.address), 
               'description': str(f.description), 
               'person': str(f.person.name)}]

    template = loader.get_template('MapView.html')
    # send all the data back
    loc_activities = loc_activities.exclude(location__name=None).order_by('time')
    context = {}
    context['known_locations'] = sorted(feature_fences.iteritems())
    context['title'] = "Activity Map for " + person.name
    context['point_collection'] = sorted(feature_points.iteritems())
    context['selectperson'] = person
    context['location'] = 'all'
    context['time_from'] = 'all'
    context['time_to'] = 'now'
    context['query_result'] = loc_activities
    return JsonResponse(
        {'html': template.render(context, request)}
    )

# watch data from emails is added by callng this method
@csrf_exempt
def add_record_view(request):
    watch_id =  request.POST.get('watch_id', '')[1:] # strip the # sign
    activity_type = request.POST.get('activity_type', '')
    text = request.POST.get('text', '')
    call_duration = request.POST.get('call_duration','')
    to_from = request.POST.get('to_from','')
    person = Person.objects.get(watch_id=watch_id)
    time = dateutil.parser.parse(request.POST.get('time', ''))
    category = request.POST.get('category', '')
    location_name = request.POST.get('location', '')
    locLon = request.POST.get('locLon','')
    locLat = request.POST.get('locLat','')

    # if locLon, locLat intersect with a Location fence then add that to activity too
    if location_name != '':
        location = Location.objects.get(name=location_name)
        Activity.objects.create(time=time, activity_type=activity_type, text=text, person=person,
                                category=category, location=location, call_duration=call_duration,
                                to_from=to_from,locLon=locLon,locLat=locLat)
    else:
        Activity.objects.create(time=time, activity_type=activity_type, text=text, person=person,
                                category=category, call_duration=call_duration,
                                to_from=to_from,locLon=locLon,locLat=locLat)

    return JsonResponse({'message': 'record added! yoohoo!'})

@csrf_exempt
def get_locations(request):
    hash = request.POST['hash']
    person = Person.objects.get(hash=hash)
    loc_activities = Activity.objects.filter(person=person,category="Location")
    loc_list = list(loc_activities)
    str_result = ""
    for loc_act in loc_activities:
    	str_result += "time: " + str(loc_act.time) + ", data: " + loc_act.activity_data 
    return JsonResponse({'result':str_result})

@csrf_exempt
def get_locs_in_time(request):
    hash = request.POST['hash']
    person = Person.objects.get(hash=hash)
    time1 = dateutil.parser.parse(request.POST.get('time1', ''))
    time2 = dateutil.parser.parse(request.POST.get('time2', ''))
    activites = Activity.objects.filter(person=person,time__gte=time1,time__lte=time2,category="Location")
    str_result = ""
    for act in activites:
        str_result += str(act.time) + "---" + act.locLon + "," + act.locLat + "---"
    return JsonResponse({'result':str_result})
    
@csrf_exempt
def get_calls_in_time(request):
    hash = request.POST['hash']
    person = Person.objects.get(hash=hash)
    time1 = dateutil.parser.parse(request.POST.get('time1', ''))
    time2 = dateutil.parser.parse(request.POST.get('time2', ''))
    activites = Activity.objects.filter(person=person,time__gte=time1,time__lte=time2,category="Phone-Call")
    str_result = ""
    for act in activites:
        str_result += "time: " + str(act.time) + " type: " + str(act.activity_type) + "to_from: " + str(act.to_from) + " duration: " +  act.call_duration
    return JsonResponse({'result':str_result})

@csrf_exempt
def get_sms_in_time(request):
    hash = request.POST['hash']
    person = Person.objects.get(hash=hash)
    time1 = dateutil.parser.parse(request.POST.get('time1', ''))
    time2 = dateutil.parser.parse(request.POST.get('time2', ''))
    activites = Activity.objects.filter(person=person,time__gte=time1,time__lte=time2,category="Sms")
    str_result = ""
    for act in activites:
        str_result += "time: " + str(act.time) + " type: " + str(act.activity_type) + "to_from: " + str(act.to_from) + " text: " + str(act.text) 
    return JsonResponse({'result':str_result})

@csrf_exempt
def get_all_activities(request):
    hash = request.Post['hash']
    person = Person.objects.get(hash=hash)
    all_activities = Activity.objects.filter(person=person)
    act_list = list(all_activities)
    str_result = ""
    for act in all_activities:
        str_result += "time: " + str(act.time) + " category: " + act.category \
        + " location: " + str(act.location) + " type: " + str(act.activity_type) \
        + " text: " + str(act.text) 
    return JsonResponse({'result':str_result})

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
    person_hash = request.GET.get('person_hash')
    result1 = Relation.objects.filter(person_1__hash=person_hash).all()
    result2 = Relation.objects.filter(person_2__hash=person_hash).all()
    result = list(chain(result1, result2))

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

        context['query_result'] = result
        context['time_from'] = from_time
        context['time_to'] = to_time

    return HttpResponse(template.render(context, request))
