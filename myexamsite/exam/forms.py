from exam.models import *
from users.models import *
from django import forms
from django.forms import formset_factory,modelformset_factory,inlineformset_factory
from django.forms import BaseFormSet,BaseInlineFormSet,BaseModelFormSet

class DateInput(forms.DateInput):
    input_type = 'date'

class ExamForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super(ExamForm, self).__init__(*args, **kwargs)
		for field in self.fields:
			self.fields[field].widget.attrs["class"] = "form-control"
			if field=='question_paper':
				self.fields[field].widget.attrs["class"] = "form-control selectpicker"

	class Meta:
		model=Exam
		fields=('name','question_paper')
		labels = {
			'Exam Name':'name',
            'Select Questions': 'question_paper',
            }

class QuestionForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(QuestionForm, self).__init__(*args, **kwargs)
		for field in self.fields:
			self.fields[field].widget.attrs["class"] = "form-control"
			if field=='question_type':
				self.fields[field].widget.attrs["class"] = "form-control selectpicker"
			if field=='hint':
				self.fields[field].widget.attrs["class"] = "form-control"
			if field=='question_text':
				self.fields[field].widget.attrs["placeholder"] = "Enter your question here"
				self.fields[field].widget.attrs["class"] = "form-control"
				self.fields[field].widget.attrs["rows"] = "auto"
	class Meta:
		model=Question
		fields=('question_type','question_text','hint',)

class AssignmentForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(AssignmentForm, self).__init__(*args, **kwargs)
		for field in self.fields:
			self.fields[field].widget.attrs["class"] = "form-control"
			if field=='user' or field=='exam':
				self.fields[field].widget.attrs["class"] = "form-control selectpicker"
			if field=='duration':
				self.fields[field].widget.attrs["placeholder"] = "Enter duration in seconds"
		self.fields['user'].queryset = User.objects.filter(groups__name='applicant')
	class Meta:
		model=Assignment
		fields=('user','exam','duration')
		labels={
		'Applicant Name':'user',
		'Select Exam ' :'exam',
		'Duration' :'duration',
		}


class AssignmentUpdationForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(AssignmentUpdationForm, self).__init__(*args, **kwargs)
		for field in self.fields:
			self.fields[field].widget.attrs["class"] = "form-control"
			if field=='user' or field=='exam'or field=='status' or field=='exam_status':
				self.fields[field].widget.attrs["class"] = "form-control selectpicker"
			if field=='duration':
				self.fields[field].widget.attrs["placeholder"] = "Enter duration in seconds"
		self.fields['user'].queryset = User.objects.filter(groups__name='applicant')
	class Meta:
		model=Assignment
		fields=('user','exam','duration','score','status','exam_status',)
		widgets = {
    				'region': forms.ChoiceField(
        widget=forms.Select(attrs={'class':'bootstrap-select'})
    ),
					}
		# labels={
		# 'Applicant Name':'user',
		# 'Select Exam ' :'exam',
		# 'Duration' :'duration',
		# 'Score ':'score',
		# 'Status':'status',
		# 'Result':'exam_status',
		# }
class ApplicantForm(forms.ModelForm):
	password = forms.CharField(max_length=32, widget=forms.PasswordInput)
	def __init__(self, *args, **kwargs):
		super(ApplicantForm, self).__init__(*args, **kwargs)
		for field in self.fields:
			self.fields[field].widget.attrs["class"] = "form-control"
			self.fields[field].required = True
			if field=='groups' or field=='gender':
				self.fields[field].widget.attrs["class"] = "form-control selectpicker"
	class Meta:
		model = User
		fields = ('first_name','last_name','gender','email','date_of_birth','mobile','password','is_active','groups')
		widgets = {
            'date_of_birth': DateInput(),
            }

class AdminUpdateProfileForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(AdminUpdateProfileForm, self).__init__(*args, **kwargs)
		for field in self.fields:
			self.fields[field].widget.attrs["class"] = "form-control"
			if field =='is_active':
				self.fields[field].widget.attrs['type']= "radio"
			if field=='groups' or field=='gender':
				self.fields[field].widget.attrs["class"] = "form-control selectpicker"

	class Meta:
		model = User
		fields = ('first_name','last_name','gender','email','date_of_birth','mobile','is_active','groups')
		widgets = {
            'date_of_birth': DateInput(),
            }

class ChoiceForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super(ChoiceForm, self).__init__(*args, **kwargs)
		for field in self.fields:
			self.fields[field].widget.attrs["class"] = "form-control"

	class Meta:
		model=Choice
		fields=('choice_text',)

class BaseChoiceFormSet(BaseFormSet):
     def clean(self):
        """Checks that no two choices have the same values."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        choices = []
        for form in self.forms:
        	choice=''
        	try:
	        	choice = form.cleaned_data['choice_text']
	        except:
	        	raise forms.ValidationError("Choice could not be empty")
	        else:
	        	if choice in choices:
	        		raise forms.ValidationError("Choice must have distinct values.")
	        	choices.append(choice)

class BaseChoiceUpdationFormSet(BaseInlineFormSet):
     def clean(self):
        """Checks that no two choices have the same values."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        choices = []
        for form in self.forms:
        	choice=''
        	try:
	        	choice = form.cleaned_data['choice_text']
	        except:
	        	raise forms.ValidationError("Choice could not be empty")
	        else:
	        	if choice in choices:
	        		raise forms.ValidationError("Choice must have distinct values.")
	        	choices.append(choice)
ChoiceFormSet = formset_factory(ChoiceForm,extra=0,min_num=4,max_num=6,validate_min=True, validate_max=True,can_delete=True,formset=BaseChoiceFormSet)
ChoiceUpdationFormSet=inlineformset_factory(Question,Choice,fields=('choice_text',),extra=0,min_num=4,max_num=6,validate_min=True, validate_max=True,can_delete=True,formset=BaseChoiceUpdationFormSet)

class AnswerForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super(AnswerForm, self).__init__(*args, **kwargs)
		for field in self.fields:
			if field=='answer':
				self.fields[field].widget.attrs["placeholder"] = "Enter your answer here"
				self.fields[field].widget.attrs["class"] = "form-control"
				self.fields[field].widget.attrs["rows"] = "auto"
	class Meta:
		model=Answer
		fields=('answer',)

class AttachmentForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super(AttachmentForm, self).__init__(*args, **kwargs)
		for field in self.fields:
			if field=='name':
				self.fields[field].widget.attrs["class"] = "form-control"
			if field=='description':
				self.fields[field].widget.attrs["placeholder"] = "Enter your description here"
				self.fields[field].widget.attrs["class"] = "form-control"
				self.fields[field].widget.attrs["rows"] = "auto"
	class Meta:
		model=Attachment
		fields=('name','attachment','description')

class BaseAttachmentFormSet(BaseFormSet):
     def clean(self):
        """Checks that no two choices have the same values."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        for form in self.forms:

	        if form.cleaned_data.get('name') is None and form.cleaned_data.get('attachment') is None:
	        	raise forms.ValidationError("Form is empty")
class BaseAttachmentUpdateFormSet(BaseModelFormSet):
     def clean(self):
        """Checks that no two choices have the same values."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        for form in self.forms:

	        if form.cleaned_data.get('name') is None and form.cleaned_data.get('attachment') is None:
	        	raise forms.ValidationError("Form is empty")

AttachmentFormSet = formset_factory(AttachmentForm,extra=1,min_num=0,max_num=3,validate_min=True,validate_max=True,can_delete=False,formset=BaseAttachmentFormSet)
AttachmentUpadateFormSet = modelformset_factory(Attachment,AttachmentForm,exclude=('id',),extra=0,min_num=0,max_num=3,validate_max=True,can_delete=False,formset=BaseAttachmentUpdateFormSet)


# class VariantForm(forms.ModelForm):
# 	def __init__(self, *args, **kwargs):
# 		super(VariantForm, self).__init__(*args, **kwargs)
# 		self.fields['item'].widget = forms.HiddenInput()
# 		self.fields['item'].label = ''
# 		for field in self.fields:
# 			self.fields[field].widget.attrs["class"] = "form-control"
# 		if field == 'sku_code':
# 			self.fields[field].widget.attrs["placeholder"] = "SKU Code"
# 			self.fields[field].required = True
# 			continue
# 			self.fields[field].widget.attrs["placeholder"] = field.capitalize()

# 	class Meta:
# 	model = Variant
# 	fields = '__all__'

# gender_choices = (
#         ('male','Male'),
#         ('female','Female'),
#         ('others','Others'),
#         )