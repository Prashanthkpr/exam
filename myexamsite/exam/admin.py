from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Answer)
admin.site.register(Exam)
admin.site.register(AnswerSheet)
admin.site.register(Assignment)
admin.site.register(Tag)
admin.site.register(Attachment)
admin.site.register(Attempt)




