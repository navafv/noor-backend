from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import FeesReceipt, Expense
from .serializers import FeesReceiptSerializer, ExpenseSerializer
from api.permissions import IsAdmin, IsStudent
from django.http import HttpResponse
from .utils import generate_receipt_pdf
from django.shortcuts import get_object_or_404
import logging

logger = logging.getLogger(__name__)

class FeesReceiptViewSet(viewsets.ModelViewSet):
    queryset = FeesReceipt.objects.select_related("student__user", "course").all()
    serializer_class = FeesReceiptSerializer
    filterset_fields = ["student", "course", "date", "mode"]
    search_fields = ["receipt_no", "student__user__first_name", "student__reg_no"]
    ordering_fields = ["date", "amount"]

    def get_permissions(self):
        if self.action == 'download_public':
             return [AllowAny()]
        if self.action in ['list', 'retrieve', 'download_pdf']:
            return [(IsAdmin | IsStudent)()] 
        return [IsAdmin()]

    def get_queryset(self):
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
        try:
            pdf_content = generate_receipt_pdf(receipt)
            if not pdf_content:
                raise ValueError("PDF Generation returned empty bytes")
        except Exception as e:
            logger.error(f"PDF Generation Error (Receipt {receipt.receipt_no}): {e}", exc_info=True)
            return Response(
                {"success": False, "message": "Unable to generate PDF receipt."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Receipt_{receipt.receipt_no}.pdf"'
        return response
        
    @action(detail=False, methods=['get'], url_path='public/(?P<public_id>[^/.]+)')
    def download_public(self, request, public_id=None):
        receipt = get_object_or_404(FeesReceipt, public_id=public_id)
        
        try:
            pdf_content = generate_receipt_pdf(receipt)
            if not pdf_content:
                 raise ValueError("PDF Generation returned empty bytes")
        except Exception as e:
            logger.error(f"Public PDF Generation Error (Receipt {receipt.receipt_no}): {e}", exc_info=True)
            return Response(
                {"success": False, "message": "Unable to generate PDF receipt."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Receipt_{receipt.receipt_no}.pdf"'
        return response


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ["category", "date"]
    search_fields = ["title", "description"]
    ordering_fields = ["date", "amount"]