from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Value, Q
from django.db.models.functions import Concat
from .models import *#Post, Project_post, Social_media
from .forms import Social_media_Form, User_Form, Post_Form, Repost_Form, Institute_Form, Project_Form, Project_field_Form,Project_post_Form,Analysis_result_Form
from datetime import datetime
from django.shortcuts import (get_object_or_404,
                              render, 
                              HttpResponseRedirect)


# Post query
class PostView(APIView):
    def get(self, request):
        media = request.GET.get('media')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        username = request.GET.get('username')
        author = request.GET.get('author')

        posts = Post.objects.select_related('user_id', 'media_id').prefetch_related('project_post_set__project_id')
        # query by media name
        if media:
            posts = posts.filter(media_id__name = media)
        # query by timme slot
        if start_date and end_date:
            start_date = datetime.strptime(start_date, "%m/%d/%Y").date()
            end_date = datetime.strptime(end_date, "%m/%d/%Y").date()
            posts = posts.filter(post_time__range = [start_date, end_date])
        # query by username
        if username:
            posts = posts.filter(user_id__username = username)
        # query by author's first name, last name, or full name
        if author:
            posts = posts.annotate(fullname = Concat('user_id__first_name', Value(' '), 'user_id__last_name')).filter(
                Q(user_id__first_name__icontains = author) |
                Q(user_id__last_name__icontains = author) |
                Q(fullname__icontains = author)
            )

        result = []
        for post in posts:
            experiments = [p.project_id.name for p in post.project_post_set.all()]
            result.append({
                'content': post.content,
                'media': post.media_id.name,
                'username': post.user_id.username,
                'time': post.post_time.strftime("%Y-%m-%d %H:%M"),
                'experiments': tuple(experiments),
            })
        return Response(result)
    
