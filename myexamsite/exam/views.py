from django.shortcuts import render,redirect,get_object_or_404
from users.models import User
from exam.forms import *
from users.forms import *
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.urls import reverse
from datetime import datetime,timezone
from django.contrib import messages
from django.forms import formset_factory,inlineformset_factory
from django.contrib.auth.models import Group
from django.core.serializers import serialize



# Create your views here.

def index(request):
	user=request.user
	if not user.is_active:
		return redirect('exam:login-user')
	elif user.is_active and user.groups.filter(name='applicant'):
		assign=Assignment.objects.filter(user=user)
		return render(request,'exam/applicant_home.html',{'user':user,'assignments':assign})
	elif user.is_active and user.groups.filter(name='company_admin'):
		return render(request,'exam/admin_home.html',{'user':user})
	else:
		return render(request,'exam/invalid_access.html')


@login_required
def applicant_exam(request):
	slug=request.POST.get('data_exam_name_slug')
	id=request.POST.get('data_assignment_id')
	status=Assignment.PENDING
	user=request.user
	question=[]
	if request.method == 'POST':
		assignment =Assignment.objects.get(id=id)
		question=assignment.exam.question_paper.all()
		extension={'image':["jpg","png","jpeg","gif","tiff","exif"],'document':['pdf','doc','docx','odt','txt']}
		exam=assignment.exam
		duration = assignment.duration
		context={
			'question_list':question,
			'user':user,
			'exam':exam,
			'extension':extension,
			'assignment_id':id,
			}
		if not assignment.attempts.exists():
			attempt_obj=Attempt.objects.create(start_time=datetime.now(timezone.utc))
			assignment.attempts.add(attempt_obj)
			context['time_left']=duration
			context['attempt']=attempt_obj
			return render(request,'exam/applicant_exam.html',context=context)
		else:
			attempt_first=assignment.attempts.first()
			start_time=attempt_first.start_time
			time_spend=(datetime.now(timezone.utc)-start_time).seconds
			time_left=duration-time_spend
			if time_left<duration:
				attempt_obj=Attempt.objects.create(start_time=datetime.now(timezone.utc))
				assignment.attempts.add(attempt_obj)
				context['time_left']=time_left
				context['attempt']=attempt_obj

				return render(request,'exam/applicant_exam.html',context=context)
			return redirect('/')


@login_required
def result(request):
	if request.method == 'POST':
		assignment_id=request.POST.get('assignment_id')
		user_data=[]
		score=0
		count =0
		assignment =Assignment.objects.get(id=assignment_id)
		questions=assignment.exam.question_paper.all()
		attempt_obj=Attempt.objects.all().latest('id')
		attempt_obj.end_time=datetime.now(timezone.utc)
		duration=(attempt_obj.end_time-attempt_obj.start_time).seconds
		attempt_obj.duration=duration
		attempt_obj.save()
		for question in questions:
			data={}
			count+=1
			data['question']=question.question_text
			choice_id=request.POST.get('choice{0}'.format(question.id))
			data['correct_answer']=question.answer
			if question.question_type =='choice':
				try:
					data['answer']=Choice.objects.get(id=choice_id)
				except:
					data['answer']=None
				AnswerSheet.objects.create(assignment=assignment,user=request.user,question=question,answer=data['answer'],exam=assignment.exam)
			else:
				try:
					data['answer']=choice_id
				except:
					data['answer']=None
				AnswerSheet.objects.create(assignment=assignment,user=request.user,question=question,answer_text=data['answer'],exam=assignment.exam)
			if str(data['answer']) == str(data['correct_answer']):
				score+=1

			user_data.append(data)
		if (score/count)*100 >= 60:
			message="Congrats You are selected for next round"
			assignment.exam_status=Assignment.PASS
		else:
			message="""Sorry, You are rejected.
			Better luck for next time.
			Thank you,Have a nice day."""
			assignment.exam_status=Assignment.FAIL
		assignment.status=Assignment.FINISHED
		assignment.score=score
		assignment.save()
		answer_sheet=AnswerSheet.objects.filter(assignment=assignment)
		context={
		'assignment':assignment,
		'answer_sheet':answer_sheet,
		}
		return render(request,'exam/applicant_result.html',context=context)

@login_required
def admin_questions(request):
	question=Question.objects.all()
	tags=Tag.objects.all()
	question_type=Question.question_choice
	if request.method=='GET':
		context={
		'questions_list':question,
		'tags':tags,
		'question_type':question_type
		}
		return render(request,'exam/admin_questions.html',context=context)
	return redirect('exam:index')
