from typing import Optional
from django.contrib.gis.geos import Point
import settings 
import googlemaps
import requests
import re
from core.custom_logger import logger

class GeoUtils:
    try:
        gmaps = googlemaps.Client(key=settings.GMAPS_API_KEY)
    except Exception as e:
        logger.error(f"Error initializing Google Maps client: {e}")
        gmaps = None
        
    @staticmethod
    def point_to_coordinates(point: Point) -> tuple:
        """
        From geos.Point to (longitude, latitude).
        """
        if not point:
            return None, None
        return point.x, point.y

    @staticmethod
    def coordinates_to_point(longitude, latitude) -> Optional[Point]:
        """
        From longitude, latitude to Point.
        """
        if not longitude or not latitude:
            return None
        return Point(x=float(longitude), y=float(latitude))

    @staticmethod
    def dict_to_point(data: dict) -> Optional[Point]:
        """
        From dict to Point.
            @param data: dict with keys `x` and `y`.

            @return: Point.
        """
        return GeoUtils.coordinates_to_point(data.get("x"), data.get("y"))

    @staticmethod
    def get_coordinates_from_address(
        address: str,
    ):
        """
        Get latitude and longitude from a Google Maps URL or address.
        
        Args:
            address (str): address.
        
        Returns:
            tuple: (latitude, longitude) or None if not found.
        """
        geocode_result = GeoUtils.gmaps.geocode(address)
        try:
            if geocode_result:
                location = geocode_result[0].get("geometry", {}).get("location", {})
                lng, lat = location.get("lng"), location.get("lat")
                return lng, lat
        except Exception as e:
            print(f"error in get_coordinates_from_url: {e}")
            return None, None
        return None, None

    @staticmethod
    def get_coordinates_from_short_url(
        short_url: str,
    ):
        """
        Get latitude and longitude from a Google Maps URL or address.
        
        Args:
            short_url (str): short URL.
        
        Returns:
            tuple: (latitude, longitude) or None if not found.
        """
        response = requests.get(short_url, allow_redirects=True, timeout=10)
        if response.status_code == 200:
            url = response.url
        else:
            print(f"error in get_coordinates_from_url: {response.status_code}")
            return None, None
        
        if "maps.google.com" in url:
            lat, lng = re.findall(r'@(\d+\.\d+),(\d+\.\d+)', url)[0]
            return lng, lat
        return None, None

    
   