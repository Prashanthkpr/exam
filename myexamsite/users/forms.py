from django import forms
from users.models import User

class DateInput(forms.DateInput):
    input_type = 'date'

class LoginForm(forms.ModelForm):
	password = forms.CharField(max_length=32, widget=forms.PasswordInput)
	def __init__(self, *args, **kwargs):
		super(LoginForm, self).__init__(*args, **kwargs)
		for field in self.fields:
			self.fields[field].widget.attrs["class"] = "form-control"
	class Meta:
		model = User
		fields = ('email','password')

class RegistrationForm(forms.ModelForm):
	password = forms.CharField(label='Password', widget=forms.PasswordInput)
	def __init__(self, *args, **kwargs):
		super(RegistrationForm, self).__init__(*args, **kwargs)
		for field in self.fields:
			self.fields[field].widget.attrs["class"] = "form-control"
			self.fields[field].required = True
			if field=='gender':
				self.fields[field].widget.attrs["class"] = "form-control selectpicker"
	class Meta:
		model = User
		fields = ('first_name','last_name','gender','email','date_of_birth','mobile','password')
		widgets = {
            'date_of_birth': DateInput(),
            }
	# def clean_password2(self):
	# 	password1 = self.cleaned_data.get("password1")
	# 	password2 = self.cleaned_data.get("password2")
	# 	if password1 and password2 and password1 != password2:
	# 		raise forms.ValidationError("Passwords don't match")
	# 		return password2

	# def save(self, commit=True):
 #    	# Save the provided password in hashed format
	#     user = super(RegistrationForm, self).save(commit=False)
	#     user.set_password(self.cleaned_data["password1"])
	#     if commit:
	#         user.save()
	#         return user
class UpdateProfileForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(UpdateProfileForm, self).__init__(*args, **kwargs)
		for field in self.fields:
			self.fields[field].widget.attrs["class"] = "form-control"
			if field=='gender':
				self.fields[field].widget.attrs["class"] = "form-control selectpicker"

	class Meta:
		model = User
		fields = ('first_name', 'last_name','email','gender','date_of_birth','mobile',)
		widgets = {
            'date_of_birth': DateInput(),
        }

