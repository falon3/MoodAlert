from django.contrib import admin
from .models import Activity, Person, Relation, Location
# Register your models here.


class LocationAdmin(admin.ModelAdmin):
    model = Location


class PersonAdmin(admin.ModelAdmin):
    model = Person


class RelationAdmin(admin.ModelAdmin):
    model = Relation


class ActivityAdmin(admin.ModelAdmin):
    model = Activity


admin.site.register(Location, LocationAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Relation, RelationAdmin)
admin.site.register(Activity, ActivityAdmin)
