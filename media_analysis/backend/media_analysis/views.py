from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Value, Q
from django.db.models.functions import Concat
from .models import Post, Project_post
from datetime import datetime

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