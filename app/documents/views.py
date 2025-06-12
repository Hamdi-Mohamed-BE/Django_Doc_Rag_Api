from rest_framework import generics
from rest_framework.views import APIView

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, OpenApiTypes

from documents import models as document_models
from documents import serializers as document_serializers

from documents.services.llm_chain import answer_question



class DocumentUploadView(generics.CreateAPIView):
    """
    View for uploading documents.
    """
    serializer_class = document_serializers.DocumentUploadSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        summary="Upload a new document",
        description="Upload a document file. Supports multiple file formats.",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'document_file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'The document file to upload. Must be a valid file format.'
                    },
                    'title': {
                        'type': 'string',
                        'description': 'Title of the document.',
                        'example': 'My Document Title'
                    },
                    'description': {
                        'type': 'string',
                        'description': 'Description of the document.',
                        'example': 'This is a description of my document.'
                    }
                },
                'required': ['document_file']
            }
        },
        responses={
            201: document_serializers.DocumentUploadSerializer,
            400: {'description': 'Bad request - invalid file or missing data'},
            401: {'description': 'Authentication required'},
        },
        examples=[
            OpenApiExample(
                'File Upload Example',
                description='Example of uploading a document',
                value={'document_file': 'example.pdf'},
            ),
        ]
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class MyDocumentsView(generics.ListAPIView):
    """
    View for listing the documents of the authenticated user.
    """
    serializer_class = document_serializers.DocumentDetailSerializer
    permission_classes = [IsAuthenticated]

    
    def get_queryset(self):
        user = self.request.user
        return document_models.Document.objects.filter(user=user).select_related('user').order_by("-created_at")

    @extend_schema(
        summary="List user's documents",
        description="Retrieve all documents uploaded by the authenticated user," \
        "ordered by creation date (newest first).",
        responses={
            200: document_serializers.DocumentDetailSerializer(many=True),
            401: {'description': 'Authentication required'},
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    

class TestVectorView(APIView):
    """
    View for testing vector search functionality.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="query",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="The query string to search for in the vector store.",
                required=True,
                default="ask any question about your documents",
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        document_uid = self.kwargs.get("document_uid")
        try:
            document = document_models.Document.objects.select_related('user').get(uid=document_uid)
        except document_models.Document.DoesNotExist:
            document = None
        
        if not document:
            return Response(
                {"detail": "Document not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        user_input = request.query_params.get("query", "test")
        response = answer_question(
            user_input,
            document
        )
        if not response:
            return Response(
                {"detail": "No answer found."},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {"answer": response},
            status=status.HTTP_200_OK
        )
