from django.urls import path

from documents import views as document_views

app_name = "documents"

urlpatterns = [
    path("upload/", document_views.DocumentUploadView.as_view(), name="upload"),
    path("my-documents/", document_views.MyDocumentsView.as_view(), name="my_documents"),

    path("ask/<uuid:document_uid>/", document_views.TestVectorView.as_view(), name="test_vector"),
]
