from django.shortcuts import redirect
from delivery_app.models import user_data, role_url_permission
from django.http import HttpResponseForbidden

class userLogMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 'Email': 'varsha@g.com', 'Password': 'varsha'
        try:
            path = request.path_info.lstrip('/')
            if path.startswith('admin/'):
                return self.get_response(request)

            if path in ['login', 'logout']:
                return self.get_response(request)
            
            user_details = user_data.objects.get(user_id = request.user.id)
            if role_url_permission.objects.filter(url = path, role_master = user_details.role_master).exists():
                perms = role_url_permission.objects.get(url = path, role_master = user_details.role_master)
                if str(request.method).upper() == 'POST' and perms.bln_post:
                    return self.get_response(request)
                if str(request.method).upper() == 'PATCH' and perms.bln_patch:
                    return self.get_response(request)
                if str(request.method).upper() == 'GET' and perms.bln_get:
                    return self.get_response(request)
                if str(request.method).upper() == 'DELETE' and perms.bln_delete:
                    return self.get_response(request)
                if str(request.method).upper() == 'PUT' and perms.bln_put:
                    return self.get_response(request)
                return HttpResponseForbidden("Permission Denied: You do not have access to this resource.")
            else:
                return HttpResponseForbidden("Permission Denied: You do not have access to this resource.")
        except user_data.DoesNotExist:
            return HttpResponseForbidden("Permission Denied: User details not found.")
        except Exception as e:
            # Handle other exceptions as needed
            return HttpResponseForbidden(f"Permission Denied: {str(e)}")

