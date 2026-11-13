"""Seed local demo data: an admin user, a learner, one course with lessons and an exam.

Local development only. Usage: python manage.py seed_demo
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from onlinecourse.models import Choice, Course, Enrollment, Instructor, Lesson, Question

DEMO_ADMIN = ("admin", "admin12345")
DEMO_LEARNER = ("learner", "learner12345")


class Command(BaseCommand):
    help = "Create demo users, a course, lessons and exam questions"

    def handle(self, *args, **options):
        admin, created = User.objects.get_or_create(username=DEMO_ADMIN[0], defaults={
            "is_staff": True, "is_superuser": True, "first_name": "Admin"})
        if created:
            admin.set_password(DEMO_ADMIN[1])
            admin.save()
        learner, created = User.objects.get_or_create(username=DEMO_LEARNER[0], defaults={
            "first_name": "Leo", "last_name": "Learner"})
        if created:
            learner.set_password(DEMO_LEARNER[1])
            learner.save()

        instructor, _ = Instructor.objects.get_or_create(user=admin, defaults={"total_learners": 1})
        course, created = Course.objects.get_or_create(name="Learning Django", defaults={
            "description": "Build web apps with Django: models, views, templates and the admin site."})
        course.instructors.add(instructor)
        if created:
            lessons = [
                ("Introduction to Django", "Django is a high-level Python web framework."),
                ("Models and the ORM", "Models map Python classes to database tables."),
                ("Views and Templates", "Views handle requests; templates render HTML."),
            ]
            for order, (title, content) in enumerate(lessons):
                Lesson.objects.create(course=course, order=order, title=title, content=content)
            exam = [
                ("Django is a framework written in which language?", 50,
                 [("Python", True), ("Java", False), ("Ruby", False)]),
                ("Which of these are Django components?", 50,
                 [("Models", True), ("Views", True), ("Servlets", False)]),
            ]
            for content, grade, choices in exam:
                q = Question.objects.create(course=course, content=content, grade=grade)
                for text, correct in choices:
                    Choice.objects.create(question=q, content=text, is_correct=correct)
        if not Enrollment.objects.filter(user=learner, course=course).exists():
            Enrollment.objects.create(user=learner, course=course, mode="honor")
            course.total_enrollment += 1
            course.save()
        self.stdout.write(self.style.SUCCESS("Demo data ready (course id %d)" % course.id))
