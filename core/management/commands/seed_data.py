import random
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from faker import Faker

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from model_bakery import baker

# Import all necessary models
from accounts.models import Role, User
from courses.models import Course, Trainer, Batch, Enrollment, BatchFeedback, CourseMaterial
from certificates.models import Certificate
from students.models import Student, Enquiry, StudentMeasurement
from finance.models import FeesReceipt, Expense, StockItem, Payroll, StockTransaction
from attendance.models import Attendance, AttendanceEntry
from messaging.models import Conversation, Message
from events.models import Event
from notifications.models import Notification

fake = Faker("en_IN")  # Use Indian locale for more realistic names/phones
TODAY = timezone.localdate()
FIVE_YEARS_AGO = TODAY - relativedelta(years=5)


class Command(BaseCommand):
    help = "Seeds the database with a large, realistic set of sample data spanning 5 years."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clean",
            action="store_true",
            help="Clean all existing data (except superusers) before seeding.",
        )
        parser.add_argument(
            "--students",
            type=int,
            default=100,
            help="Number of total students to create.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.total_students = options["students"]
        if options["clean"]:
            self._clean_db()

        self.stdout.write(self.style.HTTP_INFO("Seeding new data..."))

        # --- Seeding in dependency order ---
        self.stdout.write("1. Seeding Core Models (Roles, Admin, Courses, Trainers)...")
        core_data = self._seed_core_models()

        self.stdout.write("2. Seeding Batches (Historical and Active)...")
        batch_data = self._seed_batches(core_data)

        self.stdout.write(f"3. Seeding Student Cohorts ({self.total_students} total)...")
        self._seed_student_cohorts(core_data, batch_data)

        self.stdout.write("4. Seeding 5-Year Historical Data (Finance, Events)...")
        self._seed_historical_data(core_data)

        self.stdout.write("5. Seeding Relational Data (Attendance, Messages)...")
        self._seed_relational_data(core_data)

        self.stdout.write(self.style.SUCCESS("=" * 30))
        self.stdout.write(self.style.SUCCESS("Successfully seeded database!"))
        self.stdout.write(f"Admin Login: admin / {core_data['admin_pass']}")
        self.stdout.write(self.style.SUCCESS("=" * 30))

    def _clean_db(self):
        self.stdout.write(self.style.WARNING("Cleaning database..."))
        # Delete in reverse dependency order
        models_to_delete = [
            Certificate, BatchFeedback, AttendanceEntry, Attendance,
            FeesReceipt, Payroll, StockTransaction, Message,
            Notification, Enrollment, StudentMeasurement, CourseMaterial,
            Conversation, Student, Enquiry, Batch,
            Trainer, Course, Event, Expense, StockItem,
        ]
        for model in models_to_delete:
            model.objects.all().delete()
            self.stdout.write(f"  - Cleaned {model.__name__}")
        
        # Delete non-admin/non-superuser roles and users
        Role.objects.filter(name__in=["Trainer", "Student"]).delete()
        User.objects.filter(is_superuser=False, is_staff=True).delete()
        User.objects.filter(is_staff=False).delete()
        self.stdout.write("  - Cleaned non-admin Users and Roles")
        self.stdout.write(self.style.SUCCESS("Database cleaned."))

    def _seed_core_models(self):
        """Seeds Roles, Admin User, Courses, Trainers, and Stock."""
        
        # 1. Create Roles
        role_admin, _ = Role.objects.get_or_create(name="Admin")
        role_trainer, _ = Role.objects.get_or_create(name="Trainer")
        role_student, _ = Role.objects.get_or_create(name="Student")

        # 2. Create Admin User
        admin_pass = "admin123"
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@noor.com",
                "first_name": "Admin",
                "last_name": "User",
                "role": role_admin,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin_user.set_password(admin_pass)
            admin_user.save()

        # 3. Create Courses
        course_3m, _ = Course.objects.get_or_create(
            code="D3",
            defaults={
                "title": "3 Month Diploma",
                "duration_weeks": 12,
                "total_fees": 15000,
                "required_attendance_days": 36,
                "active": True
            }
        )
        course_6m, _ = Course.objects.get_or_create(
            code="D6",
            defaults={
                "title": "6 Month Advanced Diploma",
                "duration_weeks": 24,
                "total_fees": 30000,
                "required_attendance_days": 72,
                "active": True
            }
        )
        course_old, _ = Course.objects.get_or_create(
            code="C1",
            defaults={
                "title": "1 Month Crash Course",
                "duration_weeks": 4,
                "total_fees": 5000,
                "required_attendance_days": 12,
                "active": False  # This course is no longer offered
            }
        )

        # 4. Create Trainers (Active and Inactive)
        trainer_user_1 = baker.make(
            User,
            is_staff=True, is_superuser=False, role=role_trainer,
            first_name="Anjali", last_name="Nair", email=fake.email(),
            date_joined=fake.date_time_between(start_date="-4y", end_date="-3y"),
        )
        trainer_1 = baker.make(
            Trainer,
            user=trainer_user_1, emp_no="TR-001",
            join_date=trainer_user_1.date_joined.date(),
            salary=25000, is_active=True,
        )

        trainer_user_2 = baker.make(
            User,
            is_staff=True, is_superuser=False, role=role_trainer,
            first_name="Riya", last_name="Thomas", email=fake.email(),
            date_joined=fake.date_time_between(start_date="-1y", end_date="-6m"),
        )
        trainer_2 = baker.make(
            Trainer,
            user=trainer_user_2, emp_no="TR-002",
            join_date=trainer_user_2.date_joined.date(),
            salary=22000, is_active=True,
        )

        trainer_user_inactive = baker.make(
            User,
            is_staff=True, is_superuser=False, role=role_trainer,
            first_name="Priya", last_name="Verma", email=fake.email(),
            date_joined=fake.date_time_between(start_date="-5y", end_date="-4y"),
            is_active=False,  # Left the institute
        )
        trainer_inactive = baker.make(
            Trainer,
            user=trainer_user_inactive, emp_no="TR-000",
            join_date=trainer_user_inactive.date_joined.date(),
            salary=20000, is_active=False, # Left the institute
        )
        
        # 5. Create Stock Items
        stock_fabric = StockItem.objects.create(name="Cotton Fabric", unit_of_measure="meters", quantity_on_hand=0, reorder_level=20)
        stock_thread = StockItem.objects.create(name="Thread Spool", unit_of_measure="pieces", quantity_on_hand=0, reorder_level=50)

        return {
            "admin_user": admin_user,
            "admin_pass": admin_pass,
            "roles": {"admin": role_admin, "trainer": role_trainer, "student": role_student},
            "courses": {"c3": course_3m, "c6": course_6m, "old": course_old},
            "trainers": {"t1": trainer_1, "t2": trainer_2, "t_inactive": trainer_inactive},
            "stock": {"fabric": stock_fabric, "thread": stock_thread},
        }

    def _seed_batches(self, core_data):
        """Seeds historical and active batches."""
        
        # Historical Batches
        batch_2021_a = baker.make(Batch, code="3M-2021-A", course=core_data["courses"]["c3"], trainer=core_data["trainers"]["t1"], schedule={"Mon": "10-12"})
        batch_2022_a = baker.make(Batch, code="6M-2022-A", course=core_data["courses"]["c6"], trainer=core_data["trainers"]["t_inactive"], schedule={"Tue": "10-12"})
        batch_2023_a = baker.make(Batch, code="3M-2023-A", course=core_data["courses"]["c3"], trainer=core_data["trainers"]["t1"], schedule={"Wed": "10-12"})
        batch_2024_a = baker.make(Batch, code="6M-2024-A", course=core_data["courses"]["c6"], trainer=core_data["trainers"]["t1"], schedule={"Thu": "14-16"})
        
        # Active Batches
        batch_active_1 = baker.make(Batch, code="3M-2025-A", course=core_data["courses"]["c3"], trainer=core_data["trainers"]["t1"], schedule={"Mon": "14-16"})
        batch_active_2 = baker.make(Batch, code="6M-2025-B", course=core_data["courses"]["c6"], trainer=core_data["trainers"]["t2"], schedule={"Fri": "10-12"})

        return {
            "historical": [batch_2021_a, batch_2022_a, batch_2023_a, batch_2024_a],
            "active": [batch_active_1, batch_active_2],
        }

    def _seed_student_cohorts(self, core_data, batch_data):
        """Creates students with different lifecycle statuses."""
        
        # Define cohort sizes
        total = self.total_students
        size_active = int(total * 0.25)
        size_dropped = int(total * 0.15)
        size_grad_recent = int(total * 0.30)
        size_grad_old = total - size_active - size_dropped - size_grad_recent

        role_student = core_data["roles"]["student"]
        admin_user = core_data["admin_user"]
        
        student_cohorts = {
            "active": [],
            "completed": [],
            "dropped": []
        }

        # --- Cohort 1: Active Students ---
        self.stdout.write(f"  - Seeding {size_active} 'Active' students...")
        for _ in range(size_active):
            adm_date = fake.date_between_dates(date_start=TODAY - relativedelta(months=3), date_end=TODAY)
            student, batch = self._create_student(role_student, adm_date)
            enrollment = baker.make(Enrollment, student=student, batch=random.choice(batch_data["active"]), status="active", enrolled_on=adm_date)
            
            # Partial payment
            baker.make(FeesReceipt,
                student=student, course=enrollment.batch.course, batch=enrollment.batch,
                amount=enrollment.batch.course.total_fees / 3,
                mode=random.choice(['upi', 'cash']),
                posted_by=admin_user,
                _quantity=random.choice([1, 2])
            )
            student_cohorts["active"].append(student)

        # --- Cohort 2: Dropped Students ---
        self.stdout.write(f"  - Seeding {size_dropped} 'Dropped' students...")
        for _ in range(size_dropped):
            adm_date = fake.date_between_dates(date_start=FIVE_YEARS_AGO + relativedelta(years=2), date_end=TODAY - relativedelta(years=1))
            student, batch = self._create_student(role_student, adm_date)
            enrollment = baker.make(Enrollment, student=student, batch=random.choice(batch_data["historical"]), status="dropped", enrolled_on=adm_date)
            
            # One partial payment
            if random.random() > 0.3: # 70% chance of having made one payment
                baker.make(FeesReceipt,
                    student=student, course=enrollment.batch.course, batch=enrollment.batch,
                    amount=enrollment.batch.course.total_fees / 4,
                    mode='cash', posted_by=admin_user
                )
            student_cohorts["dropped"].append(student)

        # --- Cohort 3: Recent Graduates ---
        self.stdout.write(f"  - Seeding {size_grad_recent} 'Recent Graduates'...")
        for _ in range(size_grad_recent):
            adm_date = fake.date_between_dates(date_start=FIVE_YEARS_AGO + relativedelta(years=3), date_end=TODAY - relativedelta(months=6))
            student, batch = self._create_student(role_student, adm_date)
            enrollment = baker.make(Enrollment,
                student=student, batch=random.choice(batch_data["historical"]),
                status="completed", enrolled_on=adm_date,
                completion_date=adm_date + relativedelta(weeks=batch.course.duration_weeks + 2)
            )
            
            # Full payment
            baker.make(FeesReceipt,
                student=student, course=enrollment.batch.course, batch=enrollment.batch,
                amount=enrollment.batch.course.total_fees,
                mode='upi', posted_by=admin_user
            )
            # Issue Certificate
            baker.make(Certificate, student=student, course=enrollment.batch.course)
            student_cohorts["completed"].append(student)

        # --- Cohort 4: Historical Graduates ---
        self.stdout.write(f"  - Seeding {size_grad_old} 'Historical Graduates'...")
        for _ in range(size_grad_old):
            adm_date = fake.date_between_dates(date_start=FIVE_YEARS_AGO, date_end=FIVE_YEARS_AGO + relativedelta(years=2))
            student, batch = self._create_student(role_student, adm_date)
            enrollment = baker.make(Enrollment,
                student=student, batch=random.choice(batch_data["historical"]),
                status="completed", enrolled_on=adm_date,
                completion_date=adm_date + relativedelta(weeks=batch.course.duration_weeks + 2)
            )
            # Full payment
            baker.make(FeesReceipt,
                student=student, course=enrollment.batch.course, batch=enrollment.batch,
                amount=enrollment.batch.course.total_fees,
                mode='bank', posted_by=admin_user
            )
            # Issue Certificate
            baker.make(Certificate, student=student, course=enrollment.batch.course)
            student_cohorts["completed"].append(student)
        
        return student_cohorts

    def _create_student(self, role, adm_date):
        """Helper to create a User, Student, and Measurements."""
        user = baker.make(
            User,
            is_staff=False, is_superuser=False, role=role,
            username=fake.unique.user_name(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            date_joined=adm_date
        )
        student = Student.objects.create(
            user=user,
            guardian_name=fake.name(),
            guardian_phone=fake.phone_number(),
            admission_date=adm_date,
            address=fake.address(),
            active=(adm_date > TODAY - relativedelta(years=2)) # Only active if joined in last 2 years
        )
        
        # Generate Reg No
        student.reg_no = f"STU{adm_date.year}-{student.id:04d}"
        student.save()
        
        # Create measurements
        baker.make(StudentMeasurement,
            student=student,
            date_taken=adm_date,
            chest=random.uniform(30, 42),
            waist=random.uniform(28, 40),
            hips=random.uniform(32, 45)
        )
        
        # Pick a batch (will be overwritten by cohort logic, but good default)
        batch = random.choice(Batch.objects.all())
        return student, batch

    def _seed_historical_data(self, core_data):
        """Seeds 5 years of Expenses, Payroll, Enquiries, Events, etc."""
        
        admin_user = core_data["admin_user"]
        trainers = core_data["trainers"]
        stock_fabric = core_data["stock"]["fabric"]
        stock_thread = core_data["stock"]["thread"]

        # Loop through each month from 5 years ago to today
        current_month_start = FIVE_YEARS_AGO.replace(day=1)
        while current_month_start <= TODAY:
            month_str = current_month_start.strftime("%Y-%m")
            
            # --- Seed Payroll ---
            for trainer in [trainers["t1"], trainers["t2"], trainers["t_inactive"]]:
                if trainer.is_active and trainer.join_date <= current_month_start:
                    baker.make(Payroll,
                        trainer=trainer,
                        month=month_str,
                        net_pay=trainer.salary,
                        status="Paid"
                    )
            
            # --- Seed Expenses ---
            baker.make(Expense,
                date=current_month_start + timedelta(days=random.randint(0, 27)),
                description=random.choice(["Rent", "Electricity Bill", "Maintenance"]),
                category=random.choice(["maintenance", "other"]),
                amount=random.randint(1000, 15000),
                added_by=admin_user
            )

            # --- Seed Stock Transactions ---
            baker.make(StockTransaction,
                item=stock_fabric,
                quantity_changed=random.randint(20, 50), # Purchase
                reason=f"PO-{current_month_start.month}{current_month_start.year}",
                user=admin_user
            )
            baker.make(StockTransaction,
                item=stock_thread,
                quantity_changed=random.randint(50, 100), # Purchase
                reason=f"PO-{current_month_start.month}{current_month_start.year}",
                user=admin_user
            )
            baker.make(StockTransaction,
                item=stock_fabric,
                quantity_changed=random.randint(-15, -5), # Usage
                reason="Used for batch work",
                user=admin_user
            )

            # --- Seed Enquiries ---
            baker.make(Enquiry,
                status=random.choice(["new", "converted", "closed"]),
                course_interest=random.choice(["3 Month", "6 Month"]),
                created_at=current_month_start
            )

            # --- Seed Events ---
            if current_month_start.month == 8: # August
                baker.make(Event,
                    title=f"Onam Holiday {current_month_start.year}",
                    start_date=current_month_start.replace(day=20),
                    created_by=admin_user
                )

            current_month_start += relativedelta(months=1)

    def _seed_relational_data(self, core_data):
        """Seeds data that depends on students (Attendance, Messages, etc.)."""

        # --- Seed Attendance for Active Batches ---
        self.stdout.write("  - Seeding sample attendance for active batches...")
        active_batches = Batch.objects.filter(code__icontains="2025")
        for batch in active_batches:
            active_enrollments = batch.enrollments.filter(status="active")
            if not active_enrollments:
                continue
                
            # Create 10 attendance days in the last month
            for i in range(10):
                att_date = TODAY - timedelta(days=i * 3) # Mon, Fri, Tue, ...
                attendance_sheet = baker.make(Attendance,
                    batch=batch,
                    date=att_date,
                    taken_by=batch.trainer.user if batch.trainer else core_data["admin_user"]
                )
                
                # Mark attendance for each student
                for enrollment in active_enrollments:
                    baker.make(AttendanceEntry,
                        attendance=attendance_sheet,
                        student=enrollment.student,
                        status=random.choice(["P", "P", "P", "P", "A", "L"]) # 80% present
                    )

        # --- Seed Sample Conversation ---
        self.stdout.write("  - Seeding sample conversations...")
        active_student = Student.objects.filter(enrollments__status="active").first()
        if active_student:
            convo = baker.make(Conversation, student=active_student)
            baker.make(Message, conversation=convo, sender=active_student.user, body="Hi, when is the next holiday?")
            baker.make(Message, conversation=convo, sender=core_data["admin_user"], body="Hi! The next holiday is for Onam. You can check the Events calendar in the app.")
            convo.mark_as_read_by(active_student.user) # Student read the reply

        # --- Seed Sample Feedback ---
        self.stdout.write("  - Seeding sample feedback...")
        completed_enrollment = Enrollment.objects.filter(status="completed").first()
        if completed_enrollment:
            baker.make(BatchFeedback,
                enrollment=completed_enrollment,
                rating=random.randint(4, 5),
                comments="Great course! The trainer was very helpful."
            )

        # --- Seed Notifications ---
        self.stdout.write("  - Seeding sample notifications...")
        all_active_users = User.objects.filter(is_active=True)
        notifications_to_create = [
            Notification(
                user=user,
                title="Welcome to the New Dashboard!",
                message="We've updated the student portal. Please check out the new features.",
                level="info"
            )
            for user in all_active_users
        ]
        Notification.objects.bulk_create(notifications_to_create)