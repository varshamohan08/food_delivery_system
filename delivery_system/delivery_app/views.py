from django.db.models import CharField
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from delivery_app.serializers import OrderMasterSerializer
from .models import *
from .forms import *
from rest_framework import permissions
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Case, When, Value
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.db.models import Max
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from random import randint

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
            return Response(status = status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

class userLogout(APIView):
    def get(self, request):
        logout(request)
        return redirect('/login')

class UserAPI(APIView):
    def get(self, request):
        list_name = "List"
        if request.GET.get('id'):
            if user_data.objects.filter(id = request.GET.get('id')).exists():
                userData = user_data.objects.filter(id = request.GET.get('id')).values("id","first_name","last_name","role_master__name","email", "phone_number", "bln_active")
                # response_data = {"list_name": list_name, "data": userData}
                return Response(userData, status = status.HTTP_200_OK)
            else:
                return Response({"message" : "Invalid user id"}, status = status.HTTP_400_BAD_REQUEST)
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
                response_data = {"list_name": list_name, "data": userData}
                return Response(response_data, status = status.HTTP_200_OK)
            return Response({"message" : "List type not specified"}, status = status.HTTP_200_OK)
    
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
                    
                return Response({"message" : "Created Successfully"}, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({"message" : e}, status = status.HTTP_400_BAD_REQUEST)
        
        
    def delete(self, request):
        try:
            if user_data.objects.filter(id = request.GET.get('id')).exists():
                id = request.GET.get('id')
                user_id = user_data.objects.get(id = id).user_id
                User.objects.filter(id = user_id).delete()
                user_data.objects.filter(id = id).delete()
                return Response({"message" : "Deleted Successfully"}, status = status.HTTP_200_OK)
            else:
                return Response({"message" : "Invalid user id"}, status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message" : e}, status = status.HTTP_400_BAD_REQUEST)
        
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
            return Response({"message" : "Updated Successfully"}, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({"message" : e}, status = status.HTTP_400_BAD_REQUEST)
        
    def patch(self, request):
        try:
            if user_data.objects.filter(id = request.GET.get('id')).exists():
                user_instance = user_data.objects.get(id = request.GET.get('id'))
                user_instance.bln_active = not user_instance.bln_active
                user_instance.save()
                return Response({"message" : "Status Updated Successfully"}, status = status.HTTP_200_OK)
            else:
                return Response({"message" : "Invalid user id"}, status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message" : e}, status = status.HTTP_400_BAD_REQUEST)

class ProductAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if request.GET.get('id'):
            if products.objects.filter(id = request.GET.get('id')).exists():
                response_data = products.objects.filter(id = request.GET.get('id')).values()
                return Response(response_data, status = status.HTTP_200_OK)
            else:
                return Response({"message" : "Invalid product id"}, status = status.HTTP_400_BAD_REQUEST)
        else:
            response_data = list(products.objects.filter(int_status = 1).values())
            return Response(response_data, status = status.HTTP_200_OK)
    def post(self, request):
        try:
            products.objects.create(
                name=request.data.get('name'),
                description=request.data.get('description'),
                image=request.data.get('image'),
                unit_price=request.data.get('unit_price'),
                created_by = user_data.objects.get(user_id = request.user.id),
                modified_by = user_data.objects.get(user_id = request.user.id)
            )
            return Response({"message" : "Created Successfully"}, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({"message" : e}, status = status.HTTP_400_BAD_REQUEST)
    def delete(self, request):
        try:
            if products.objects.filter(id = request.GET.get('id')).exists():
                products.objects.filter(id = request.GET.get('id')).update(int_status = 0)
                return Response({"message" : "Deleted Successfully"}, status = status.HTTP_200_OK)
            else:
                return Response({"message" : "Invalid user id"}, status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message" : e}, status = status.HTTP_400_BAD_REQUEST)
        
    def put(self, request):
        try:
            instance = products.objects.get(id = request.data.get('id'))
            instance.name = request.data.get('name')
            instance.description = request.data.get('description')
            instance.unit_price = request.data.get('unit_price')
            instance.modified_by = user_data.objects.get(user_id = request.user.id)
            instance.modified_date = timezone.now()
            if request.data.get('image'):
                instance.image = request.data.get('image')
            instance.save()
            return Response({"message" : "Updated Successfully"}, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({"message" : e}, status = status.HTTP_400_BAD_REQUEST)

class ProductLsitAPI(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        if request.GET.get('id'):
            if products.objects.filter(id = request.GET.get('id')).exists():
                response_data = products.objects.filter(id = request.GET.get('id')).values()
                return Response(response_data, status = status.HTTP_200_OK)
            else:
                return Response({"message" : "Invalid product id"}, status = status.HTTP_400_BAD_REQUEST)
        else:
            response_data = list(products.objects.filter(int_status = 1).values())
            return Response(response_data, status = status.HTTP_200_OK)

class OrderAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        order_status_cancel = order_status.objects.get(name = "CANCELLED")
        if request.GET.get('id'):
            if order_master.objects.filter(id = request.GET.get('id')).exclude(order_status = order_status_cancel).exists():
                master = order_master.objects.filter(id = request.GET.get('id')).values().first()
                details = order_details.objects.filter(order_master_id = request.GET.get('id')).values()
                response_data = {
                    "master" : master,
                    "details" : details
                }
                return Response(response_data, status = status.HTTP_200_OK)
            else:
                return Response({"message" : "Invalid order id"}, status = status.HTTP_400_BAD_REQUEST)
        else:
            user_details = user_data.objects.get(user_id = request.user.id)
            orders = []
            if user_details.role_master.name.upper() == 'ADMIN':
                orders = order_master.objects.filter(int_status=1).exclude(order_status = order_status_cancel).prefetch_related('order_details_set')
            if user_details.role_master.name.upper() == 'DELIVERY AGENT':
                orders = order_master.objects.filter(int_status=1, delivery_agent = user_details).exclude(order_status = order_status_cancel).prefetch_related('order_details_set')
            if user_details.role_master.name.upper() == 'CUSTOMER':
                orders = order_master.objects.filter(int_status=1, customer = user_details).exclude(order_status = order_status_cancel).prefetch_related('order_details_set')
            serializer = OrderMasterSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            with transaction.atomic():
                if request.data.get('products'):
                    order_no = 'ORD-1'
                    if order_master.objects.exists():
                        order_no = 'ORD-' + str(order_master.objects.aggregate(max_id=Max('id'))['max_id'] + 1)
                    ordermaster = order_master()
                    ordermaster.order_no = order_no
                    ordermaster.order_status = order_status.objects.get(name = 'PENDING')
                    ordermaster.customer = user_data.objects.get(user_id = request.user.id)
                    ordermaster.created_by = user_data.objects.get(user_id = request.user.id)
                    ordermaster.created_date = timezone.now()
                    ordermaster.modified_by = user_data.objects.get(user_id = request.user.id)
                    ordermaster.modified_date = timezone.now()
                    ordermaster.save()
                    total_amt = 0
                    for product in request.data.get('products'):
                        product_details = products.objects.get(id = product["id"])
                        order_details.objects.create(
                            order_master = ordermaster,
                            product_id = product["id"],
                            quantity = product["quantity"],
                            unit_price = product_details.unit_price,
                            amount = product_details.unit_price * product["quantity"]
                        )
                        total_amt += product_details.unit_price * product["quantity"]
                    ordermaster.total_amt = total_amt
                    ordermaster.save()
                    # Example usage
                    customer = user_data.objects.get(user_id = request.user.id)
                    otp = randint(100000, 999999)
                    subject = "Order created"
                    body = "Order with order number "+order_no+"created succussfully. Your otp will be "+str(otp)
                    to_email = customer.email
                    customer.otp = otp
                    customer.save()
                    # send_email(subject, body, to_email)
                    return Response({"message" : "Created Successfully"}, status = status.HTTP_200_OK)
                return Response(status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message" : e}, status = status.HTTP_400_BAD_REQUEST)
    def patch(self, request):
        try:
            if request.data.get('id'):
                user_details = user_data.objects.get(user_id = request.user.id)
                order_data = order_master.objects.get(id = request.data.get('id'))
                if order_data and user_details.role_master.name.upper() in ['ADMIN', 'DELIVERY AGENT']:
                    if order_data.order_status.name == 'PENDING' and user_details.role_master.name.upper() == 'ADMIN':
                        order_data.order_status = order_status.objects.get(name = 'ASSIGNED')
                        order_data.delivery_agent_id = request.data.get('agent_id')
                    elif order_data.order_status.name == 'ASSIGNED':
                        customer = user_data.objects.get(user_id = order_data.customer)
                        if customer.otp == request.data.get('otp'):
                            order_data.order_status = order_status.objects.get(name = 'DELIVERED')
                    elif request.data.get('action') == 'CANCEL':
                        order_data.order_status = order_status.objects.get(name = 'CANCELLED')
                    else:
                        return Response({"message" : "User dos not have the privilege"}, status = status.HTTP_400_BAD_REQUEST)
                    order_data.save()
                    return Response({"message" : "Status changed Successfully"}, status = status.HTTP_200_OK)
                return Response({"message" : "User dos not have the privilege"}, status = status.HTTP_400_BAD_REQUEST)
            return Response({"message" : "Something went wrong"}, status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message" : e}, status = status.HTTP_400_BAD_REQUEST)
