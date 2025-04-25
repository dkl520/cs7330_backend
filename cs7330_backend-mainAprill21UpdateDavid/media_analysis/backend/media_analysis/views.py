from django.db import transaction
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializer import *

from django.db.models import Value, Q, Prefetch
from django.db.models.functions import Concat
from .models import *  # Post, Project_post, Social_media
from .forms import Social_media_Form, User_Form, Post_Form, Repost_Form, Institute_Form, Project_Form, \
    Project_field_Form, Project_post_Form, Analysis_result_Form
from datetime import datetime
from collections import defaultdict
from django.shortcuts import (get_object_or_404,
                              render,
                              HttpResponseRedirect)
import json


# Post query
class PostView(APIView):
    def get(self, request):
        # 参数改成 media_id
        media_id = request.GET.get('media_id')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        username = request.GET.get('username')
        author = request.GET.get('author')

        posts = (
            Post.objects
            .select_related('user_id', 'media_id')
            .prefetch_related('project_post_set__project_id')
        )

        # ── 1) 按 media_id 过滤 ────────────────────────────────
        if media_id:  # 可能是 "3" 这样的字符串
            posts = posts.filter(media_id=media_id)

        # ── 2) 其他条件保持不变 ────────────────────────────────
        if start_date and end_date:
            start_date = datetime.strptime(start_date, "%m/%d/%Y").date()
            end_date = datetime.strptime(end_date, "%m/%d/%Y").date()
            posts = posts.filter(post_time__range=[start_date, end_date])

        if username:
            posts = posts.filter(user_id__username=username)

        if author:
            posts = posts.annotate(
                fullname=Concat('user_id__first_name', Value(' '), 'user_id__last_name')
            ).filter(
                Q(user_id__first_name__icontains=author) |
                Q(user_id__last_name__icontains=author) |
                Q(fullname__icontains=author)
            )

        # ── 3) 组装返回数据 ──────────────────────────────────
        result = []
        for post in posts:
            experiments = [pp.project_id.name for pp in post.project_post_set.all()]
            result.append({
                'post_id': post.post_id,
                'content': post.content,
                'media': post.media_id.name,  # 仍然返回平台名称，更友好
                'media_id': post.media_id_id,  # 如需同时返回 id，可加这一行
                'username': post.user_id.username,
                'time': post.post_time.strftime("%Y-%m-%d %H:%M"),
                'experiments': tuple(experiments),
            })
        return Response(result)


# experiment query
class ExperimentView(APIView):
    def get(self, request):
        name = request.GET.get('name')

        posts = Project_post.objects.select_related('post_id', 'project_id').prefetch_related(
            'analysis_result_set__field_id')
        # query by project name
        if name:
            posts = posts.filter(project_id__name=name)

        post_result = []
        field_result = []

        for post in posts:
            value = [a.value for a in post.analysis_result_set.all()]
            field = [a.field_id.field_name for a in post.analysis_result_set.all()]
            field_result += field
            post_result.append({
                'post_id': post.post_id.post_id,
                'username': post.post_id.user_id.username,
                'media': post.post_id.media_id.name,
                'content': post.post_id.content,
                'time': post.post_id.post_time.strftime("%Y-%m-%d %H:%M"),
                'city': post.post_id.location_city,
                'state': post.post_id.location_state,
                'country': post.post_id.location_country,
                'likes': post.post_id.likes,
                'dislikes': post.post_id.dislikes,
                'has_multimedia': post.post_id.has_multimedia,
                'field': field,
                'value': value,

            })

        # count for field percentage
        counter = {}
        for f in field_result:
            counter[f] = counter.get(f, 0) + 1
        total = len(posts)
        percentages = {k: round((v / total) * 100, 2) for k, v in counter.items()}

        result = {
            'posts': post_result,
            'percentages': percentages,
        }
        return Response(result)


# for 7330 student
from collections import defaultdict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Project_post


