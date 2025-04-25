The backend here only have query functions, and the frontend here just is a simple react app only for sending get request. 
1. post query
   expected "GET" request:  "GET /api/query/post/?media={mediw}&start_date={start_data}&end_date={end_data}&username={username}&author={author_name}

   data response:
   {
     'content': post.content,
     'media': post.media_id.name,
     'username': post.user_id.username,
     'time': post.post_time.strftime("%Y-%m-%d %H:%M"),
     'experiments': experiments,
   }

2.experiment query
      expected "GET" request: "GET /api/query/experiment/?name= {name}

      date response:
      {
         'posts': post_result,
         'percentages': percentages,
      }
      where:
      post_result:
      {
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
      }
      percentages:
      {
        'field1': %,
        'field2': %,
        'field3': %,
        ...
      }

3. (7330 students only) pending
