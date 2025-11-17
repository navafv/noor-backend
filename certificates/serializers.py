from rest_framework import serializers
from .models import Certificate
from courses.models import Enrollment

class CertificateSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source="student.user.get_full_name")
    course_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = Certificate
        fields = [
            "id", "certificate_no", "student", "student_name",
            "course", "course_title", "issue_date", "qr_hash",
            "remarks", "revoked", "pdf_file"
        ]
        read_only_fields = [
            "certificate_no", "issue_date", "qr_hash", "pdf_file", 
            "student_name", "course_title"
        ]

    def validate(self, attrs):
        student = attrs.get("student")
        course = attrs.get("course")
        
        if not (student and course):
            return attrs

        # 1. Check for existing valid certificate
        existing_cert_query = Certificate.objects.filter(
            student=student, course=course, revoked=False
        )
        if self.instance:
            existing_cert_query = existing_cert_query.exclude(id=self.instance.id)
        
        if existing_cert_query.exists():
            raise serializers.ValidationError(
                "A valid certificate already exists for this student and course."
            )
        
        # 2. Check for Course Completion
        has_completed_enrollment = Enrollment.objects.filter(
            student=student, 
            course=course,
            status="completed"
        ).exists()

        if not has_completed_enrollment:
            active_enrollment = Enrollment.objects.filter(
                student=student, course=course, status="active"
            ).first()
            
            if active_enrollment:
                raise serializers.ValidationError(
                    f"Student has not completed this course yet. "
                    f"Attendance: {active_enrollment.get_present_days_count()}/"
                    f"{course.required_attendance_days} days."
                )
            else:
                 raise serializers.ValidationError(
                    "Student is not enrolled in this course or has dropped it."
                 )

        return attrs