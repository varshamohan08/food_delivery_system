from rest_framework import serializers
from .models import order_details, order_master, order_status, products, user_data

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = order_status
        fields = '__all__'

class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_data
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = products
        fields = '__all__'

class OrderDetailsSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = order_details
        fields = '__all__'

class OrderMasterSerializer(serializers.ModelSerializer):
    order_status = OrderStatusSerializer()
    customer = UserDataSerializer()
    delivery_agent = UserDataSerializer()
    order_details_set = OrderDetailsSerializer(many=True)

    class Meta:
        model = order_master
        fields = '__all__'