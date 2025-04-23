"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from media_analysis.views import *#PostView, ExperimentView, social_media_create_view, user_create_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/query/post/', PostView.as_view()),
    path('api/query/experiment/', ExperimentView.as_view()),

    # path('api/query/media/create/', social_media_create_view),
    # path('api/query/User/create/', user_create_view),
    # path('api/query/Post/create/', post_create_view),
    # path('api/query/repost/create/', repost_create_view),
    # path('api/query/institute/create/', institute_create_view),
    # path('api/query/Project/create/', project_form_create_view),
    # path('api/query/ProjectField/create/', project_field_create_view),
    # path('api/query/ProjectPost/create/', project_post_create_view),
    # path('api/query/AnalysisResult/create/', analysis_result_create_view),


    #  path('api/query/media/list/', social_media_list_view),
    # path('api/query/User/list/', user_list_view),
    # path('api/query/Post/list/', post_list_view),
    # path('api/query/repost/list/', repost_list_view),
    # path('api/query/institute/list/', institute_list_view),
    # path('api/query/Project/list/', project_form_list_view),
    # path('api/query/ProjectField/list/', project_field_list_view),
    # path('api/query/ProjectPost/list/', project_post_list_view),
    # path('api/query/AnalysisResult/list/', analysis_result_list_view),
    

    # path('media/<id>/update', social_media_update_view ),
    # path('User/<id>/update', user_update_view ),
    # path('Post/<id>/update', post_update_view ),
    # path('repost/<id>/update', repost_update_view ),
    # path('institute/<id>/update', institute_update_view ),
    # path('Project/<id>/update', project_update_view ),
    # path('ProjectField/<id>/update', project_field_update_view ),
    # path('ProjectPost/<id>/update', project_post_update_view ),
    # path('AnalysisResult/<id>/update', analysis_result_update_view ),




    # path('media/<id>/delete', social_media_delete_view ),
    # path('User/<id>/delete', user_delete_view ),
    # path('Post/<id>/delete', post_delete_view ),
    # path('repost/<id>/delete', repost_delete_view ),
    # path('institute/<id>/delete', institute_delete_view ),
    # path('Project/<id>/delete', project_delete_view ),
    # path('ProjectField/<id>/delete', project_field_delete_view ),
    # path('ProjectPost/<id>/delete', project_post_delete_view ),
    # path('AnalysisResult/<id>/delete', analysis_result_delete_view ),

    #api calls
    path('api/media', get_social_media, name='get_social_media'),
    path('api/media/create', create_social_media, name='create_social_media'),
    path('api/media/<int:pk>', social_media_detail, name='social_media_detail'),

    path('api/user', get_user, name='get_user'),
    path('api/user/create', create_user, name='create_user'),
    path('api/user/<int:pk>', user_detail, name='user_detail'),


    path('api/post', get_post, name='get_post'),

    path('api/get_available_posts', get_available_posts, name='get_available_posts'),
    path('api/post/create', create_post, name='create_post'),
    path('api/post/<int:pk>', post_detail, name='post_detail'),



    path('api/repost', get_repost, name='get_repost'),
    path('api/repost/create', create_repost, name='create_repost'),
    path('api/repost/bulk_repost', bulk_repost, name='bulk_repost'),
    path('api/repost/<int:pk>', repost_detail, name='repost_detail'),

    path('api/institute', get_institute, name='get_institute'),
    path('api/institute/create', create_institute, name='create_institute'),
    path('api/institute/<int:pk>', institute_detail, name='institute_detail'),

    path('api/project', get_project, name='get_project'),
    path('api/project/create', create_project, name='create_project'),
    path('api/project/<int:pk>', project_detail, name='project_detail'),

    path('api/project_post', get_project_post, name='get_project_post'),
    path('api/project_post/create', create_project_post, name='create_project_post'),
    path('api/project_post/<int:pk>', project_post_detail, name='project_post_detail'),


    path('api/analysis_result', get_analysis_result, name='get_anaysis_result'),
    path('api/analysis_result/create', create_analysis_result, name='create_analysis_result'),
    path('api/analysis_result/<int:pk>', analysis_result_detail, name='analysis_result_detail'),

]