@login_required
def admin_question_create(request):
	question_form=QuestionForm()
	choice_formset=ChoiceFormSet(prefix='choice')
	answer_form=AnswerForm()
	attachment_formset=AttachmentFormSet(prefix='attachment')
	tags=Tag.objects.all()
	if request.method=='GET':

		context={
		'question_form':question_form,
		'choice_formset':choice_formset,
		'answer_form':answer_form,
		'attachment_formset':attachment_formset,
		'tags':tags
		}
		return render(request,'exam/admin_question_create.html',context=context)
	if request.method=="POST":
		question_form=QuestionForm(request.POST)
		attachment_formset=AttachmentFormSet(request.POST,request.FILES,prefix='attachment')
		question_type=request.POST.get('question_type')
		question_tags_slug=request.POST.getlist('tags')
		attachment_errors=[]
		if question_type=='choice':
			question_id=0
			choice_formset=ChoiceFormSet(request.POST,prefix='choice')
			if question_form.is_valid() and choice_formset.is_valid():
				choice_name=request.POST['choice_text']
				choice_answer=request.POST[choice_name]
				question_obj=question_form.save(commit=False)
				question_obj.pub_date=datetime.now(timezone.utc)
				if attachment_formset:
					if attachment_formset.is_valid():
						for attachment_form in attachment_formset:
							if attachment_form.is_valid():
								attachment_obj=attachment_form.save()
								question_obj.save()
								question_obj.attachments.add(attachment_obj)
					else:
						attachment_errors=attachment_formset.errors
						if not attachment_formset.non_form_errors():
							return JsonResponse({'success': False,'attachment_errors':attachment_errors,})
				question_obj.save()
				question_id=question_obj.id
				for tag_slug in question_tags_slug:
					if Tag.objects.filter(name_slug=tag_slug).exists():
						tag=Tag.objects.get(name_slug=tag_slug)
					else:
						tag=Tag.objects.create(name=tag_slug)
					question_obj.tags.add(tag)
				for choice_form in choice_formset:
					if choice_form.is_valid():
						choice_obj=choice_form.save(commit=False)
						choice_obj.question=question_obj
						choice_obj.save()
					else:
						choice_formset=ChoiceFormSet(request.POST,prefix='choice')
				choice_answer=Choice.objects.get(question=question_obj,choice_text=choice_answer)
				question_obj.answer=choice_answer
				question_obj.save()
				url=reverse('exam:admin-question-update' ,args=[question_id])
				messages.success(request, 'Question created Successfully.')
				return JsonResponse({'success': True,'message':"Successfully Created",'url':url})
			return JsonResponse({'success': False,'question_errors': dict(question_form.errors.items()),'choice_errors':choice_formset.non_form_errors(),'attachment_errors':attachment_errors})
		else:
			answer_form=AnswerForm(request.POST)
			question_id=0
			if question_form.is_valid() and answer_form.is_valid():
				question_obj=question_form.save(commit=False)
				question_obj.pub_date=datetime.now(timezone.utc)
				if attachment_formset:
					if attachment_formset.is_valid():
						for attachment_form in attachment_formset:
							if attachment_form.is_valid():
								attachment_obj=attachment_form.save()
								question_obj.save()
								question_obj.attachments.add(attachment_obj)
					else:
						attachment_errors=attachment_formset.errors
						if not attachment_formset.non_form_errors():
							return JsonResponse({'success': False,'attachment_errors':attachment_errors,})
				answer_obj=answer_form.save(commit=False)
				question_obj.save()
				question_id=question_obj.id
				answer_obj.question=question_obj
				answer_obj.save()
				for tag_slug in question_tags_slug:
					if Tag.objects.filter(name_slug=tag_slug).exists():
						tag=Tag.objects.get(name_slug=tag_slug)
					else:
						tag=Tag.objects.create(name=tag_slug)
					question_obj.tags.add(tag)
				url=reverse('exam:admin-question-update' ,args=[question_id])
				messages.success(request, 'Question created Successfully.')
				return JsonResponse({'success': True,'message':"Successfully Created",'url':url})
			return JsonResponse({'success': False,'question_errors': dict(question_form.errors.items()),'answer_errors': dict(answer_form.errors.items()),'attachment_errors':attachment_errors})
	return redirect('exam:admin-questions')

