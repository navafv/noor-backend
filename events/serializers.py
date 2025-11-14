from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source="created_by.get_full_name")
    
    class Meta:
        model = Event
        fields = [
            "id", "title", "description", "start_date", "end_date",
            "created_by", "created_by_name", "created_at"
        ]
        read_only_fields = ["id", "created_by", "created_by_name", "created_at"]

    def create(self, validated_data):
        # Auto-assign the creator
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)