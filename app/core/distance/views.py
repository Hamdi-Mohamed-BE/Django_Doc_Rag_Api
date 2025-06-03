from rest_framework.serializers import ValidationError
from django.utils.translation import gettext_lazy as _

from django.contrib.gis.geos import Point
from django.contrib.gis.db import models
from django.contrib.gis.measure import Distance
import settings


class Query:
    """
    A utility class for geographic queries, providing methods to order and filter querysets by distance 
    from a given geographical point.

    Methods
    -------
    order_by_distance(queryset, longitude, latitude, model_field="location")
        Orders a queryset by the distance to a specified geographical point.
        
    filter_by_distance(queryset, *, longitude, latitude, border=settings.DEFAULT_DISTANCE_BORDER, model_field="location")
        Filters a queryset to include only objects within a certain distance from a specified geographical point.
    """

    @staticmethod
    def order_by_distance(queryset, longitude, latitude, model_field="location"):
        """
        Orders a queryset by the distance from a given geographical point.

        Parameters
        ----------
        queryset : QuerySet
            The queryset to be ordered.
        longitude : float
            The longitude of the reference point.
        latitude : float
            The latitude of the reference point.
        model_field : str, optional
            The field in the model representing the geographical location, 
            by default "location".

        Returns
        -------
        QuerySet
            The queryset ordered by distance from the reference point.
        """
        ref_location = Point(x=longitude, y=latitude, srid=4326)
        queryset = queryset.annotate(
            distance_to=models.functions.Distance(model_field, ref_location)
        ).order_by("distance_to")
        return queryset


    @staticmethod
    def filter_by_distance(
        queryset,
        *,
        longitude,
        latitude,
        border=settings.DEFAULT_DISTANCE_BORDER,
        model_field="current_location",
    ):
        """
        Filters a queryset to include only objects within a specified distance 
        from a given geographical point.

        Parameters
        ----------
        queryset : QuerySet
            The queryset to be filtered.
        longitude : float
            The longitude of the reference point.
        latitude : float
            The latitude of the reference point.
        border : float, optional
            The maximum distance (in meters) from the reference point to include 
            objects in the queryset. Defaults to `settings.DEFAULT_DISTANCE_BORDER`.
        model_field : str, optional
            The field in the model representing the geographical location, 
            by default "location".

        Returns
        -------
        QuerySet
            The queryset filtered by the specified distance from the reference point.
        """
        ref_location = Point(x=longitude, y=latitude, srid=4326)
        distance = Distance(m=border)

        kwargs = {}

        if border:
            kwargs.update({
                f"{model_field}__distance_lte": (ref_location, distance)
            })

        queryset = queryset.filter(models.Q(**kwargs))
        return queryset



class DistanceView:
    """
    A view utility providing functionality to filter querysets based on 
    geographical distance using query parameters for longitude and latitude.

    Methods
    -------
    resolve_geolocation_filter(queryset)
        Filters the given queryset based on geolocation query parameters.
    """

    @staticmethod
    def resolve_geolocation_filter(
        queryset,
        longitude=None,
        latitude=None,
        model_field="current_location",
    ):
        """
        Filters a queryset based on longitude and latitude query parameters.

        This method filters the queryset based on the longitude and latitude provided
        in the query parameters. If no longitude and latitude are provided, the queryset
        is returned unchanged.

        Parameters
        ----------
        queryset : QuerySet
            The queryset to be filtered.

        Returns
        -------
        QuerySet
            The filtered queryset based on the longitude and latitude provided 
            in the query parameters.

        Raises
        ------
        ValidationError
            If the longitude or latitude provided are invalid or cannot be converted to float.
        """
        
        # If no longitude and latitude are provided, return the queryset unchanged.
        if longitude is None and latitude is None:
            return queryset

        try:
            # Validate and convert longitude and latitude to float.
            longitude = float(longitude)
            latitude = float(latitude)
        except Exception:
            raise ValidationError(detail=_("Invalid longitude or latitude"))

        # Filter the queryset based on the given geographical point.
        queryset = Query.filter_by_distance(
            queryset,
            longitude=longitude,
            latitude=latitude,
            model_field=model_field,
        )
        return queryset
