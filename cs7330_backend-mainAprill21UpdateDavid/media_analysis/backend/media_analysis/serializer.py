from rest_framework import serializers
from .models import *

class social_media_serializer(serializers.ModelSerializer):
    class Meta:
        model = Social_media
        fields = '__all__'


class user_serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class post_serializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class repost_serializer(serializers.ModelSerializer):
    class Meta:
        model = Repost
        fields = '__all__'

class institute_serializer(serializers.ModelSerializer):
    class Meta:
        model = Institute
        fields = '__all__'

class project_serializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class project_field_serializer(serializers.ModelSerializer):
    class Meta:
        model = Project_field
        fields = '__all__'

class project_post_serializer(serializers.ModelSerializer):
    class Meta:
        model = Project_post
        fields = '__all__'

class analysis_result_serializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis_result
        fields = '__all__'