@login_required
def admin_question_update(request,id):
	question_instance=Question.objects.get(id=id)
	question_type=question_instance.question_type
	attachment_queryset=question_instance.attachments.all()
	if request.method=='GET':
		question_form=QuestionForm(instance=question_instance)
		if attachment_queryset:
			attachment_formset=AttachmentUpadateFormSet(prefix='attachment',queryset=attachment_queryset)
		else:
			attachment_formset=AttachmentFormSet(prefix='attachment')
		tags=Tag.objects.all()
		context={
			'question_form':question_form,
			'attachment_formset':attachment_formset,
			'tags':tags,
		}
		if question_type=='choice':
			choice_queryset=Choice.objects.filter(question=question_instance)
			choice_formset=ChoiceUpdationFormSet(prefix='choice',instance=question_instance)
			context['choice_formset']=choice_formset
			context['choice_answer']=question_instance.answer
		else:
			answer_instance=Answer.objects.get(question=question_instance)
			answer_form=AnswerForm(instance=answer_instance)
			context['answer_form']=answer_form
		return render(request,'exam/admin_question_update.html',context=context)

	elif request.method=='POST':
		question_form=QuestionForm(request.POST,instance=question_instance)
		question_tags_slug=request.POST.getlist('tags')
		attachment_formset=AttachmentUpadateFormSet(request.POST,request.FILES,prefix='attachment',queryset=attachment_queryset)
		tags=Tag.objects.all()
		if question_type=='choice':
			choice_queryset=Choice.objects.filter(question=question_instance)
			choice_formset=ChoiceUpdationFormSet(request.POST,prefix='choice',instance=question_instance)
			if question_form.is_valid() and choice_formset.is_valid():
				choice_name=request.POST['choice_text']
				choice_answer=request.POST[choice_name]
				question_obj=question_form.save(commit=False)
				choiceset_obj=choice_formset.save(commit=False)
				question_obj.pub_date=datetime.now(timezone.utc)
				if attachment_formset:
					if attachment_formset.is_valid():
						for attachment_form in attachment_formset:
							if attachment_form.is_valid():
								attachment_obj=attachment_form.save()
								question_obj.save()
								question_obj.attachments.add(attachment_obj)
					else:
						attachment_errors=attachment_formset.errors
						if not attachment_formset.non_form_errors():
							return JsonResponse({'success': False,'attachment_errors':attachment_errors,})
				question_obj.save()
				for tag_slug in question_tags_slug:
					if Tag.objects.filter(name_slug=tag_slug).exists():
						tag=Tag.objects.get(name_slug=tag_slug)
					else:
						tag=Tag.objects.create(name=tag_slug)
					question_obj.tags.add(tag)
				for choice_form in choice_formset:
					if choice_form.is_valid():
							# choice_form.instance.delete()
						choice_obj=choice_form.save(commit=False)
						choice_obj.question=question_obj
						choice_obj.save()
					else:
						choice_formset=ChoiceUpdationFormSet(prefix='choice',instance=question_instance)
				choices=[choice.instance.id for choice in choice_formset]
				for choice in choice_queryset:
					if choice.id not in choices:
						choice.delete()
				attachments=[attachment.instance.id for attachment in attachment_formset]
				for attachment  in attachment_queryset:
					if attachment.id not in attachments:
						attachment.delete()
				choice_answer=Choice.objects.get(question=question_obj,choice_text=choice_answer)
				question_obj.answer=choice_answer
				question_obj.save()
				messages.success(request, 'Question updated Successfully.')
				return JsonResponse({'success': True,'message':"Successfully updated"})
			return JsonResponse({'success': False,'question_errors': dict(question_form.errors.items()),'choice_errors':choice_formset.non_form_errors()})
		else:
			answer_instance=Answer.objects.get(question=question_instance)
			answer_form=AnswerForm(request.POST,instance=answer_instance)
			if question_form.is_valid() and answer_form.is_valid():
				question_obj=question_form.save(commit=False)
				question_obj.pub_date=datetime.now(timezone.utc)
				answer_obj=answer_form.save(commit=False)
				if attachment_formset:
					if attachment_formset.is_valid():
						for attachment_form in attachment_formset:
							if attachment_form.is_valid:
								attachment_obj=attachment_form.save()
								question_obj.save()
								question_obj.attachments.add(attachment_obj)
					else:
						attachment_errors=attachment_formset.errors
						if not attachment_formset.non_form_errors():
							return JsonResponse({'success': False,'attachment_errors':attachment_errors,})
				question_obj.save()
				answer_obj.question=question_obj
				answer_obj.save()
				for tag_slug in question_tags_slug:
					if Tag.objects.filter(name_slug=tag_slug).exists():
						tag=Tag.objects.get(name_slug=tag_slug)
					else:
						tag=Tag.objects.create(name=tag_slug)
					question_obj.tags.add(tag)
				messages.success(request, 'Question updated Successfully.')
				return JsonResponse({'success': True,'message':"Successfully updated"})
			return JsonResponse({'success': False,'question_errors': dict(question_form.errors.items()),'answer_errors': dict(answer_form.errors.items())})
	return redirect('exam:admin-questions')

