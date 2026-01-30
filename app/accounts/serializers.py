from django.contrib.auth import get_user_model
from rest_framework import serializers

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["id", "name", "created_at", "default_start_address"]

User = get_user_model()
class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "default_start_address"
        ]