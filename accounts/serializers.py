from .models import CustomUser
from rest_framework import serializers


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'password',
            'first_name',
            'last_name',
            'business_name',
            'phone_number',
            'address',
            'city',
            'state',
            'country',
            'profile_picture'
        ]

    def create(self, validated_data):
        # Create a new user
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password = validated_data['password'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            business_name = validated_data['business_name'],
            phone_number = validated_data['phone_number'],
            address = validated_data['address'],
            city= validated_data['city'],
            state = validated_data['state'],
            country = validated_data['country'],
            # profile_picture = validated_data['profile_picture']
        )
        
        return user