@login_required
def admin_question_delete(request):
	if request.method=='POST':
		data_question_id=request.POST.get('data_question_id')
		question_obj=Question.objects.get(id=data_question_id)
		question_obj.delete()
		messages.success(request, 'Question deleted Successfully.')
		return JsonResponse({"message":"Successfully Deleted"})
	return redirect('exam:admin-questions')

@login_required
def admin_questions_filter(request):
	if request.method=='POST':
		print(request.POST)
		questions=Question.objects.all()
		if request.POST.get('question-type'):
			questions=questions.filter(question_type=request.POST.get('question-type'))
		if request.POST.getlist('question-tags'):
			tags=Tag.objects.filter(name__in=request.POST.getlist('question-tags'))
			questions=questions.filter(tags__in=tags)
		if request.POST.get('question-description'):
			questions=questions.filter(question_text__icontains=request.POST.get('question-description'))
		questions=list(questions.values('question_type','question_text','tags__name',))
		return JsonResponse({'questions':questions})

@login_required
def admin_exam(request):
	question=Question.objects.all()
	tags=Tag.objects.all()
	exam=Exam.objects.all()
	if request.method=='GET':
		context={
		'questions_list':question,
		'exam_list':exam,
		'tags':tags
		}

		return render(request,'exam/admin_exam.html',context=context)
	return redirect('exam:admin-exam')

@login_required
def admin_exam_create(request):
	# instance= get_object_or_404(Exam, id=id)
	# print(instance)
	if request.method=='GET':
		exam_form=ExamForm()
		return render(request,'exam/admin_exam_create.html',{'exam_form':exam_form})
	if request.method=="POST":
		exam_form=ExamForm(request.POST)
		if exam_form.is_valid():
			exam_obj=exam_form.save()
			exam_id=exam_obj.id
			messages.success(request, 'Exam Created Successfully.')
			return HttpResponseRedirect(reverse('exam:admin-exam-update',args=[exam_id]))
		return render(request,'exam/admin_exam_create.html',{'exam_form':exam_form})
	return redirect('exam:admin-exam')
@login_required
def admin_exam_update(request,id):
	instance=Exam.objects.get(id=id)
	if request.method=='GET':
		exam_form=ExamForm(instance=instance)
		return render(request,'exam/admin_exam_update.html',{'exam_form':exam_form})
	elif request.method=='POST':
		exam_form=ExamForm(request.POST,instance=instance)
		if exam_form.is_valid():
			exam_form.save()
			messages.success(request, 'Exam Updated Successfully.')
			return render(request,'exam/admin_exam_update.html',{'exam_form':exam_form,})
		return render(request,'exam/admin_exam_update.html',{'exam_form':exam_form})
	return redirect('exam:admin-exam')

@login_required
def admin_exam_delete(request):
	if request.method=='POST':
		data_exam_id=request.POST.get('data_exam_id')
		exam_obj=Exam.objects.get(id=data_exam_id)
		exam_obj.delete()
		messages.success(request, 'Exam deleted Successfully.')
		return JsonResponse({"message":"Successfully Deleted"})
	return redirect('exam:admin-exam')

@login_required
def admin_exams_filter(request):
	if request.method=='POST':
		print(request.POST)
		exams=Exam.objects.all()
		if request.POST.get('exam-name'):
			exams=exams.filter(name__icontains=request.POST.get('exam-name'))
		if request.POST.get('question-description'):
			question=Question.objects.filter(question_text__icontains=request.POST.get('question-description'))
			print(question)
			exams=exams.filter(question_paper__in=question)
		print(exams)
		exams=list(exams.values('name','question_paper'))
		print(exams)
		return JsonResponse({'exams':exams})

