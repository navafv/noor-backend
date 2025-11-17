from django.db import transaction
from rest_framework import serializers
from .models import Course, Enrollment, CourseMaterial


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "id", "code", "title", "duration_weeks", "total_fees", 
            "syllabus", "active", "required_attendance_days"
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source="student.user.get_full_name")
    course_title = serializers.ReadOnlyField(source="course.title")
    course_id = serializers.ReadOnlyField(source="course.id")
    completion_date = serializers.DateField(read_only=True)
    
    present_days = serializers.SerializerMethodField()
    required_days = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = [
            "id", "student", "student_name", "course", "course_title",
            "enrolled_on", "status", "course_id", "completion_date",
            "present_days", "required_days"
        ]
        read_only_fields = ["id", "enrolled_on"]
    
    def get_present_days(self, obj):
        return obj.get_present_days_count()

    def get_required_days(self, obj):
        return obj.course.required_attendance_days

    @transaction.atomic
    def create(self, validated_data):
        course = validated_data["course"]
        student = validated_data["student"]

        if Enrollment.objects.filter(student=student, course=course).exists():
            raise serializers.ValidationError("Student already enrolled in this course.")

        return super().create(validated_data)


class CourseMaterialSerializer(serializers.ModelSerializer):
    course_title = serializers.ReadOnlyField(source="course.title")
    course = serializers.ReadOnlyField(source="course.id")

    class Meta:
        model = CourseMaterial
        fields = [
            "id", "course", "course_title", "title", "description",
            "file", "link", "uploaded_at"
        ]
        read_only_fields = ["id", "uploaded_at", "course_title", "course"]

    def validate(self, attrs):
        file = attrs.get("file", getattr(self.instance, 'file', None))
        link = attrs.get("link", getattr(self.instance, 'link', None))
        
        if not file and not link:
            raise serializers.ValidationError("Must provide either a file or a link.")
        if file and link:
            raise serializers.ValidationError("Cannot provide both a file and a link.")

        return attrs

    def create(self, validated_data):
        course_pk = self.context['view'].kwargs.get('course_pk')
        if not course_pk:
            raise serializers.ValidationError("Course ID not found in URL context.")
            
        validated_data['course_id'] = course_pk
        return super().create(validated_data)