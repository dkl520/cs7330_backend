from django.db import models
from django.db.models import F, Q

# Create your models here.
class Social_media(models.Model):
    media_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        permissions = ()
        db_table = 'social_media'

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    media_id = models.ForeignKey(Social_media, on_delete=models.CASCADE, db_column='media_id')
    username = models.CharField(max_length=40)
    first_name = models.CharField(max_length=50, null=True, default=None)
    last_name = models.CharField(max_length=50, null=True, default=None)
    country_of_birth = models.CharField(max_length=50, null=True, default=None)
    country_of_residence = models.CharField(max_length=50, null=True, default=None)
    age = models.IntegerField(null=True, default=None)
    gender = models.CharField(max_length=20, null=True, default=None)
    is_verified =models.BooleanField(default=False)

    class Meta:
        permissions = ()
        db_table = 'user'
        constraints = [
            models.UniqueConstraint(fields=['media_id', 'username'], 
                                    name= 'unique_username_within_media')
        ]

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    media_id = models.ForeignKey(Social_media, on_delete=models.CASCADE, db_column='media_id')
    content = models.TextField()
    post_time = models.DateTimeField()
    location_city = models.CharField(max_length=50, null=True, default=None)
    location_state = models.CharField(max_length=50, null=True, default=None)
    location_country = models.CharField(max_length=50, null=True, default=None)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    has_multimedia = models.BooleanField(default=False)

    class Meta:
        permissions = ()
        db_table = 'post'
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'media_id', 'post_time'],
                                    name= 'one_post_one_time_a_user_within_a_media')
        ]

class Repost(models.Model):
    repost_id = models.AutoField(primary_key=True)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, db_column='post_id')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE,db_column='user_id')
    repost_time = models.DateTimeField()

    class Meta:
        permissions = ()
        db_table = 'repost'

class Institute(models.Model):
    institute_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        permissions = ()
        db_table = 'institute'

class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    manager_first_name = models.CharField(max_length=50)
    manager_last_name = models.CharField(max_length=50)
    institute_id = models.ForeignKey(Institute, on_delete=models.CASCADE, db_column='institute_id')
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        permissions = ()
        db_table = 'project'
        constraints = [
            models.CheckConstraint(check=Q(start_date__lte = F('end_date')),
                                   name='start_date_before_or_equal_end_date')
        ]

class Project_field(models.Model):
    field_id = models.AutoField(primary_key=True)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE, db_column='project_id')
    field_name = models.CharField(max_length=50)

    class Meta:
        permissions = ()
        db_table = 'project_field'
        constraints = [
            models.UniqueConstraint(fields=['project_id', 'field_name'],
                                    name='field_name_unique_within_project')
        ]

class Project_post(models.Model):
    project_post_id = models.AutoField(primary_key=True)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE, db_column='project_id')
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, db_column='post_id')

    class Meta:
        permissions = ()
        db_table = 'project_post'
        constraints = [
            models.UniqueConstraint(fields=['project_id', 'post_id'],
                                    name='over_analysis')
        ]

class Analysis_result(models.Model):
    result_id = models.AutoField(primary_key=True)
    project_post_id = models.ForeignKey(Project_post, on_delete=models.CASCADE, db_column='project_post_id')
    field_id = models.ForeignKey(Project_field, on_delete=models.CASCADE, db_column='field_id')
    value = models.CharField(max_length=255, null=True, default=None)

    class Meta:
        permissions = ()
        db_table = 'analysis_result'
        constraints = [
            models.UniqueConstraint(fields=['project_post_id', 'field_id'],
                                    name='one_result_for_one_post_with_a_field_within_a_project')
        ]
