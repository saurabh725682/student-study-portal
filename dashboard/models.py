from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# Creating model for notes..
class Notes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField() 
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "notes"
        verbose_name_plural = "notes"

# Creating model for homework..
class Homework(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50)
    title = models.CharField(max_length=100)
    description = models.TextField()
    due = models.DateTimeField()
    is_finished= models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
# Creating model for todo..
class Todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000)
    is_finished = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    

    
    
    
    
    
    








































