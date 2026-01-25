from rest_framework import serializers

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["id", "name", "created_at"]
