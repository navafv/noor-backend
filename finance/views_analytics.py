from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.permissions import IsAdmin
from .models import FeesReceipt, Expense
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone

class FinanceDashboardView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        now = timezone.now()
        current_month = now.month
        current_year = now.year

        # 1. Summary Cards
        total_revenue = FeesReceipt.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        total_expense = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        
        month_revenue = FeesReceipt.objects.filter(
            date__month=current_month, date__year=current_year
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        month_expense = Expense.objects.filter(
            date__month=current_month, date__year=current_year
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        # 2. Revenue Chart Data (Last 6 months)
        # This logic is simplified; for robust charting, you might want a specific helper
        revenue_by_month = (
            FeesReceipt.objects.annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('-month')[:6]
        )
        
        chart_data = []
        for entry in revenue_by_month:
            chart_data.append({
                "month": entry['month'].strftime("%b %Y"),
                "revenue": entry['total']
            })
        chart_data.reverse()

        # 3. Recent Transactions
        recent_receipts = FeesReceipt.objects.select_related('student__user').order_by('-created_at')[:5]
        recent_expenses = Expense.objects.order_by('-created_at')[:5]
        
        transactions = []
        for r in recent_receipts:
            transactions.append({
                "type": "credit",
                "description": f"Fees: {r.student.user.get_full_name()}",
                "amount": r.amount,
                "date": r.date
            })
        for e in recent_expenses:
            transactions.append({
                "type": "debit",
                "description": f"Exp: {e.title}",
                "amount": e.amount,
                "date": e.date
            })
        
        # Sort combined list by date desc
        transactions.sort(key=lambda x: x['date'], reverse=True)

        return Response({
            "summary": {
                "total_revenue": total_revenue,
                "total_expense": total_expense,
                "net_income": total_revenue - total_expense,
                "month_revenue": month_revenue,
                "month_expense": month_expense
            },
            "chart_data": chart_data,
            "recent_transactions": transactions[:10]
        })