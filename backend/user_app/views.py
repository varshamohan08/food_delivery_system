from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Case, When, Value
from django.db.models import CharField
from .models import user_data, role_url_permission, role_master

# Create your views here.

def send_email(subject, body, to_email):
    sender_email = ""
    sender_password = ""

    # Create the email message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, message.as_string())


class userLogin(APIView):
    def post(self,request):
        data = request.data

        username = data.get('email', None)
        password = data.get('password', None)

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return Response({"success": True}, status = status.HTTP_200_OK)
        else:
            return Response({"success": False}, status=status.HTTP_400_BAD_REQUEST)


class userLogout(APIView):
    def get(self, request):
        logout(request)
        return Response({"success": True}, status = status.HTTP_200_OK)


class UserAPI(APIView):
    def get(self, request):
        list_name = "List"
        if request.GET.get("id"):
            if user_data.objects.filter(id = request.GET.get("id")).exists():
                userData = user_data.objects.filter(id = request.GET.get("id")).values("id","first_name","last_name","role_master__name","email", "phone_number", "bln_active")
                return Response({"success": True, "user": userData}, status = status.HTTP_200_OK)
            else:
                return Response({"success": False, "message" : "Invalid user id"}, status = status.HTTP_400_BAD_REQUEST)
        else:
            if request.GET.get('type'):
                if request.GET.get('type') == 'del':
                    role = role_master.objects.get(name = 'Delivery Agent')
                    list_name = "Delivery Agent List"
                if request.GET.get('type') == 'cust':
                    role = role_master.objects.get(name = 'Customer')
                    list_name = "Customer List"
                userData = user_data.objects.filter(role_master_id = role.id).annotate(
                    status=Case(
                        When(bln_active=False, then=Value('Inactive')),
                        default=Value('Active'),
                        output_field=CharField(),  # Change the field type accordingly
                    )
                ).values("id","first_name","last_name","role_master__name","email", "phone_number","status")
                # return render(request, "list.html", {"list_name": list_name, "data": userData})
                response_data = {
                    "success": True,
                    "list_name": list_name, 
                    "data": userData
                }
                return Response(response_data, status = status.HTTP_200_OK)
            return Response({"success": False, "message" : "List type not specified"}, status = status.HTTP_200_OK)
    
    def post(self, request):
        try:
            with transaction.atomic():
                user = User.objects.create(username=request.data.get('email'))
                user.email = request.data.get('email')
                user.set_password(request.data.get('password'))
                user.save()
                data = {}
                user_data.objects.create(
                    user=user,
                    role_master=role_master.objects.get(id = request.data.get('role_master')),
                    first_name=request.data.get('first_name'),
                    last_name=request.data.get('last_name'),
                    password=user.password,
                    email=request.data.get('email'),
                    phone_number=request.data.get('phone_number')
                )
                    
                return Response({"success": True, "message" : "Created Successfully"}, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "message" : e}, status = status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            if user_data.objects.filter(id = request.GET.get('id')).exists():
                id = request.GET.get('id')
                user_id = user_data.objects.get(id = id).user_id
                User.objects.filter(id = user_id).delete()
                user_data.objects.filter(id = id).delete()
                return Response({"success": True, "message" : "Deleted Successfully"}, status = status.HTTP_200_OK)
            else:
                return Response({"success": False, "message" : "Invalid user id"}, status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "message" : e}, status = status.HTTP_400_BAD_REQUEST)
        
    def put(self, request):
        try:
            instance = user_data.objects.get(id = request.data.get('id'))
            instance.role_master = role_master.objects.get(id = request.data.get('role_master'))
            instance.first_name = request.data.get('first_name')
            instance.last_name = request.data.get('last_name')
            instance.phone_number = request.data.get('phone_number')
            instance.email = request.data.get('email')
            instance.bln_active = request.data.get('bln_active')
            instance.save()
            return Response({"success": True, "message" : "Updated Successfully"}, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "message" : e}, status = status.HTTP_400_BAD_REQUEST)
        
    def patch(self, request):
        try:
            if user_data.objects.filter(id = request.GET.get('id')).exists():
                user_instance = user_data.objects.get(id = request.GET.get('id'))
                user_instance.bln_active = not user_instance.bln_active
                user_instance.save()
                return Response({"success": True, "message" : "Status Updated Successfully"}, status = status.HTTP_200_OK)
            else:
                return Response({"success": False, "message" : "Invalid user id"}, status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "message" : e}, status = status.HTTP_400_BAD_REQUEST)
