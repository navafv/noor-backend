from django.db.models import Sum
from django.db.models.functions import TruncMonth
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import FeesReceipt, Expense
from courses.models import Course, Enrollment
from api.permissions import IsAdmin
from students.models import Student

class FinanceAnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [IsAdmin]

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        total_income = FeesReceipt.objects.aggregate(total=Sum("amount"))["total"] or 0
        total_income = float(total_income)
        total_active_students = Student.objects.filter(
            enrollments__status="active"
        ).distinct().count()
        data = {
            "total_income": total_income,
            "total_active_students": total_active_students,
        }
        return Response(data)

    @action(detail=False, methods=["get"], url_path="income-expense")
    def income_expense_timeline(self, request):
        income_data = (
            FeesReceipt.objects
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(total_income=Sum("amount"))
            .order_by("month")
        )        
        expense_data = (
            Expense.objects
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(total_expense=Sum("amount"))
            .order_by("month")
        )
        timeline = {}
        for rec in income_data:
            if not rec["month"]: continue
            key = rec["month"].strftime("%Y-%m")
            timeline.setdefault(key, {"month": key, "income": 0, "expense": 0, "payroll": 0})
            timeline[key]["income"] += float(rec["total_income"] or 0)
        for rec in expense_data:
            if not rec["month"]: continue
            key = rec["month"].strftime("%Y-%m")
            timeline.setdefault(key, {"month": key, "income": 0, "expense": 0, "payroll": 0})
            timeline[key]["expense"] += float(rec["total_expense"] or 0)
        for data in timeline.values():
            data["net_profit"] = round(data["income"] - (data["expense"] + data["payroll"]), 2)
        return Response(sorted(timeline.values(), key=lambda x: x["month"]))

    @action(detail=False, methods=["get"], url_path="course/(?P<course_id>[^/.]+)")
    def course_summary(self, request, course_id=None):
        """
        Shows total income and student count for a specific course.
        """
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found."}, status=404)

        receipts = (
            FeesReceipt.objects.filter(course=course)
            .aggregate(total_income=Sum("amount"))
        )
        
        # Count unique students enrolled in this course
        active_students = Enrollment.objects.filter(
            batch__course=course,
            status="active"
        ).values("student").distinct().count()

        data = {
            "course": course.title,
            "total_income": float(receipts["total_income"] or 0),
            "active_students": active_students,
        }
        return Response(data)