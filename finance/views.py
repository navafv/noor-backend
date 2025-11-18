from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import FeesReceipt, Expense
from .serializers import FeesReceiptSerializer, ExpenseSerializer
from api.permissions import IsAdmin, IsStudent
from django.http import FileResponse
from .utils import generate_receipt_pdf
from django.shortcuts import get_object_or_404

class FeesReceiptViewSet(viewsets.ModelViewSet):
    queryset = FeesReceipt.objects.select_related("student__user", "course").all()
    serializer_class = FeesReceiptSerializer
    filterset_fields = ["student", "course", "date", "mode"]
    search_fields = ["receipt_no", "student__user__first_name", "student__reg_no"]
    ordering_fields = ["date", "amount"]

    def get_permissions(self):
        # Allow public access to the specific download endpoint
        if self.action == 'download_public':
             return [AllowAny()]
        if self.action in ['list', 'retrieve', 'download_pdf']:
            return [(IsAdmin | IsStudent)()] 
        return [IsAdmin()]

    def get_queryset(self):
        # For public download, we bypass the standard queryset filtering
        if self.action == 'download_public':
            return FeesReceipt.objects.all()
        
        user = self.request.user
        if user.is_staff:
            return super().get_queryset()
        if hasattr(user, 'student'):
            return super().get_queryset().filter(student=user.student)
        return FeesReceipt.objects.none()

    @action(detail=True, methods=['get'], url_path='download')
    def download_pdf(self, request, pk=None):
        receipt = self.get_object()
        
        # Generate PDF if it doesn't exist
        if not receipt.pdf_file:
            pdf_content = generate_receipt_pdf(receipt)
            if pdf_content:
                from django.core.files.base import ContentFile
                filename = f"Receipt_{receipt.receipt_no}.pdf"
                receipt.pdf_file.save(filename, ContentFile(pdf_content), save=True)
            else:
                return Response({"detail": "Error generating PDF."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            return FileResponse(
                receipt.pdf_file.open('rb'), 
                as_attachment=True, 
                filename=f"Receipt_{receipt.receipt_no}.pdf"
            )
        except FileNotFoundError:
            return Response({"detail": "PDF file not found."}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=False, methods=['get'], url_path='public/(?P<public_id>[^/.]+)')
    def download_public(self, request, public_id=None):
        """
        Public endpoint to download receipt using UUID. No login required.
        """
        receipt = get_object_or_404(FeesReceipt, public_id=public_id)
        
        # Generate PDF if missing
        if not receipt.pdf_file:
            pdf_content = generate_receipt_pdf(receipt)
            if pdf_content:
                from django.core.files.base import ContentFile
                filename = f"Receipt_{receipt.receipt_no}.pdf"
                receipt.pdf_file.save(filename, ContentFile(pdf_content), save=True)
            else:
                return Response({"detail": "Error generating PDF."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            return FileResponse(
                receipt.pdf_file.open('rb'), 
                as_attachment=True, 
                filename=f"Receipt_{receipt.receipt_no}.pdf"
            )
        except FileNotFoundError:
            return Response({"detail": "PDF file not found."}, status=status.HTTP_404_NOT_FOUND)


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ["category", "date"]
    search_fields = ["title", "description"]
    ordering_fields = ["date", "amount"]