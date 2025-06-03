
from rest_framework import serializers

from documents import models as document_models


class DocumentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = document_models.Document
        fields = (
            "uid",
            "user",
            "title",
            "status",
            "description",
            "document_file",
            "created_at",
            "updated_at",
        )


class DocumentUploadSerializer(serializers.ModelSerializer):
    document_file = serializers.FileField(
        required=True,
        allow_empty_file=False,
        max_length=None,
        allow_null=False,
    )
    class Meta:
        model = document_models.Document
        fields = ("uid", "title", "description", "document_file")
        read_only_fields = ("uid", "created_at", "updated_at")

    def create(self, validated_data):
        user = self.context["request"].user
        document = document_models.Document.objects.create(
            user=user,
            **validated_data
        )
        return document