@login_required
def admin_assignment(request):
	exam=Exam.objects.all()
	assignment=Assignment.objects.all()
	status=Assignment.STATUS_CHOICE
	exam_status=Assignment.EXAM_CHOICE
	if request.method=="GET":
		context={
		'assignment_list':assignment,
		'exam_list':exam,
		'status':status,
		'exam_status':exam_status
		}
		return render(request,'exam/admin_assignment.html',context=context)
	return redirect('exam:admin-assignment')
@login_required
def admin_assignment_create(request):
	if request.method=='GET':
		assignment_form=AssignmentForm(initial={"exam":request.GET.get('exam')})
		return render(request,'exam/admin_assignment_create.html',{'assignment_form':assignment_form})
	elif request.method=="POST":
		assignment_form=AssignmentForm(request.POST)
		if assignment_form.is_valid():
			assignment_obj=assignment_form.save()
			assignment_id=assignment_obj.id
			messages.success(request, 'Assignment Created Successfully.')
			return HttpResponseRedirect(reverse('exam:admin-assignment-update',args=[assignment_id]))
		return render(request,'exam/admin_assignment_create.html',{'assignment_form':assignment_form})
	return redirect('exam:admin-assignment')

@login_required
def admin_assignment_update(request,id):
	instance=Assignment.objects.get(id=id)
	if request.method=='GET':
		assignment_form=AssignmentUpdationForm(instance=instance)
		attempts=instance.attempts.all()
		return render(request,'exam/admin_assignment_update.html',{'assignment_form':assignment_form,'attempts':attempts})

	elif request.method=='POST':
		assignment_form=AssignmentUpdationForm(request.POST,instance=instance)
		if assignment_form.is_valid():
			assignment_form.save()
			messages.success(request, 'Assignment Updated Successfully.')
			return render(request,'exam/admin_assignment_update.html',{'assignment_form':assignment_form,})
		return render(request,'exam/admin_assignment_update.html',{'assignment_form':assignment_form})
	return redirect('exam:admin-assignment')
@login_required
def admin_assignment_delete(request):
	if request.method=='POST':
		data_assignment_id=request.POST.get('data_assignment_id')
		assignment_obj=Assignment.objects.get(id=data_assignment_id)
		assignment_obj.delete()
		messages.success(request, 'Assignment deleted Successfully.')
		return JsonResponse({"message":"Successfully Deleted"})
	return redirect('exam:admin-assignment')

@login_required
def admin_assignment_result(request,id):
	if request.method=='GET':
		assignment=Assignment.objects.get(id=id)
		answer_sheet=AnswerSheet.objects.filter(assignment=assignment)
		context={
		'assignment':assignment,
		'answer_sheet':answer_sheet,
		}
		return render(request,'exam/admin_assignment_result.html',context=context)

@login_required
def admin_assignments_filter(request):
	if request.method=='POST':
		assignments=Assignment.objects.all()
		if request.POST.get('applicant'):
			applicants=User.objects.filter(first_name__icontains=request.POST.get('applicant'),
				last_name__icontains=request.POST.get('applicant'))
			assignments=assignments.filter(user__in=applicants)
		if request.POST.get('exam-name'):
			exams=Exam.objects.filter(name__icontains=request.POST.get('exam-name'))
			assignments=assignments.filter(exam__in=exams)
		if request.POST.get('status'):
			assignments=assignments.filter(status=request.POST.get('status'))
		if request.POST.get('score'):
			assignments=assignments.filter(score = request.POST.get('score'))
		if request.POST.get('exam-result'):
			assignments=assignments.filter(exam_status=request.POST.get('exam-result'))
		assignments=list(assignments.values('user__first_name','user__last_name','exam__name','score','status','exam_status'))
		return JsonResponse({'assignments':assignments})

@login_required
def admin_applicants_list(request):
	if request.method=='GET':
		applicant_list=User.objects.exclude(groups__name ='company_admin')
		groups=Group.objects.all()
		context={
		'applicant_list':applicant_list,
		'groups':groups
		}
		return render(request,'exam/admin_applicants.html',context=context)
	return redirect('exam:index')

@login_required
def admin_applicant_create(request):
	# instance= get_object_or_404(Exam, id=id)
	# print(instance)
	if request.method=='GET':
		applicant_form=ApplicantForm()
		return render(request,'exam/admin_applicant_create.html',{'applicant_form':applicant_form})
	if request.method=="POST":
		applicant_form=ApplicantForm(request.POST)
		if applicant_form.is_valid():
			user_obj=applicant_form.save(commit=False)
			user_obj.email=request.POST.get('email').lower()
			user_obj.set_password(applicant_form.cleaned_data.get('password'))
			user_obj.save()
			messages.success(request, 'Applicant Created Successfully.')
			return render(request,'exam/admin_applicant_create.html',{'applicant_form':applicant_form})
		return render(request,'exam/admin_applicant_create.html',{'applicant_form':applicant_form})
	return redirect('exam:admin-applicants')

