from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
# --- 1. IMPORT IsAuthenticated ---
from rest_framework.permissions import AllowAny, IsAuthenticated 
from api.permissions import IsStaffOrReadOnly, IsAdmin, IsStudent
# --- END IMPORT ---
from .models import Certificate
from .serializers import CertificateSerializer
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404


class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.select_related("student__user", "course")
    serializer_class = CertificateSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ["revoked", "course", "student", "issue_date"]
    search_fields = ["certificate_no", "student__user__username", "student__reg_no"]
    ordering_fields = ["issue_date", "certificate_no"]

    @action(detail=False, methods=["get"], permission_classes=[AllowAny], url_path="verify/(?P<qr_hash>[^/.]+)")
    def verify_certificate(self, request, qr_hash=None):
        cert = Certificate.objects.filter(qr_hash=qr_hash, revoked=False).select_related("student__user", "course").first()
        if not cert:
            return Response({"valid": False, "message": "Certificate not found or revoked."}, status=status.HTTP_404_NOT_FOUND)
        data = {
            "valid": True,
            "certificate_no": cert.certificate_no,
            "student": cert.student.user.get_full_name(),
            "course": cert.course.title if cert.course else None,
            "issue_date": cert.issue_date,
            "remarks": cert.remarks,
        }
        return Response(data)


    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def revoke(self, request, pk=None):
        cert = self.get_object()
        new_status = not cert.revoked
        cert.revoked = new_status
        cert.save(update_fields=["revoked"])
        status_text = "revoked" if new_status else "un-revoked"
        return Response({"detail": f"Certificate has been {status_text}."})

    # --- 2. This action now has its permission imported ---
    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated]) 
    def download(self, request, pk=None):
        """
        Securely downloads the certificate PDF.
        Accessible by Admins OR the student who owns it.
        """
        cert = get_object_or_404(Certificate, pk=pk)

        # Permission check
        is_owner = request.user == cert.student.user
        is_admin = request.user.is_staff
        
        if not (is_owner or is_admin):
            return Response({"detail": "Not authorized to download this file."}, status=status.HTTP_403_FORBIDDEN)
            
        if not cert.pdf_file:
            return Response({"detail": "PDF file not found for this certificate."}, status=status.HTTP_404_NOT_FOUND)

        try:
            return FileResponse(cert.pdf_file.open('rb'), as_attachment=True, filename=cert.pdf_file.name.split('/')[-1])
        except FileNotFoundError:
            return Response({"detail": "File not found on server."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"Error accessing file: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StudentCertificateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CertificateSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        try:
            student_id = self.request.user.student.id
            return Certificate.objects.filter(
                student_id=student_id,
                revoked=False
            ).select_related(
                "student__user", "course"
            ).order_by("-issue_date")
        except Exception:
            return Certificate.objects.none()