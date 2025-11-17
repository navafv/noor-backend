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

    def validate(self, attrs):
        # Handle update vs create scenarios
        start_date = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = attrs.get('end_date', getattr(self.instance, 'end_date', None))

        # Default end_date to start_date if not provided
        if end_date is None:
             # If end_date is being explicitly set to None, or not sent, assume single day
             end_date = start_date
             attrs['end_date'] = start_date

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError("End date cannot be before the start date.")
        
        return attrs

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)