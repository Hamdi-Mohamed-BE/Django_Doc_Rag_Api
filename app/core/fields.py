from rest_framework.fields import ListField
from rest_framework import serializers


class ManyToManyFormDataField(ListField):
    """
    List-like serializer field for many-to-many relations. Used for swagger compatibility. Is represented in Swagger as
    a list of strings. Hides original field in serializer. Example:

    class StoneModel(...):
        found_by = ManyToManyField(User)

    class StoneSerializer(...):
        found_by = ManyToManyFormDataField()

        class Meta:
            fields= ['found_by', ]
    """

    def to_representation(self, value):
        return [v.pk for v in value.all()]

    def to_internal_value(self, data):
        if isinstance(data, list):
            data = data[0]
        data = data.split(",")  # convert string to list
        return super().to_internal_value(data)


class StringArrayField(ListField):
    """
    List-like serializer field. Used for swagger compatibility. Is represented in Swagger as a list of strings. Hides
    original field in serializer. Example:

    class StoneModel(...):
        found_by = ArrayField(models.CharField(...))

    class StoneSerializer(...):
        found_by = StringArrayField()

        class Meta:
            fields= ['found_by', ]
    """

    def to_internal_value(self, data):
        if isinstance(data, list):
            data = data[0]
        data = data.split(",")  # convert string to list
        return super().to_internal_value(data)


class ReadWriteSerializerMethodField(serializers.SerializerMethodField):
    """
    Writable method field for serializer. Used for swagger compatibility. Is represented by Swagger as string field.
    When used in serializer needs get_{field_name} method implementation. E. g.

    class SomeSerializer(...):
        some_field = ReadWriteSerializerMethodField()

        def get_some_field(self, instance):
            {apply your logic here}
    """

    def __init__(self, method_name=None, **kwargs):
        self.method_name = method_name
        kwargs["source"] = "*"
        super(serializers.SerializerMethodField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        return {self.field_name: data}
