from rest_framework import fields, serializers, validators
from .models import CustomUser, Machine

class UserSerializer(serializers.ModelSerializer):
    #machine = serializers.CharField(validators=[required,check_machine_id])
    class Meta:
        model = CustomUser
        fields = ('pk', 'email', 'password', 'machine')
        extra_kwargs = {'machine': {'required': True}}

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        if 'password' in validated_data:
            user.set_password(validated_data['password'])
        user.save()
        return user
