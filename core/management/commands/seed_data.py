import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from model_bakery import baker
from faker import Faker

from accounts.models import Role, User
from courses.models import Course, Trainer, Batch, Enrollment
from certificates.models import Certificate
from students.models import Student, Enquiry
from finance.models import FeesReceipt, Expense, StockItem
from attendance.models import Attendance, AttendanceEntry
from messaging.models import Conversation, Message
from events.models import Event

fake = Faker()

class Command(BaseCommand):
    help = "Seeds the database with a realistic set of sample data."

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean all existing data before seeding.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clean']:
            self.stdout.write(self.style.WARNING("Cleaning database..."))
            # Delete in reverse dependency order
            Certificate.objects.all().delete()
            AttendanceEntry.objects.all().delete()
            Attendance.objects.all().delete()
            FeesReceipt.objects.all().delete()
            Enrollment.objects.all().delete()
            Student.objects.all().delete()
            Enquiry.objects.all().delete()
            Batch.objects.all().delete()
            Trainer.objects.all().delete()
            Course.objects.all().delete()
            Conversation.objects.all().delete()
            Event.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            Role.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Database cleaned."))

        self.stdout.write(self.style.HTTP_INFO("Seeding new data..."))

        # 1. Create Roles
        role_admin = Role.objects.create(name="Admin")
        role_trainer = Role.objects.create(name="Trainer")
        role_student = Role.objects.create(name="Student")

        # 2. Create Admin User
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@noor.com",
            password="admin123",
            first_name="Admin",
            last_name="User",
            role=role_admin
        )

        # 3. Create Courses
        course_3m = baker.make(
            Course,
            code="D3",
            title="3 Month Diploma",
            duration_weeks=12,
            total_fees=15000,
            required_attendance_days=36
        )
        course_6m = baker.make(
            Course,
            code="D6",
            title="6 Month Advanced Diploma",
            duration_weeks=24,
            total_fees=30000,
            required_attendance_days=72
        )

        # 4. Create Trainers (Simplified)
        trainers = []
        for i in range(2):
            trainer_user = baker.make(
                User,
                is_staff=True,
                is_superuser=False,
                role=role_trainer,
                username=fake.unique.user_name(),
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )
            trainer = baker.make(
                Trainer,
                user=trainer_user,
                emp_no=fake.unique.numerify(text="TR-####"),
                join_date=fake.date_between(start_date="-2y", end_date="-1y"),
                salary=random.choice([20000, 25000, 30000])
            )
            trainers.append(trainer)
        self.stdout.write(f"Created {len(trainers)} trainers.")

        # 5. Create Batches
        batch_a = baker.make(Batch, code="3M-A", course=course_3m, trainer=trainers[0], schedule={"Mon": "10-12", "Wed": "10-12"})
        batch_b = baker.make(Batch, code="6M-B", course=course_6m, trainer=trainers[1], schedule={"Tue": "14-16", "Thu": "14-16"})

        # 6. Create Enquiries
        baker.make(Enquiry, status="new", _quantity=5)
        baker.make(Enquiry, status="closed", _quantity=3)
        self.stdout.write(f"Created 8 enquiries.")

        # 7. Create Students and Enroll them (Simplified)
        students = []
        for i in range(10):
            student_user = baker.make(
                User,
                is_staff=False,
                is_superuser=False,
                role=role_student,
                username=fake.unique.user_name(),
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )
            student = baker.make(
                Student,
                user=student_user,
                reg_no=None, # Will be set by serializer/save
                admission_date=fake.date_between(start_date="-1y", end_date="today"),
                guardian_name=fake.name(),
                guardian_phone=fake.phone_number()
            )
            students.append(student)

            # Enroll them
            batch = batch_a if i < 5 else batch_b
            enrollment = baker.make(Enrollment, student=student, batch=batch)
            
            # 8. Create FeesReceipts for them
            baker.make(
                FeesReceipt,
                student=student,
                course=batch.course,
                batch=batch,
                amount=batch.course.total_fees / 2, # Half payment
                mode=random.choice(['upi', 'cash']),
                posted_by=admin_user
            )
        self.stdout.write(f"Created {len(students)} students and enrolled them.")

        # 9. Mark one student as completed
        student_to_complete = students[0]
        enrollment = student_to_complete.enrollments.first()
        course = enrollment.batch.course
        
        # --- FIX: Create multiple attendance sheets, one for each day ---
        # 10. Create Attendance for their batch to mark them as completed
        days_to_create = course.required_attendance_days + 1
        for i in range(days_to_create):
            # Create a new attendance sheet for a different day in the past
            attendance_date = timezone.now().date() - timedelta(days=i + 1)
            attendance_sheet = baker.make(
                Attendance, 
                batch=enrollment.batch, 
                date=attendance_date, 
                taken_by=admin_user
            )
            # Create the single 'Present' entry for this student on this day
            baker.make(
                AttendanceEntry, 
                attendance=attendance_sheet, 
                student=student_to_complete, 
                status="P"
            )
        
        # Trigger the completion check
        enrollment.check_and_update_status()
        self.stdout.write(f"Marked student {student_to_complete.user.username} as completed.")

        # 11. Issue a Certificate for them
        cert = baker.make(Certificate, student=student_to_complete, course=course)
        self.stdout.write(f"Issued Certificate {cert.certificate_no} to student.")

        # 12. Create a Conversation
        convo = baker.make(Conversation, student=students[1])
        baker.make(Message, conversation=convo, sender=students[1].user, body=fake.sentence())
        baker.make(Message, conversation=convo, sender=admin_user, body=fake.sentence())
        self.stdout.write(f"Created a sample conversation.")

        # 13. Create an Event
        baker.make(Event, title="Onam Holiday", description="Institute will be closed for Onam.", start_date=timezone.now().date() + timedelta(days=10), created_by=admin_user)
        self.stdout.write(f"Created a sample event.")

        # 14. Create other misc items
        baker.make(Expense, category=random.choice(['material', 'maintenance']), amount=fake.random_int(min=500, max=5000), added_by=admin_user, _quantity=5)
        baker.make(StockItem, name="Fabric (meters)", unit_of_measure="meters", quantity_on_hand=100)
        self.stdout.write(f"Created sample expenses and stock.")

        self.stdout.write(self.style.SUCCESS("Successfully seeded database!"))
        self.stdout.write(f"Admin Login: admin / admin123")