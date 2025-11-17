from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import FeesReceipt, Expense
from .serializers import FeesReceiptSerializer, ExpenseSerializer
from api.permissions import IsAdmin, IsStudent
from django.http import FileResponse
from .utils import generate_receipt_pdf

class FeesReceiptViewSet(viewsets.ModelViewSet):
    queryset = FeesReceipt.objects.select_related("student__user", "course").all()
    serializer_class = FeesReceiptSerializer
    filterset_fields = ["student", "course", "date", "mode"]
    search_fields = ["receipt_no", "student__user__first_name", "student__reg_no"]
    ordering_fields = ["date", "amount"]

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'download_pdf']:
            return [IsAdmin() | IsStudent()] 
        return [IsAdmin()]

    def get_queryset(self):
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


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ["category", "date"]
    search_fields = ["title", "description"]
    ordering_fields = ["date", "amount"]