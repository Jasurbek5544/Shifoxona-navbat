from rest_framework import serializers
from .models import Specialization, Doctor, Schedule

class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = ['id', 'name', 'description']

class ScheduleSerializer(serializers.ModelSerializer):
    weekday_display = serializers.CharField(source='get_weekday_display', read_only=True)

    class Meta:
        model = Schedule
        fields = ['id', 'weekday', 'weekday_display', 'start_time', 'end_time', 'is_working']

class DoctorListSerializer(serializers.ModelSerializer):
    specialization = SpecializationSerializer(read_only=True)
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'full_name', 'clinic_name', 'specialization', 'experience_years', 'photo']

class DoctorDetailSerializer(serializers.ModelSerializer):
    specialization = SpecializationSerializer(read_only=True)
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    schedules = ScheduleSerializer(many=True, read_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'full_name', 'clinic_name', 'specialization', 'experience_years',
                 'bio', 'photo', 'schedules'] 