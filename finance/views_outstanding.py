from rest_framework import viewsets
from rest_framework.response import Response
from api.permissions import IsAdmin
from courses.models import Enrollment
from .models import FeesReceipt
from django.db.models import Sum, OuterRef, Subquery, F, DecimalField
from django.db.models.functions import Coalesce

class OutstandingFeesViewSet(viewsets.ViewSet):
    """
    Lists students who have paid less than the course total fee.
    Optimized to avoid N+1 queries.
    """
    permission_classes = [IsAdmin]

    def list(self, request):
        # Subquery to calculate total paid per student per course
        paid_subquery = FeesReceipt.objects.filter(
            student=OuterRef('student'),
            course=OuterRef('course')
        ).values('student', 'course').annotate(
            total_paid=Sum('amount')
        ).values('total_paid')

        # Annotate enrollments with the paid amount
        enrollments = Enrollment.objects.filter(status='active').select_related(
            'student', 'course', 'student__user'
        ).annotate(
            paid_amount=Coalesce(Subquery(paid_subquery), 0, output_field=DecimalField()),
            balance=F('course__total_fees') - F('paid_amount')
        ).filter(balance__gt=0)  # Filter efficiently at DB level

        outstanding_list = []
        for enrollment in enrollments:
            outstanding_list.append({
                "student_id": enrollment.student.id,
                "student_name": enrollment.student.user.get_full_name(),
                "reg_no": enrollment.student.reg_no,
                "guardian_phone": enrollment.student.guardian_phone,
                "student_phone": enrollment.student.user.phone,
                "course_title": enrollment.course.title,
                "total_fee": enrollment.course.total_fees,
                "paid_amount": enrollment.paid_amount,
                "balance": enrollment.balance
            })

        return Response(outstanding_list)