# experiment query
class ExperimentView(APIView):
    def get(self, request):
        name = request.GET.get('name')

        posts = Project_post.objects.select_related('post_id', 'project_id').prefetch_related('analysis_result_set__field_id')
        #query by project name
        if name:
            posts = posts.filter(project_id__name = name)
      
        post_result = []
        field_result = []

        for post in posts:
            value = [a.value for a in post.analysis_result_set.all()]
            field = [a.field_id.field_name for a in post.analysis_result_set.all()]
            field_result += field
            post_result.append({
                'post_id':post.post_id.post_id,
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
    

#--------
#social media crud

def social_media_create_view(request):
    # dictionary for initial data with
    # field names as keys
    context = {}

    # add the dictionary during initialization
    form = Social_media_Form(request.POST or None)
    if form.is_valid():
        form.save()

    context['form'] = form
    return render(request, "create_view.html", context)

def social_media_list_view(request):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # add the dictionary during initialization
    context["dataset"] = Social_media.objects.all()
        
    return render(request, "list.html", context)



def social_media_update_view(request, id):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # fetch the object related to passed id
    obj = get_object_or_404(Social_media, media_id = id)

    # pass the object as instance in form
    form = Social_media_Form(request.POST or None, instance = obj)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return HttpResponseRedirect("/"+id)

    # add form dictionary to context
    context["form"] = form

    return render(request, "update.html", context)


def social_media_delete_view(request, id):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # fetch the object related to passed id
    obj = get_object_or_404(Social_media, media_id = id)


    if request.method =="POST":
        # delete object
        obj.delete()
        # after deleting redirect to 
        # home page
        return HttpResponseRedirect("/")

    return render(request, "delete.html", context)


#user ---------------------------------
def user_create_view(request):
    # dictionary for initial data with
    # field names as keys
    context = {}

    # add the dictionary during initialization
    form = User_Form(request.POST or None)
    if form.is_valid():
        form.save()

    context['form'] = form
    return render(request, "create_view.html", context)

def user_list_view(request):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # add the dictionary during initialization
    context["dataset"] = User.objects.all()
        
    return render(request, "list.html", context)


def user_update_view(request, id):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # fetch the object related to passed id
    obj = get_object_or_404(User, user_id = id)

    # pass the object as instance in form
    form = User_Form(request.POST or None, instance = obj)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return HttpResponseRedirect("/"+id)

    # add form dictionary to context
    context["form"] = form

    return render(request, "update.html", context)


def user_delete_view(request, id):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # fetch the object related to passed id
    obj = get_object_or_404(User, user_id = id)


    if request.method =="POST":
        # delete object
        obj.delete()
        # after deleting redirect to 
        # home page
        return HttpResponseRedirect("/")

    return render(request, "delete.html", context)


#post-----------------------------------------------------
def post_create_view(request):
    # dictionary for initial data with
    # field names as keys
    context = {}

    # add the dictionary during initialization
    form = Post_Form(request.POST or None)
    if form.is_valid():
        form.save()

    context['form'] = form
    return render(request, "create_view.html", context)

def post_list_view(request):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # add the dictionary during initialization
    context["dataset"] = Post.objects.all()
        
    return render(request, "list.html", context)



def post_update_view(request, id):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # fetch the object related to passed id
    obj = get_object_or_404(Post, post_id = id)

    # pass the object as instance in form
    form = Post_Form(request.POST or None, instance = obj)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return HttpResponseRedirect("/"+id)

    # add form dictionary to context
    context["form"] = form

    return render(request, "update.html", context)


def post_delete_view(request, id):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # fetch the object related to passed id
    obj = get_object_or_404(Post, post_id = id)


    if request.method =="POST":
        # delete object
        obj.delete()
        # after deleting redirect to 
        # home page
        return HttpResponseRedirect("/")

    return render(request, "delete.html", context)



#repost-----------------------------------------------
def repost_create_view(request):
    # dictionary for initial data with
    # field names as keys
    context = {}

    # add the dictionary during initialization
    form = Repost_Form(request.POST or None)
    if form.is_valid():
        form.save()

    context['form'] = form
    return render(request, "create_view.html", context)

def repost_list_view(request):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # add the dictionary during initialization
    context["dataset"] = Repost.objects.all()
        
    return render(request, "list.html", context)



def repost_update_view(request, id):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # fetch the object related to passed id
    obj = get_object_or_404(Repost, repost_id = id)

    # pass the object as instance in form
    form = Repost_Form(request.POST or None, instance = obj)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return HttpResponseRedirect("/"+id)

    # add form dictionary to context
    context["form"] = form

    return render(request, "update.html", context)


def repost_delete_view(request, id):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # fetch the object related to passed id
    obj = get_object_or_404(Repost, repost_id = id)


    if request.method =="POST":
        # delete object
        obj.delete()
        # after deleting redirect to 
        # home page
        return HttpResponseRedirect("/")

    return render(request, "delete.html", context)

# def project_field_list_view(request):
#     # dictionary for initial data with 
#     # field names as keys
#     context ={}

#     # add the dictionary during initialization
#     context["dataset"] = Repost.objects.all()
        
#     return render(request, "list.html", context)





#institute crud--------------------------------------
def institute_create_view(request):
    # dictionary for initial data with
    # field names as keys
    context = {}

    # add the dictionary during initialization
    form = Institute_Form(request.POST or None)
    if form.is_valid():
        form.save()

    context['form'] = form
    return render(request, "create_view.html", context)

def institute_list_view(request):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # add the dictionary during initialization
    context["dataset"] = Institute.objects.all()
        
    return render(request, "list.html", context)


def institute_update_view(request, id):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # fetch the object related to passed id
    obj = get_object_or_404(Institute, institute_id = id)

    # pass the object as instance in form
    form = Institute_Form(request.POST or None, instance = obj)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return HttpResponseRedirect("/"+id)

    # add form dictionary to context
    context["form"] = form

    return render(request, "update.html", context)


def institute_delete_view(request, id):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # fetch the object related to passed id
    obj = get_object_or_404(Institute, institute_id = id)


    if request.method =="POST":
        # delete object
        obj.delete()
        # after deleting redirect to 
        # home page
        return HttpResponseRedirect("/")

    return render(request, "delete.html", context)



#project form ----------------------------------------
def project_form_create_view(request):
    # dictionary for initial data with
    # field names as keys
    context = {}

    # add the dictionary during initialization
    form = Project_Form(request.POST or None)
    if form.is_valid():
        form.save()

    context['form'] = form
    return render(request, "create_view.html", context)

def project_form_list_view(request):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # add the dictionary during initialization
    context["dataset"] = Project_Form.objects.all()
        
    return render(request, "list.html", context)


def project_update_view(request, id):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # fetch the object related to passed id
    obj = get_object_or_404(Project, project_id = id)

    # pass the object as instance in form
    form = Project_Form(request.POST or None, instance = obj)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return HttpResponseRedirect("/"+id)

    # add form dictionary to context
    context["form"] = form

    return render(request, "update.html", context)


def project_delete_view(request, id):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # fetch the object related to passed id
    obj = get_object_or_404(Project, project_id = id)


    if request.method =="POST":
        # delete object
        obj.delete()
        # after deleting redirect to 
        # home page
        return HttpResponseRedirect("/")

    return render(request, "delete.html", context)


#project field--------------------------------------------------
def project_field_create_view(request):
    # dictionary for initial data with
    # field names as keys
    context = {}

    # add the dictionary during initialization
    form = Project_field_Form(request.POST or None)
    if form.is_valid():
        form.save()

    context['form'] = form
    return render(request, "create_view.html", context)

def project_field_list_view(request):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # add the dictionary during initialization
    context["dataset"] = Project_field.objects.all()
        
    return render(request, "list.html", context)



def project_field_update_view(request, id):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # fetch the object related to passed id
    obj = get_object_or_404(Project_field, field_id = id)

    # pass the object as instance in form
    form = Project_field_Form(request.POST or None, instance = obj)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return HttpResponseRedirect("/"+id)

    # add form dictionary to context
    context["form"] = form

    return render(request, "update.html", context)


def project_field_delete_view(request, id):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # fetch the object related to passed id
    obj = get_object_or_404(Project_field, field_id = id)


    if request.method =="POST":
        # delete object
        obj.delete()
        # after deleting redirect to 
        # home page
        return HttpResponseRedirect("/")

    return render(request, "delete.html", context)




#project Post-------------------------------------
def project_post_create_view(request):
    # dictionary for initial data with
    # field names as keys
    context = {}

    # add the dictionary during initialization
    form = Project_post_Form(request.POST or None)
    if form.is_valid():
        form.save()

    context['form'] = form
    return render(request, "create_view.html", context)

def project_post_list_view(request):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # add the dictionary during initialization
    context["dataset"] = Project_post.objects.all()
        
    return render(request, "list.html", context)


def project_post_update_view(request, id):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # fetch the object related to passed id
    obj = get_object_or_404(Project_post, project_post_id = id)

    # pass the object as instance in form
    form = Project_post_Form(request.POST or None, instance = obj)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return HttpResponseRedirect("/"+id)

    # add form dictionary to context
    context["form"] = form

    return render(request, "update.html", context)


def project_post_delete_view(request, id):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # fetch the object related to passed id
    obj = get_object_or_404(Project_post, project_post_id = id)


    if request.method =="POST":
        # delete object
        obj.delete()
        # after deleting redirect to 
        # home page
        return HttpResponseRedirect("/")

    return render(request, "delete.html", context)

#analysis------------------------------------------------
def analysis_result_create_view(request):
    # dictionary for initial data with
    # field names as keys
    context = {}

    # add the dictionary during initialization
    form = Analysis_result_Form(request.POST or None)
    if form.is_valid():
        form.save()

    context['form'] = form
    return render(request, "create_view.html", context)



def analysis_result_list_view(request):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # add the dictionary during initialization
    context["dataset"] = Analysis_result.objects.all()
        
    return render(request, "list.html", context)

def analysis_result_update_view(request, id):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # fetch the object related to passed id
    obj = get_object_or_404(Analysis_result, result_id = id)

    # pass the object as instance in form
    form = Analysis_result_Form(request.POST or None, instance = obj)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return HttpResponseRedirect("/"+id)

    # add form dictionary to context
    context["form"] = form

    return render(request, "update.html", context)


def analysis_result_delete_view(request, id):
    # dictionary for initial data with 
    # field names as keys
    context ={}

    # fetch the object related to passed id
    obj = get_object_or_404(Analysis_result, result_id = id)


    if request.method =="POST":
        # delete object
        obj.delete()
        # after deleting redirect to 
        # home page
        return HttpResponseRedirect("/")

    return render(request, "delete.html", context)
