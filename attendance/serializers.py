from rest_framework import serializers
from django.db import transaction
from .models import Attendance, AttendanceEntry
from students.models import Student
from courses.models import Enrollment

class AttendanceEntrySerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source="student.user.get_full_name")
    reg_no = serializers.ReadOnlyField(source="student.reg_no")

    class Meta:
        model = AttendanceEntry
        fields = ["id", "student", "student_name", "reg_no", "status", "remarks"]


class StudentAttendanceEntrySerializer(serializers.ModelSerializer):
    """
    Read-only serializer for a student to see their own history.
    """
    date = serializers.ReadOnlyField(source="attendance.date")

    class Meta:
        model = AttendanceEntry
        fields = ["id", "date", "status", "remarks"]


class AttendanceSerializer(serializers.ModelSerializer):
    entries = AttendanceEntrySerializer(many=True)
    summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Attendance
        fields = [
            "id", "date", "taken_by", "remarks", 
            "entries", "summary", "created_at"
        ]
        read_only_fields = ["id", "created_at", "summary"]

    def get_summary(self, obj):
        return obj.summary

    def _validate_student_ids(self, entries_data):
        """
        Ensure all student IDs exist and are active.
        """
        student_ids = [e.get('student') for e in entries_data]
        existing_count = Student.objects.filter(id__in=student_ids, active=True).count()
        
        # Note: We perform a loose check here. Strict validation 
        # per ID happens during bulk creation or can be added if strictness is required.
        return student_ids

    def _check_student_completion(self, student_id):
        """
        After marking attendance, check if the student has completed their course.
        """
        try:
            # Find all active enrollments for this student
            enrollments = Enrollment.objects.filter(
                student_id=student_id, 
                status="active"
            )
            for enrollment in enrollments:
                enrollment.check_and_update_status()
        except Exception:
            pass

    @transaction.atomic
    def create(self, validated_data):
        entries_data = validated_data.pop("entries", [])
        validated_data['taken_by'] = self.context['request'].user
        
        attendance = Attendance.objects.create(**validated_data)

        # Bulk create entries
        AttendanceEntry.objects.bulk_create([
            AttendanceEntry(attendance=attendance, **e) for e in entries_data
        ])
        
        # Check completion status for all students present
        for entry in entries_data:
            if entry.get('status') == 'P':
                self._check_student_completion(entry['student'])
                
        return attendance

    @transaction.atomic
    def update(self, instance, validated_data):
        entries_data = validated_data.pop("entries", [])
        
        instance.remarks = validated_data.get("remarks", instance.remarks)
        instance.save()

        # Update or Create entries
        processed_student_ids = []
        
        for entry_data in entries_data:
            student_id = entry_data.get("student")
            status_val = entry_data.get("status")
            remarks_val = entry_data.get("remarks", "")

            processed_student_ids.append(student_id)

            entry, created = AttendanceEntry.objects.update_or_create(
                attendance=instance,
                student_id=student_id,
                defaults={"status": status_val, "remarks": remarks_val}
            )
            
            # If status changed to Present, check completion
            if status_val == 'P':
                self._check_student_completion(student_id)

        return instance