class AdvancedView(APIView):
    def get(self, request):
        post_id_param = request.GET.get('post_id')

        # ✅ 参数校验
        if not post_id_param:
            return Response({'error': 'post_id 参数不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            post_id_list = post_id_param.split(',')
        except Exception:
            return Response({'error': 'post_id 参数格式错误，应为逗号分隔的整数列表'},
                            status=status.HTTP_400_BAD_REQUEST)

        # ✅ 获取所有包含这些 post_id 的 Project_post 对象
        posts = (Project_post.objects
                 .select_related('post_id', 'project_id')
                 .prefetch_related('analysis_result_set__field_id')
                 .filter(post_id__post_id__in=post_id_list))

        project_name_set = set()  # 用于去重
        project_result = []

        for project_post in posts:
            project = project_post.project_id
            if project.name in project_name_set:
                continue  # 已处理该项目，跳过

            project_name_set.add(project.name)
            qs = posts.filter(project_id=project)

            fields = []
            field_result = []
            field_dict = {}

            for post in qs:
                analysis_set = post.analysis_result_set.all()
                if not analysis_set:
                    continue  # 没有分析结果，跳过该 post

                value = [a.value for a in analysis_set]
                field = [a.field_id.field_name for a in analysis_set]
                field_id = [a.field_id.field_id for a in analysis_set]

                if not field_id:
                    continue  # 空字段，继续

                field_result.extend(field)
                for fid, fn, v in zip(field_id, field, value):
                        field_dict[fid] = fn
                        fields.append({
                            'post_id': post.post_id.post_id,
                            'field_id': fid,
                            'value': v,
                        })

            # ✅ 字段统计百分比
            counter = {}
            for f in field_result:
                counter[f] = counter.get(f, 0) + 1
            total = len(qs)
            if total == 0:
                continue  # 避免除以 0

            percentages = {k: round((v / total) * 100, 2) for k, v in counter.items()}

            # ✅ 分组结果
            grouped = defaultdict(list)
            for item in fields:
                fid_list = item['field_id']
                val_list = item['value']
                if not fid_list or not val_list:
                    continue
                grouped[fid_list].append({
                    'post_id': item['post_id'],
                    'value': val_list
                })

            formatted_fields = []
            for fid, record in grouped.items():
                field_name = field_dict.get(fid, '未知字段')
                percentage = percentages.get(field_name, 0)
                formatted_fields.append({
                    'field_id': fid,
                    'field_name': field_name,
                    'percentage': percentage,
                    'result': record
                })

            project_result.append({
                'project_id': project.project_id,
                'project_name': project.name,
                'fields': formatted_fields,
            })
        
        return Response(project_result)


# #--------
# #social media crud

# def social_media_create_view(request):
#     # dictionary for initial data with
#     # field names as keys
#     context = {}

#     # add the dictionary during initialization
#     form = Social_media_Form(request.POST or None)
#     if form.is_valid():
#         form.save()

#     context['form'] = form
#     return render(request, "create_view.html", context)

# def social_media_list_view(request):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # add the dictionary during initialization
#     context["dataset"] = Social_media.objects.all()

#     return render(request, "list.html", context)


# def social_media_update_view(request, id):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # fetch the object related to passed id
#     obj = get_object_or_404(Social_media, media_id = id)

#     # pass the object as instance in form
#     form = Social_media_Form(request.POST or None, instance = obj)

#     # save the data from the form and
#     # redirect to detail_view
#     if form.is_valid():
#         form.save()
#         return HttpResponseRedirect("/"+id)

#     # add form dictionary to context
#     context["form"] = form

#     return render(request, "update.html", context)


# def social_media_delete_view(request, id):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # fetch the object related to passed id
#     obj = get_object_or_404(Social_media, media_id = id)


#     if request.method =="POST":
#         # delete object
#         obj.delete()
#         # after deleting redirect to 
#         # home page
#         return HttpResponseRedirect("/")

#     return render(request, "delete.html", context)


# #user ---------------------------------
# def user_create_view(request):
#     # dictionary for initial data with
#     # field names as keys
#     context = {}

#     # add the dictionary during initialization
#     form = User_Form(request.POST or None)
#     if form.is_valid():
#         form.save()

#     context['form'] = form
#     return render(request, "create_view.html", context)

# def user_list_view(request):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # add the dictionary during initialization
#     context["dataset"] = User.objects.all()

#     return render(request, "list.html", context)


# def user_update_view(request, id):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # fetch the object related to passed id
#     obj = get_object_or_404(User, user_id = id)

#     # pass the object as instance in form
#     form = User_Form(request.POST or None, instance = obj)

#     # save the data from the form and
#     # redirect to detail_view
#     if form.is_valid():
#         form.save()
#         return HttpResponseRedirect("/"+id)

#     # add form dictionary to context
#     context["form"] = form

#     return render(request, "update.html", context)


# def user_delete_view(request, id):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # fetch the object related to passed id
#     obj = get_object_or_404(User, user_id = id)


#     if request.method =="POST":
#         # delete object
#         obj.delete()
#         # after deleting redirect to 
#         # home page
#         return HttpResponseRedirect("/")

#     return render(request, "delete.html", context)


# #post-----------------------------------------------------
# def post_create_view(request):
#     # dictionary for initial data with
#     # field names as keys
#     context = {}

#     # add the dictionary during initialization
#     form = Post_Form(request.POST or None)
#     if form.is_valid():
#         form.save()

#     context['form'] = form
#     return render(request, "create_view.html", context)

# def post_list_view(request):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # add the dictionary during initialization
#     context["dataset"] = Post.objects.all()

#     return render(request, "list.html", context)


# def post_update_view(request, id):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # fetch the object related to passed id
#     obj = get_object_or_404(Post, post_id = id)

#     # pass the object as instance in form
#     form = Post_Form(request.POST or None, instance = obj)

#     # save the data from the form and
#     # redirect to detail_view
#     if form.is_valid():
#         form.save()
#         return HttpResponseRedirect("/"+id)

#     # add form dictionary to context
#     context["form"] = form

#     return render(request, "update.html", context)


# def post_delete_view(request, id):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # fetch the object related to passed id
#     obj = get_object_or_404(Post, post_id = id)


#     if request.method =="POST":
#         # delete object
#         obj.delete()
#         # after deleting redirect to 
#         # home page
#         return HttpResponseRedirect("/")

#     return render(request, "delete.html", context)


# #repost-----------------------------------------------
# def repost_create_view(request):
#     # dictionary for initial data with
#     # field names as keys
#     context = {}

#     # add the dictionary during initialization
#     form = Repost_Form(request.POST or None)
#     if form.is_valid():
#         form.save()

#     context['form'] = form
#     return render(request, "create_view.html", context)

# def repost_list_view(request):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # add the dictionary during initialization
#     context["dataset"] = Repost.objects.all()

#     return render(request, "list.html", context)


# def repost_update_view(request, id):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # fetch the object related to passed id
#     obj = get_object_or_404(Repost, repost_id = id)

#     # pass the object as instance in form
#     form = Repost_Form(request.POST or None, instance = obj)

#     # save the data from the form and
#     # redirect to detail_view
#     if form.is_valid():
#         form.save()
#         return HttpResponseRedirect("/"+id)

#     # add form dictionary to context
#     context["form"] = form

#     return render(request, "update.html", context)


# def repost_delete_view(request, id):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # fetch the object related to passed id
#     obj = get_object_or_404(Repost, repost_id = id)


#     if request.method =="POST":
#         # delete object
#         obj.delete()
#         # after deleting redirect to 
#         # home page
#         return HttpResponseRedirect("/")

#     return render(request, "delete.html", context)

# # def project_field_list_view(request):
# #     # dictionary for initial data with 
# #     # field names as keys
# #     context ={}

# #     # add the dictionary during initialization
# #     context["dataset"] = Repost.objects.all()

# #     return render(request, "list.html", context)


# #institute crud--------------------------------------
# def institute_create_view(request):
#     # dictionary for initial data with
#     # field names as keys
#     context = {}

#     # add the dictionary during initialization
#     form = Institute_Form(request.POST or None)
#     if form.is_valid():
#         form.save()

#     context['form'] = form
#     return render(request, "create_view.html", context)

# def institute_list_view(request):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # add the dictionary during initialization
#     context["dataset"] = Institute.objects.all()

#     return render(request, "list.html", context)


# def institute_update_view(request, id):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # fetch the object related to passed id
#     obj = get_object_or_404(Institute, institute_id = id)

#     # pass the object as instance in form
#     form = Institute_Form(request.POST or None, instance = obj)

#     # save the data from the form and
#     # redirect to detail_view
#     if form.is_valid():
#         form.save()
#         return HttpResponseRedirect("/"+id)

#     # add form dictionary to context
#     context["form"] = form

#     return render(request, "update.html", context)


# def institute_delete_view(request, id):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # fetch the object related to passed id
#     obj = get_object_or_404(Institute, institute_id = id)


#     if request.method =="POST":
#         # delete object
#         obj.delete()
#         # after deleting redirect to 
#         # home page
#         return HttpResponseRedirect("/")

#     return render(request, "delete.html", context)


# #project form ----------------------------------------
# def project_form_create_view(request):
#     # dictionary for initial data with
#     # field names as keys
#     context = {}

#     # add the dictionary during initialization
#     form = Project_Form(request.POST or None)
#     if form.is_valid():
#         form.save()

#     context['form'] = form
#     return render(request, "create_view.html", context)

# def project_form_list_view(request):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # add the dictionary during initialization
#     context["dataset"] = Project_Form.objects.all()

#     return render(request, "list.html", context)


# def project_update_view(request, id):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # fetch the object related to passed id
#     obj = get_object_or_404(Project, project_id = id)

#     # pass the object as instance in form
#     form = Project_Form(request.POST or None, instance = obj)

#     # save the data from the form and
#     # redirect to detail_view
#     if form.is_valid():
#         form.save()
#         return HttpResponseRedirect("/"+id)

#     # add form dictionary to context
#     context["form"] = form

#     return render(request, "update.html", context)


# def project_delete_view(request, id):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # fetch the object related to passed id
#     obj = get_object_or_404(Project, project_id = id)


#     if request.method =="POST":
#         # delete object
#         obj.delete()
#         # after deleting redirect to 
#         # home page
#         return HttpResponseRedirect("/")

#     return render(request, "delete.html", context)


# #project field--------------------------------------------------
# def project_field_create_view(request):
#     # dictionary for initial data with
#     # field names as keys
#     context = {}

#     # add the dictionary during initialization
#     form = Project_field_Form(request.POST or None)
#     if form.is_valid():
#         form.save()

#     context['form'] = form
#     return render(request, "create_view.html", context)

# def project_field_list_view(request):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # add the dictionary during initialization
#     context["dataset"] = Project_field.objects.all()

#     return render(request, "list.html", context)


# def project_field_update_view(request, id):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # fetch the object related to passed id
#     obj = get_object_or_404(Project_field, field_id = id)

#     # pass the object as instance in form
#     form = Project_field_Form(request.POST or None, instance = obj)

#     # save the data from the form and
#     # redirect to detail_view
#     if form.is_valid():
#         form.save()
#         return HttpResponseRedirect("/"+id)

#     # add form dictionary to context
#     context["form"] = form

#     return render(request, "update.html", context)


# def project_field_delete_view(request, id):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # fetch the object related to passed id
#     obj = get_object_or_404(Project_field, field_id = id)


#     if request.method =="POST":
#         # delete object
#         obj.delete()
#         # after deleting redirect to 
#         # home page
#         return HttpResponseRedirect("/")

#     return render(request, "delete.html", context)


# #project Post-------------------------------------
# def project_post_create_view(request):
#     # dictionary for initial data with
#     # field names as keys
#     context = {}

#     # add the dictionary during initialization
#     form = Project_post_Form(request.POST or None)
#     if form.is_valid():
#         form.save()

#     context['form'] = form
#     return render(request, "create_view.html", context)

# def project_post_list_view(request):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # add the dictionary during initialization
#     context["dataset"] = Project_post.objects.all()

#     return render(request, "list.html", context)


# def project_post_update_view(request, id):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # fetch the object related to passed id
#     obj = get_object_or_404(Project_post, project_post_id = id)

#     # pass the object as instance in form
#     form = Project_post_Form(request.POST or None, instance = obj)

#     # save the data from the form and
#     # redirect to detail_view
#     if form.is_valid():
#         form.save()
#         return HttpResponseRedirect("/"+id)

#     # add form dictionary to context
#     context["form"] = form

#     return render(request, "update.html", context)


# def project_post_delete_view(request, id):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # fetch the object related to passed id
#     obj = get_object_or_404(Project_post, project_post_id = id)


#     if request.method =="POST":
#         # delete object
#         obj.delete()
#         # after deleting redirect to 
#         # home page
#         return HttpResponseRedirect("/")

#     return render(request, "delete.html", context)

# #analysis------------------------------------------------
# def analysis_result_create_view(request):
#     # dictionary for initial data with
#     # field names as keys
#     context = {}

#     # add the dictionary during initialization
#     form = Analysis_result_Form(request.POST or None)
#     if form.is_valid():
#         form.save()

#     context['form'] = form
#     return render(request, "create_view.html", context)


# def analysis_result_list_view(request):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # add the dictionary during initialization
#     context["dataset"] = Analysis_result.objects.all()

#     return render(request, "list.html", context)

# def analysis_result_update_view(request, id):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # fetch the object related to passed id
#     obj = get_object_or_404(Analysis_result, result_id = id)

#     # pass the object as instance in form
#     form = Analysis_result_Form(request.POST or None, instance = obj)

#     # save the data from the form and
#     # redirect to detail_view
#     if form.is_valid():
#         form.save()
#         return HttpResponseRedirect("/"+id)

#     # add form dictionary to context
#     context["form"] = form

#     return render(request, "update.html", context)


# def analysis_result_delete_view(request, id):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # fetch the object related to passed id
#     obj = get_object_or_404(Analysis_result, result_id = id)


#     if request.method =="POST":
#         # delete object
#         obj.delete()
#         # after deleting redirect to 
#         # home page
#         return HttpResponseRedirect("/")

#     return render(request, "delete.html", context)


# api calls
# TODO Warning get all commands are for debugging. Very dangerous for data leak reasons

# class social_media_serializer(serializers.ModelSerializer):
#     class Meta:
#         model = Social_media
#         fields = '__all__'
@api_view(['GET'])
def get_social_media(request):
    # test response
    selected = Social_media.objects.all()
    serializer = social_media_serializer(selected, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_social_media(request):
    serializer = social_media_serializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        # test response
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def social_media_detail(request, pk):
    try:
        selected = Social_media.objects.get(pk=pk)
    except Social_media.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = social_media_serializer(selected)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = social_media_serializer(selected, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        selected.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class user_serializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = '__all__'


@api_view(['GET'])
def get_user(request):
    # test response
    selected = User.objects.all()
    serializer = user_serializer(selected, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_user(request):
    serializer = user_serializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        # test response
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, pk):
    try:
        selected = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = user_serializer(selected)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = user_serializer(selected, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        selected.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class post_serializer(serializers.ModelSerializer):
#     class Meta:
#         model = Post
#         fields = '__all__'


@api_view(['GET'])
def get_post(request):
    user_id = request.query_params.get('user_id')
    media_id = request.query_params.get('media_id')
    # 构建查询集
    qs = Post.objects.all()
    if user_id is not None:
        qs = qs.filter(user_id=user_id)
    if media_id is not None:
        qs = qs.filter(media_id=media_id)

    serializer = post_serializer(qs, many=True)
    return Response(serializer.data)


# @api_view(['GET'])
# def get_post_batch(request):
#     ids = request.query_params.getlist('post_ids')  # ['1','2','3']
#     qs  = Post.objects.filter(id__in=ids) if ids else Post.objects.none()
#     serializer = post_serializer(qs, many=True)
#     return Response(serializer.data)


@api_view(['GET'])
def get_post_batch(request):
    # 1️⃣ 取出 ID 列表：/post_batch?post_ids=1&post_ids=2…
    ids = request.query_params.getlist('post_ids')  # ['1', '2', '3']
    # 2️⃣ 解析“是否取反”开关：/post_batch?in=false  (默认 true)
    # 把传进来的字符串统一转小写，便于比较
    in_raw = request.query_params.get('in', 'true').lower()
    # 只要不是 “false/0/no” 之一，就当作 True
    include_flag = in_raw not in ('false', '0', 'no')
    # 3️⃣ 根据开关拼接查询集
    if include_flag:  # in=true → 只要这些 ID
        qs = Post.objects.filter(id__in=ids)
    else:  # in=false → 排除这些 ID
        qs = Post.objects.exclude(id__in=ids)
    # 4️⃣ 序列化并返回
    serializer = post_serializer(qs, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_available_posts(request):
    """
    Query params
    ------------
    user_id   : int  – current user
    media_id  : int  – social-media source to filter on
    Returns all posts from `media_id` that:
      • are NOT authored by `user_id`
      • have NOT yet been reposted by `user_id`
    """
    user_id = request.query_params.get("user_id")
    media_id = request.query_params.get("media_id")

    if user_id is None or media_id is None:
        return Response(
            {"detail": "Both user_id and media_id are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    # 1. posts in this media, excluding the user’s own posts
    posts_qs = (
        Post.objects
        .filter(media_id=media_id)
        .exclude(user_id=user_id)
    )
    # 2. collect IDs the user has already reposted
    reposted_ids = (
        Repost.objects
        .filter(user_id=user_id)
        .values_list("post_id", flat=True)
    )

    # 3. exclude those already-reposted IDs
    posts_qs = posts_qs.exclude(post_id__in=reposted_ids)

    serializer = post_serializer(posts_qs, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_post(request):
    serializer = post_serializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        # test response
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def post_detail(request, pk):
    try:
        selected = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = post_serializer(selected)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = post_serializer(selected, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        selected.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class repost_serializer(serializers.ModelSerializer):
#     class Meta:
#         model = Repost
#         fields = '__all__'


@api_view(['GET'])
def get_repost(request):
    # test response
    user_id = request.query_params.get('user_id')
    if user_id is not None:
        qs = Repost.objects.filter(user_id=user_id)
    else:
        qs = Repost.objects.all()
    serializer = repost_serializer(qs, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_repost(request):
    serializer = repost_serializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        # test response
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def bulk_repost(request):
    user_id = request.data.get("user_id")
    post_ids = request.data.get("post_ids", [])
    if not user_id or not isinstance(post_ids, list):
        return Response(
            {"detail": "user_id 和 post_ids (list) 均不能为空"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    # 如果你的字段名就是 post_id = ForeignKey(Post
    now = timezone.now()
    repost_objs = [
        Repost(user_id_id=user_id, post_id_id=pid, repost_time=now)  # 两个 _id
        for pid in post_ids
    ]
    with transaction.atomic():
        Repost.objects.bulk_create(repost_objs, ignore_conflicts=True)
    return Response({"attempted": post_ids}, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def repost_detail(request, pk):
    try:
        selected = Repost.objects.get(pk=pk)
    except Repost.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = repost_serializer(selected)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = repost_serializer(selected, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        selected.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class institute_serializer(serializers.ModelSerializer):
#     class Meta:
#         model = Institute
#         fields = '__all__'


@api_view(['GET'])
def get_institute(request):
    # test response
    selected = Institute.objects.all()
    serializer = institute_serializer(selected, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_institute(request):
    serializer = institute_serializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        # test response
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def institute_detail(request, pk):
    try:
        selected = Institute.objects.get(pk=pk)
    except Institute.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = institute_serializer(selected)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = institute_serializer(selected, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        selected.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class project_serializer(serializers.ModelSerializer):
#     class Meta:
#         model = Project
#         fields = '__all__'


# @api_view(['GET'])
# def get_project(request):
#     #test response
#     selected = Project.objects.all()
#     serializer = project_serializer(selected, many =True)
#     return Response(serializer.data)

@api_view(['GET'])
def get_project(request):
    """
    如果 URL 中带 ?id=123，就过滤 owner_id=123；否则返回所有项目。
    """
    institute_id = request.query_params.get('institute_id')
    if institute_id is not None:
        qs = Project.objects.filter(institute_id=institute_id)
    else:
        qs = Project.objects.all()
    serializer = project_serializer(qs, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_project(request):
    serializer = project_serializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        # test response
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def project_detail(request, pk):
    try:
        selected = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = project_serializer(selected)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = project_serializer(selected, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        selected.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class project_field_serializer(serializers.ModelSerializer):
#     class Meta:
#         model = Project_field
#         fields = '__all__'

@api_view(['GET'])
def get_project_field(request):
    # test response
    project_id = request.query_params.get('project_id')
    if project_id is not None:
        qs = Project_field.objects.filter(project_id=project_id)
    else:
        qs = Project_field.objects.all()
    serializer = project_field_serializer(qs, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_project_field(request):
    serializer = project_field_serializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        # test response
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def project_field_detail(request, pk):
    try:
        selected = Project_field.objects.get(pk=pk)
    except Project_field.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = project_field_serializer(selected)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = project_field_serializer(selected, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        selected.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class project_post_serializer(serializers.ModelSerializer):
#     class Meta:
#         model = Project_post
#         fields = '__all__'


@api_view(['GET'])
def get_project_post(request):
    # test response
    project_id = request.query_params.get('project_id')
    if project_id is not None:
        qs = Project_post.objects.filter(project_id=project_id)
    else:
        qs = Project_post.objects.all()
    serializer = project_post_serializer(qs, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_project_post(request):
    serializer = project_post_serializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        # test response
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def bulk_project_post(request):
    project_id = request.data.get("project_id")
    post_ids = request.data.get("post_ids", [])
    if not project_id or not isinstance(post_ids, list):
        return Response(
            {"detail": "project_id 和 post_ids (list) 均不能为空"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    project_post_objs = [
        Project_post(project_id_id=project_id, post_id_id=pid)  # 两个 _id
        for pid in post_ids
    ]
    with transaction.atomic():
        Project_post.objects.bulk_create(project_post_objs, ignore_conflicts=True)
    return Response({"attempted": post_ids}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def project_post_remains(request):
    project_id = request.query_params.get('project_id')
    if not project_id:
        return Response({"detail": "Missing project_id"}, status=status.HTTP_400_BAD_REQUEST)

    linked_post_ids = Project_post.objects.filter(project_id=project_id).values_list('post_id', flat=True)
    unlinked_posts = Post.objects.exclude(post_id__in=linked_post_ids)
    # 序列化返回
    serializer = post_serializer(unlinked_posts, many=True)
    return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
def project_post_detail(request, pk):
    try:
        selected = Project_post.objects.get(pk=pk)
    except Project_post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = project_post_serializer(selected)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = project_post_serializer(selected, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        selected.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def project_post_all(request):
    """
    GET /api/project_post/listall?project_id=42
    Returns every column in PROJECT_POST + its POST + its ANALYSIS_RESULTs.
    Rows with no analysis_result still appear (LEFT JOIN semantics).
    """
    project_id = request.query_params.get('project_id')
    if not project_id:
        return Response({"detail": "project_id is required"}, status=400)
    # ProjectPost <-FK-> Post (one)  +  ProjectPost <-FK-> AnalysisResult (many)
    qs = (
        Project_post.objects
        .filter(project_id__project_id=project_id)
        .select_related('post_id', 'project_id')  # ← 外键字段名本来就叫 post_id
        .prefetch_related(  # ← 没写 related_name，用默认 *_set
            Prefetch(
                'analysis_result_set',  # 默认反向名
                queryset=Analysis_result.objects.select_related('field_id')
            )
        )
    )
    post_result = []
    for post in qs:
        value = [a.value for a in post.analysis_result_set.all()]
        field = [a.field_id.field_name for a in post.analysis_result_set.all()]
        field_id = [a.field_id.field_id for a in post.analysis_result_set.all()]

        post_result.append({
            'project_post_id': post.project_post_id,
            'project_id': post.project_id.project_id,
            'post_id': post.post_id.post_id,
            'content': post.post_id.content,
            'user_id': post.post_id.user_id.user_id,
            'media_id': post.post_id.media_id.media_id,
            'post_time': post.post_id.post_time.strftime("%Y-%m-%d %H:%M:%S"),
            'location_city': post.post_id.location_city,
            'location_state': post.post_id.location_state,
            'location_country': post.post_id.location_country,
            'likes': post.post_id.likes,
            'dislikes': post.post_id.dislikes,
            'has_multimedia': post.post_id.has_multimedia,
            'analysis': [{'field_id': i, 'field_name': n, 'value': v}
                         for i, n, v in zip(field_id, field, value)]
        })
    return Response(post_result)


# class analysis_result_serializer(serializers.ModelSerializer):
#     class Meta:
#         model = Analysis_result
#         fields = '__all__'


@api_view(['GET'])
def get_analysis_result(request):
    # test response
    project_post_id = request.query_params.get('project_post_id')
    if project_post_id is not None:
        qs = Analysis_result.objects.filter(project_post_id=project_post_id)
    else:
        qs = Analysis_result.objects.all()
    serializer = analysis_result_serializer(qs, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_analysis_result(request):
    serializer = analysis_result_serializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        # test response
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def analysis_result_detail(request, pk):
    try:
        selected = Analysis_result.objects.get(pk=pk)
    except Analysis_result.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = analysis_result_serializer(selected)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = analysis_result_serializer(selected, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        selected.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
