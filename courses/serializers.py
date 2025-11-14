"""
Courses Serializers
-------------------
Enhancements:
- Added validation and nested display fields.
- Added atomic enrollment creation with capacity checks.
- Added 'has_feedback' field to EnrollmentSerializer.
- NEW: Added CourseMaterialSerializer.
"""

from django.db import transaction
from rest_framework import serializers
from .models import Course, Trainer, Batch, Enrollment, BatchFeedback, CourseMaterial


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model."""
    class Meta:
        model = Course
        fields = [
            "id", "code", "title", "duration_weeks", "total_fees", 
            "syllabus", "active", "required_attendance_days"
        ]


class TrainerSerializer(serializers.ModelSerializer):
    """Serializer for Trainer model."""
    trainer_name = serializers.ReadOnlyField(source="user.get_full_name")

    class Meta:
        model = Trainer
        fields = ["id", "user", "trainer_name", "emp_no", "join_date", "salary", "is_active"]


class BatchSerializer(serializers.ModelSerializer):
    """Serializer for Batch model."""
    course_title = serializers.ReadOnlyField(source="course.title")
    trainer_name = serializers.ReadOnlyField(source="trainer.user.get_full_name")

    class Meta:
        model = Batch
        fields = [
            "id", "course", "course_title", "trainer", "trainer_name",
            "code", "capacity", "schedule",
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for Enrollment model with validation."""
    student_name = serializers.ReadOnlyField(source="student.user.get_full_name")
    batch_code = serializers.ReadOnlyField(source="batch.code")
    course_title = serializers.ReadOnlyField(source="batch.course.title")
    has_feedback = serializers.SerializerMethodField()
    course_id = serializers.ReadOnlyField(source="batch.course.id") 
    completion_date = serializers.DateField(read_only=True)
    present_days = serializers.SerializerMethodField()
    required_days = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = [
            "id", "student", "student_name", "batch", "batch_code", 
            "enrolled_on", "status", "course_title", "has_feedback",
            "course_id", "completion_date",
            "present_days", "required_days"
        ]
        read_only_fields = ["id", "enrolled_on"]
    
    def get_present_days(self, obj):
        return obj.get_present_days_count()

    def get_required_days(self, obj):
        return obj.batch.course.required_attendance_days

    def get_has_feedback(self, obj):
        # Check if the one-to-one reverse relation exists
        return hasattr(obj, 'feedback')

    @transaction.atomic
    def create(self, validated_data):
        """Prevent enrolling student into full or duplicate batch."""
        batch = validated_data["batch"]
        student = validated_data["student"]

        # Capacity check
        if batch.is_full():
            raise serializers.ValidationError("Batch capacity reached.")

        # Duplicate check
        if Enrollment.objects.filter(student=student, batch=batch).exists():
            raise serializers.ValidationError("Student already enrolled in this batch.")

        return super().create(validated_data)


class BatchFeedbackSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source="enrollment.student.user.get_full_name")
    batch_code = serializers.ReadOnlyField(source="enrollment.batch.code")

    class Meta:
        model = BatchFeedback
        fields = [
            "id", "enrollment", "student_name", "batch_code", 
            "rating", "comments", "submitted_at"
        ]
        read_only_fields = ["id", "submitted_at"]

    def validate_enrollment(self, enrollment):
        """
        Check if the feedback is from the currently logged-in user.
        """
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")
        
        if enrollment.student.user != request.user:
            raise serializers.ValidationError("You can only submit feedback for your own enrollments.")
        
        if enrollment.status != "completed":
            # Optional: only allow feedback on completed courses
            raise serializers.ValidationError("Feedback can only be submitted for completed batches.")
            
        if BatchFeedback.objects.filter(enrollment=enrollment).exists():
            raise serializers.ValidationError("Feedback has already been submitted for this enrollment.")
            
        return enrollment


# --- UPDATED SERIALIZER ---
class CourseMaterialSerializer(serializers.ModelSerializer):
    """
    Serializer for uploading and viewing course materials.
    """
    course_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = CourseMaterial
        # --- FIX: Removed 'course' from this list ---
        fields = [
            "id", "course_title", "title", "description",
            "file", "link", "uploaded_at"
        ]
        read_only_fields = ["id", "uploaded_at", "course_title"]
        # --- END FIX ---

    def validate(self, attrs):
        # Ensure either file or link is provided
        file = attrs.get("file")
        link = attrs.get("link")
        
        # On create
        if not self.instance:
            if not file and not link:
                raise serializers.ValidationError("Must provide either a file or a link.")
            if file and link:
                raise serializers.ValidationError("Cannot provide both a file and a link.")
        
        # On update (patch)
        if self.instance:
            if file and (link or self.instance.link):
                raise serializers.ValidationError("Cannot provide both a file and a link.")
            if link and (file or self.instance.file):
                raise serializers.ValidationError("Cannot provide both a file and a link.")

        return attrs

    def create(self, validated_data):
        # 'course' will be provided from the nested URL, not the request body
        validated_data['course_id'] = self.context['view'].kwargs['course_pk']
        return super().create(validated_data)