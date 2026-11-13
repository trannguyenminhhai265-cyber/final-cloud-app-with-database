from django.contrib import admin
# Import all seven models
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission


# ChoiceInline: edit choices inside a question
class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 2


# QuestionInline: edit questions inside a course
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 5


# Register your models here.
class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline, QuestionInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']


# QuestionAdmin: show choices inline for each question
class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ['content', 'course', 'grade']
    list_filter = ['course']
    search_fields = ['content']


# LessonAdmin
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']


admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Submission)
