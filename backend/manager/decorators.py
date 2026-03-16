from functools import wraps
from manager.manager import has_permission
from manager.manager import HttpsAppResponse
from django.db import connection
from django.core.cache import cache
import time


# @has_perm("can_add_system_parameter")

def has_perm(act_code):
    def decorator(view):
        @wraps(view)
        def _wrapped_view(self, request, *args, **kwargs):
            if has_permission(self.request.user, act_code) is False:
                return HttpsAppResponse.send([], 0, "You don't have permission to perform this action.")
            return view(self, request, *args, **kwargs)
        return _wrapped_view
    return decorator


def query_debugger(view):
    def wrap(self, request, *args, **kwargs):
        initial_queries = len(connection.queries)
        start = time.time()
        result = view(self, request, *args, **kwargs)
        execution_time = time.time()-start
        final_queries = len(connection.queries)
        total_time = 0.0

        print(f"==============> function : {view.__name__} made {final_queries - initial_queries} queries <========================")
        for data in connection.queries:
            print(f"\n({data['time']}) => {data['sql']}")
            total_time += float(data['time'])
        print(f"\n===============> Total : {round(total_time,3)}(query), {round(execution_time,3)}(function) <==================\n")

        return result
    return wrap


def queryset_caching(query_func):
    def wrap(*args, **kwargs):
        cache_key = f"{query_func.__name__}_{args}_{kwargs}"
        result = cache.get(cache_key)
        if not result:
            result = query_func(*args, **kwargs)
            # add expire time
            cache.set(cache_key, result)
        return result
    return wrap


# All Example : https://www.w3resource.com/python-exercises/decorator/index.php

#Example: check secret key in header
# def check_secret_key(function):
#     @wraps(function)
#     def decorator(request, *args, **kwrgs):
#         key = request.headers.get("Secret-Key")
#         if key == settings.SECRET_KEY:
#             return function(request, *args, **kwrgs)
#         else:
#         return HttpResponse(json.dumps({"data":{}, "status": 0, "message": "Secret key did not match!"}))

#     return decorator
