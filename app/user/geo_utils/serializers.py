from rest_framework import serializers

class LocationPointDisplaySerializer(serializers.Serializer):
    longitude = serializers.FloatField(source="x")
    latitude = serializers.FloatField(source="y")