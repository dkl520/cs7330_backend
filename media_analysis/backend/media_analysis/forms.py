from django import forms
from .models import Social_media, User, Post, Repost, Institute, Project, Project_field, Project_post, Analysis_result


# creating a form for Social media table
class Social_media_Form(forms.ModelForm):

    # create meta class
    class Meta:
        # specify model to be used
        model = Social_media

        # specify fields to be used
        fields = [
            "media_id",
            "name",
        ]


class User_Form(forms.ModelForm):

    # create meta class
    class Meta:
        # specify model to be used
        model = User

        # specify fields to be used
        fields = [
            "user_id",
            "media_id",
            "username",
            "first_name",
            "last_name",
            "country_of_birth",
            "country_of_residence",
            "age",
            "gender",
            "is_verified"
        ]
  
   

class Post_Form(forms.ModelForm):

    # create meta class
    class Meta:
        # specify model to be used
        model = Post

        # specify fields to be used
        fields = [
            "post_id",
            "user_id",
            "media_id",
            "content",
            "post_time",
            "location_city",
            "location_state",
            "location_country",
            "likes",
            "dislikes",
            "has_multimedia"

        ]
    

class Repost_Form(forms.ModelForm):
    # create meta class
    class Meta:
        # specify model to be used
        model = Repost

        # specify fields to be used
        fields = [
            "repost_id",
            "post_id",
            "user_id",
            "repost_time",
        ]

class Institute_Form(forms.ModelForm):

    # create meta class
        class Meta:
        # specify model to be used
            model = Institute

        # specify fields to be used
            fields = [
                "institute_id",
                "name"
            ]
class Project_Form(forms.ModelForm):

    # create meta class
        class Meta:
        # specify model to be used
            model = Project

        # specify fields to be used
            fields = [
                "project_id",
                "name",
                "manager_first_name",
                "manager_last_name",
                "institute_id",
                "start_date",
                "end_date"
            ]

class Project_field_Form(forms.ModelForm):

    # create meta class
        class Meta:
        # specify model to be used
            model = Project_field

        # specify fields to be used
            fields = [
                "field_id",
                "project_id",
                "field_name"
            ]

class Project_post_Form(forms.ModelForm):

    # create meta class
        class Meta:
        # specify model to be used
            model = Project_post

        # specify fields to be used
            fields = [
                "project_post_id",
                "project_id",
                "post_id"
            ]

class Analysis_result_Form(forms.ModelForm):

    # create meta class
        class Meta:
        # specify model to be used
            model = Analysis_result

        # specify fields to be used
            fields = [
                "result_id",
                "project_post_id",
                "field_id",
                "value"
            ]


