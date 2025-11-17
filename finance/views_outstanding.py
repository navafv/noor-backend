from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from api.permissions import IsAdmin
from courses.models import Enrollment
from .models import FeesReceipt
from django.db.models import Sum, F, Case, When, Value, DecimalField

class OutstandingFeesViewSet(viewsets.ViewSet):
    """
    Lists students who have paid less than the course total fee.
    """
    permission_classes = [IsAdmin]

    def list(self, request):
        # 1. Get all active enrollments
        enrollments = Enrollment.objects.filter(status='active').select_related('student', 'course', 'student__user')
        
        outstanding_list = []

        for enrollment in enrollments:
            student = enrollment.student
            course = enrollment.course
            
            # Total fee for the course
            total_fee = course.total_fees
            
            # Total paid by student FOR THIS COURSE
            paid_agg = FeesReceipt.objects.filter(
                student=student, 
                course=course
            ).aggregate(total=Sum('amount'))
            
            paid_amount = paid_agg['total'] or 0
            
            balance = total_fee - paid_amount
            
            if balance > 0:
                outstanding_list.append({
                    "student_id": student.id,
                    "student_name": student.user.get_full_name(),
                    "reg_no": student.reg_no,
                    "guardian_phone": student.guardian_phone,
                    "course_title": course.title,
                    "total_fee": total_fee,
                    "paid_amount": paid_amount,
                    "balance": balance
                })

        return Response(outstanding_list)