from django.db import models
from users.models import User
from django.template.defaultfilters import slugify
from django.core.validators import FileExtensionValidator
from django.conf import settings

# Create your models here.

class Attachment(models.Model):
    ''' attachment for question '''
    name = models.CharField(max_length=50)
    attachment = models.FileField(upload_to = 'question/pictures',validators=[FileExtensionValidator(allowed_extensions=['pdf','jpg','jpeg','gif','tiff','exiff','odt','png','doc','docx','txt'])])
    description = models.TextField(blank=True,null=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    ''' Tags for question '''
    name = models.CharField(max_length=50,unique=True)
    name_slug =  models.CharField(max_length=50,blank=True,null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name_slug = slugify(self.name) # set the slug explicitly
        super(Tag, self).save(*args, **kwargs) # call Django's save()

class Question(models.Model):
    ''' create question for exam '''
    question_choice = (
        ('choice','Choice'),
        ('text','Text'),
        ('program','Program'),
        )
    question_type = models.CharField(max_length=10,choices=question_choice,default='choice')
    name_slug = models.CharField(max_length=50,blank=True,null=True)
    question_text = models.TextField(blank=False ,unique = True)
    hint = models.CharField(max_length=50,blank=True,null=True)
    pub_date = models.DateTimeField('date published',blank=True,null=True)
    attachments = models.ManyToManyField(Attachment,blank=True)
    tags = models.ManyToManyField(Tag,blank=True)
    answer = models.ForeignKey('exam.Choice',on_delete=models.CASCADE,related_name='answer',blank=True,null=True)

    def __str__(self):
        return self.question_text

    # def save(self, *args, **kwargs):
    #     self.name_slug = slugify(self.name) # set the slug explicitly
    #     super(Question, self).save(*args, **kwargs) # call Django's save()

class Choice(models.Model):
    ''' Choices for question,if question type is choice

    '''
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    name_slug = models.CharField(max_length=50)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
    def save(self, *args, **kwargs):
        self.name_slug = slugify(self.choice_text) # set the slug explicitly
        super(Choice, self).save(*args, **kwargs) # call Django's save()

class Answer(models.Model):
    ''' Answer for question, if question type is text.'''
    question = models.ForeignKey('exam.Question',on_delete=models.CASCADE,related_name='answertext')
    answer = models.TextField(default=None)
    name_slug = models.CharField(max_length=50,blank=True,null=True)

    def __str__(self):
        return str(self.question)

class Exam(models.Model):
    '''create exam for applicant assignment'''
    name = models.CharField(max_length=100,blank = False,unique=True)
    name_slug = models.CharField(max_length=100)
    question_paper = models.ManyToManyField(Question)
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name_slug = slugify(self.name) # set the slug explicitly
        super(Exam, self).save(*args, **kwargs) # call Django's save()

class AnswerSheet(models.Model):
    '''Answer sheet  to store the applicant answers'''
    assignment=models.ForeignKey('exam.Assignment',on_delete=models.CASCADE,blank=True,null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    question = models.ForeignKey(Question,on_delete=models.CASCADE)
    answer = models.ForeignKey(Choice,on_delete=models.CASCADE,blank=True,null=True)
    exam = models.ForeignKey(Exam,on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True,null=True)

    def __str__(self):
        return str(self.user)+"------"+str(self.exam)+"----"+str(self.question)

class Attempt(models.Model):
    '''Applicant attempts to write the exam'''

    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True,null=True)
    duration = models.FloatField(blank=True,null=True,help_text='Duration in seconds')

    def __str__(self):

        return str(self.start_time)
class Assignment(models.Model):
    """ create assignment for applicant"""
    PENDING = 'pending'
    ABORTED = 'aborted'
    FINISHED = 'finished'
    TIMEOUT = 'timeout'

    PASS = 'pass'
    FAIL = 'fail'
    STATUS_CHOICE = (
        (PENDING,'Pending'),
        (ABORTED,'Aborted'),
        (FINISHED,'Finished'),
        (TIMEOUT,'Timeout'),
        )
    EXAM_CHOICE= (
        (PASS,'Pass'),
        (FAIL,'Fail'),
        )

    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam,on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    status = models.CharField(max_length=10,choices=STATUS_CHOICE,default=PENDING)
    exam_status = models.CharField(max_length=10,choices=EXAM_CHOICE,default=None,blank=True,null=True)
    name_slug = models.CharField(max_length=50,blank=True,null=True)
    attempts = models.ManyToManyField(Attempt,blank=True)
    duration = models.FloatField(help_text='Duration in seconds')


    def __str__(self):
        return str(self.user)+" "+str(self.exam)

