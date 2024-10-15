from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from delivery_app.serializers import OrderMasterSerializer
from .models import products, order_status, order_master, order_details
from .forms import *
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.db.models import Max
from random import randint
from user_app.models import user_data


class ProductAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if request.GET.get('id'):
            if products.objects.filter(id = request.GET.get('id')).exists():
                res_data = products.objects.filter(id = request.GET.get('id')).values()
                return Response({"success": True, "data":res_data}, status = status.HTTP_200_OK)
            else:
                return Response({"success": False, "message" : "Invalid product id"}, status = status.HTTP_400_BAD_REQUEST)
        else:
            res_data = list(products.objects.filter(int_status = 1).values())
            return Response({"success": True, "data": res_data}, status = status.HTTP_200_OK)

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
            return Response({"success": True, "message" : "Created Successfully"}, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "message" : e}, status = status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            if products.objects.filter(id = request.GET.get('id')).exists():
                products.objects.filter(id = request.GET.get('id')).update(int_status = 0)
                return Response({"success": True, "message" : "Deleted Successfully"}, status = status.HTTP_200_OK)
            else:
                return Response({"success": False, "message" : "Invalid user id"}, status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "message" : e}, status = status.HTTP_400_BAD_REQUEST)
        
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
            return Response({"success": True, "message" : "Updated Successfully"}, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "message" : e}, status = status.HTTP_400_BAD_REQUEST)


class ProductListAPI(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        if request.GET.get('id'):
            if products.objects.filter(id = request.GET.get('id')).exists():
                response_data = products.objects.filter(id = request.GET.get('id')).values()
                return Response(response_data, status = status.HTTP_200_OK)
            else:
                return Response({"success": True, "message" : "Invalid product id"}, status = status.HTTP_400_BAD_REQUEST)
        else:
            response_data = list(products.objects.filter(int_status = 1).values())
            return Response({"success": True, "data": response_data}, status = status.HTTP_200_OK)

class OrderAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        order_status_cancel = order_status.objects.get(name = "CANCELLED")
        if request.GET.get('id'):
            if order_master.objects.filter(id = request.GET.get('id')).exclude(order_status = order_status_cancel).exists():
                master = order_master.objects.filter(id = request.GET.get('id')).values().first()
                details = order_details.objects.filter(order_master_id = request.GET.get('id')).values()
                response_data = {
                    "success": True,
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
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

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
                    return Response({"success": True, "message" : "Created Successfully"}, status = status.HTTP_200_OK)
                return Response({"success": False}, status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "message" : e}, status = status.HTTP_400_BAD_REQUEST)
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
                        return Response({"success": False, "message" : "User dos not have the privilege"}, status = status.HTTP_400_BAD_REQUEST)
                    order_data.save()
                    return Response({"success": True, "message" : "Status changed Successfully"}, status = status.HTTP_200_OK)
                return Response({"success": False, "message" : "User dos not have the privilege"}, status = status.HTTP_400_BAD_REQUEST)
            return Response({"success": False, "message" : "Something went wrong"}, status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "message" : e}, status = status.HTTP_400_BAD_REQUEST)
