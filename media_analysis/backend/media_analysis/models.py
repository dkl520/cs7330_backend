from django.db import models

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
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    country_of_birth = models.CharField(max_length=50, null=True)
    country_of_residence = models.CharField(max_length=50, null=True)
    age = models.IntegerField(null=True)
    gender = models.CharField(max_length=20, null=True)
    is_verified =models.BooleanField(default=False)

    class Meta:
        permissions = ()
        db_table = 'user'

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    media_id = models.ForeignKey(Social_media, on_delete=models.CASCADE, db_column='media_id')
    content = models.TextField()
    post_time = models.DateTimeField()
    location_city = models.CharField(max_length=50, null=True)
    location_state = models.CharField(max_length=50, null=True)
    location_country = models.CharField(max_length=50, null=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    has_multimedia = models.BooleanField(default=False)

    class Meta:
        permissions = ()
        db_table = 'post'

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

class Project_field(models.Model):
    field_id = models.AutoField(primary_key=True)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE, db_column='project_id')
    field_name = models.CharField(max_length=50)

    class Meta:
        permissions = ()
        db_table = 'project_field'

class Project_post(models.Model):
    project_post_id = models.AutoField(primary_key=True)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE, db_column='project_id')
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, db_column='post_id')

    class Meta:
        permissions = ()
        db_table = 'project_post'

class Analysis_result(models.Model):
    result_id = models.AutoField(primary_key=True)
    project_post_id = models.ForeignKey(Project_post, on_delete=models.CASCADE, db_column='project_post_id')
    field_id = models.ForeignKey(Project_field, on_delete=models.CASCADE, db_column='field_id')
    value = models.CharField(max_length=255)

    class Meta:
        permissions = ()
        db_table = 'analysis_result'
