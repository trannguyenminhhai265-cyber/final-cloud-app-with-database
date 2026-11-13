from django.shortcuts import render
from django.http import HttpResponseRedirect
# <HINT> Import any new Models here
from .models import Course, Enrollment, Question, Choice, Submission
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# CourseListView
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_details_bootstrap.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_enrolled'] = check_if_enrolled(self.request.user, self.object)
        return context


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


# Submit view: create an exam submission record for a course enrollment
def submit(request, course_id):
    # Get user and course object, then the associated enrollment
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = get_object_or_404(Enrollment, user=user, course=course)
    # Create a submission object referring to the enrollment
    submission = Submission.objects.create(enrollment=enrollment)
    # Collect the selected choices from the exam form and add them to the submission
    choices = extract_answers(request)
    submission.choices.set(choices)
    submission_id = submission.id
    # Redirect to show_exam_result with the submission id
    return HttpResponseRedirect(reverse(viewname='onlinecourse:exam_result',
                                        args=(course_id, submission_id,)))


# An example method to collect the selected choices from the exam form from the request object
def extract_answers(request):
   submitted_anwsers = []
   for key in request.POST:
       if key.startswith('choice'):
           value = request.POST[key]
           choice_id = int(value)
           submitted_anwsers.append(choice_id)
   return submitted_anwsers


# Exam result view: check if learner passed the exam and show results for each question
def show_exam_result(request, course_id, submission_id):
    context = {}
    # Get course and submission based on their ids
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    # Get the selected choice ids from the submission record
    choices = submission.choices.all()
    selected_ids = [choice.id for choice in choices]
    # For each question, check whether the selected answers are correct and sum the score
    total_score = 0
    possible_score = 0
    questions = course.question_set.all()
    for question in questions:
        possible_score += question.grade
        if question.is_get_score(selected_ids):
            total_score += question.grade
    grade = round(total_score * 100 / possible_score) if possible_score > 0 else 0
    context['course'] = course
    context['grade'] = grade
    context['total_score'] = total_score
    context['possible_score'] = possible_score
    context['choices'] = choices
    context['selected_ids'] = selected_ids
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