@login_required
def admin_applicant_update(request):
	instance=User.objects.get(email=request.GET.get('email'))
	if request.method=='GET':
		applicant_form=AdminUpdateProfileForm(instance=instance)
		assignment_list=Assignment.objects.filter(user=instance)
		context={
		'assignment_list':assignment_list,
		'applicant_form':applicant_form,
		}
		return render(request,'exam/admin_applicant_update.html',context=context)
	elif request.method=='POST':
		applicant_form=AdminUpdateProfileForm(request.POST,instance=instance)
		if applicant_form.is_valid():
			user_obj=applicant_form.save(commit=False)
			user_obj.email=request.POST.get('email').lower()
			user_obj.save()
			messages.success(request, 'Applicant Updated Successfully.')
			return render(request,'exam/admin_applicant_update.html',{'applicant_form':applicant_form,})
		return render(request,'exam/admin_applicant_update.html',{'applicant_form':applicant_form})
	return redirect('exam:admin-applicants')
@login_required
def admin_applicant_delete(request):
	if request.method=='POST':
		data_applicant_id=request.POST.get('data_applicant_id')
		applicant_obj=User.objects.get(id=data_applicant_id)
		applicant_obj.delete()
		messages.success(request, 'Applicant deleted Successfully.')
		return JsonResponse({"message":"Successfully Deleted"})
	return redirect('exam:admin-applicants')
@login_required
def admin_applicants_filter(request):
	if request.method=='POST':
		applicants=User.objects.all()
		if request.POST.get('email'):
			applicants=applicants.filter(email__icontains=request.POST.get('email'))
		if request.POST.get('first-name'):
			applicants=applicants.filter(first_name__icontains=request.POST.get('first-name'))
		if request.POST.get('last-name'):
			applicants=applicants.filter(last_name__icontains=request.POST.get('last-name'))
		if request.POST.get('group'):
			if request.POST.get('group')=='None':
				applicants=applicants.filter(groups = None)
			else:
				applicants=applicants.filter(groups = request.POST.get('group'))
		if request.POST.get('active'):
			applicants=applicants.filter(is_active=request.POST.get('active'))
		applicants=list(applicants.values('email','first_name','last_name','groups__name','is_active'))
		return JsonResponse({'applicants':applicants})


def register(request):
	if request.method=="GET":
		register_form=RegistrationForm()
		return render(request,'exam/register.html',{"register_form":register_form})
	elif request.method=='POST':
		register_form=RegistrationForm(request.POST)
		if register_form.is_valid():
			user_obj=register_form.save(commit=False)
			user_obj.email=request.POST.get('email').lower()
			user_obj.set_password(register_form.cleaned_data.get('password'))
			user_obj.save()
			return render(request,'exam/register.html',{"register_form":register_form,"success":True})
		return render(request,'exam/register.html',{"register_form":register_form})
	return redirect('/')
def login_user(request):
	login_form=LoginForm()
	if request.method=="POST" and request.POST.get('email') and request.POST.get('password'):
		email= request.POST.get('email').lower()
		raw_password = request.POST.get('password')
		login_form=LoginForm(request.POST)
		user_obj = authenticate(request,email=email, password=raw_password)
		if user_obj is not None:
			login(request,user_obj)
			return redirect('/')
		return render(request,'exam/login.html',{"login_form":login_form,'failure':True})
	else:
		return render(request,'exam/login.html',{"login_form":login_form})

def logout_user(request):
	logout(request)
	return redirect('/')
@login_required
def user_profile(request):
	if request.method == 'GET':
		user_form=UpdateProfileForm(instance=request.user)
		return render(request,'exam/user_profile.html',{'user_form':user_form})
	elif request.method == 'POST':
		user_form=UpdateProfileForm(request.POST,instance=request.user)
		if user_form.is_valid():
			user_obj=user_form.save(commit=False)
			user_obj.email=request.POST.get('email').lower()
			user_obj.save()
			return render(request,'exam/user_profile.html',{'user_form':user_form,"success":True})
		return render(request,'exam/user_profile.html',{'user_form':user_form})
	else:
		return render(request,'exam/user_profile.html',{'user_form':user_form})

