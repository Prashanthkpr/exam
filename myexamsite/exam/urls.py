from django.contrib import admin
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
# from django.contrib.auth.views import logout


app_name='exam'

urlpatterns = [
	path('', views.index , name='index'),
	path('logout/', views.logout_user ,name='logout-user'),
	path('register/', views.register ,name='register'),
	path('login/', views.login_user ,name='login-user'),
	path('user/profile/', views.user_profile ,name='user-profile'),
    path('applicant/assignment/start/',views.applicant_exam ,name='applicant-exam'),
    path('applicant/assignment/result/',views.result ,name='applicant-result'),
    path('organisation/admin/assignment/',views.admin_assignment ,name='admin-assignment'),
    path('organisation/admin/assignment/create',views.admin_assignment_create ,name='admin-assignment-create'),
    path('organisation/admin/assignment/update/<int:id>/',views.admin_assignment_update ,name='admin-assignment-update'),
    path('organisation/admin/assignment/delete/',views.admin_assignment_delete ,name='admin-assignment-delete'),
    path('organisation/admin/exam/',views.admin_exam ,name='admin-exam'),
    path('organisation/admin/exam/create/',views.admin_exam_create ,name='admin-exam-create'),
    path('organisation/admin/exam/update/<int:id>/',views.admin_exam_update ,name='admin-exam-update'),
    path('organisation/admin/exam/delete/',views.admin_exam_delete ,name='admin-exam-delete'),
    path('organisation/admin/applicants/',views.admin_applicants_list ,name='admin-applicants'),
    path('organisation/admin/applicant/create/',views.admin_applicant_create ,name='admin-applicant-create'),
    path('organisation/admin/applicant/update',views.admin_applicant_update ,name='admin-applicant-update'),
    path('organisation/admin/applicant/delete/',views.admin_applicant_delete ,name='admin-applicant-delete'),
    path('organisation/admin/questions/',views.admin_questions ,name='admin-questions'),
    path('organisation/admin/question/create/',views.admin_question_create ,name='admin-question-create'),
    path('organisation/admin/question/update/<int:id>/',views.admin_question_update ,name='admin-question-update'),
    path('organisation/admin/question/delete/',views.admin_question_delete ,name='admin-question-delete'),
    path('organisation/admin/assignment/result/<int:id>/',views.admin_assignment_result ,name='admin-assignment-result'),
    path('organisation/admin/applicants/filter/',views.admin_applicants_filter ,name='admin-applicants-filter'),
    path('organisation/admin/questions/filter/',views.admin_questions_filter ,name='admin-questions-filter'),
    path('organisation/admin/exams/filter/',views.admin_exams_filter ,name='admin-exams-filter'),
    path('organisation/admin/assignments/filter/',views.admin_assignments_filter ,name='admin-assignments-filter'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
