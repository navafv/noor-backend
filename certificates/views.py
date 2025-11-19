from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated 
from api.permissions import IsAdmin, IsStudent
from .models import Certificate
from .serializers import CertificateSerializer
from .utils import generate_certificate_pdf
from django.http import FileResponse
from django.shortcuts import get_object_or_404

class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.select_related("student__user", "course").order_by("-issue_date")
    serializer_class = CertificateSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ["revoked", "course", "student", "issue_date"]
    search_fields = ["certificate_no", "student__user__username", "student__reg_no", "course__title"]
    ordering_fields = ["issue_date", "certificate_no"]

    @action(detail=False, methods=["get"], permission_classes=[AllowAny], url_path="verify/(?P<qr_hash>[^/.]+)")
    def verify_certificate(self, request, qr_hash=None):
        try:
            cert = Certificate.objects.select_related(
                "student__user", "course"
            ).get(qr_hash=qr_hash, revoked=False)
        except Certificate.DoesNotExist:
             return Response({"valid": False, "message": "Certificate not found or has been revoked."}, status=status.HTTP_404_NOT_FOUND)

        data = {
            "valid": True,
            "certificate_no": cert.certificate_no,
            "student_name": cert.student.user.get_full_name(),
            "course_title": cert.course.title if cert.course else "Unknown Course",
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
        return Response({"detail": f"Certificate has been {status_text}.", "revoked": new_status})

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated]) 
    def download(self, request, pk=None):
        cert = get_object_or_404(Certificate, pk=pk)

        is_owner = (request.user.is_authenticated and
                    hasattr(request.user, 'student') and 
                    request.user.student == cert.student)
        is_admin = request.user.is_staff
        
        if not (is_owner or is_admin):
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
            
        # if not cert.pdf_file:
        #     return Response({"detail": "PDF file not found."}, status=status.HTTP_404_NOT_FOUND)

        pdf_content = generate_certificate_pdf(cert)

        if not pdf_content:
             return Response({"detail": "Error generating PDF."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return FileResponse(
            pdf_content, 
            as_attachment=True, 
            filename=f"{cert.certificate_no}.pdf", # Use certificate_no for filename
            content_type='application/pdf'
        )

        # try:
        #     return FileResponse(
        #         cert.pdf_file.open('rb'), 
        #         as_attachment=True, 
        #         filename=cert.pdf_file.name.split('/')[-1]
        #     )
        # except FileNotFoundError:
        #     return Response({"detail": "File not found on server."}, status=status.HTTP_404_NOT_FOUND)


class StudentCertificateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CertificateSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        try:
            student = self.request.user.student
            return Certificate.objects.filter(
                student=student,
                revoked=False
            ).select_related("course").order_by("-issue_date")
        except AttributeError: # If user has no student profile
            return Certificate.objects.none()