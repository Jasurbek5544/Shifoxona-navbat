from rest_framework import serializers
from .models import Patient, Appointment
from doctors.serializers import DoctorListSerializer
from doctors.models import Doctor, Schedule

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'full_name', 'phone', 'telegram_id']

class AppointmentSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
    schedule = serializers.PrimaryKeyRelatedField(queryset=Schedule.objects.all())

    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'doctor', 'schedule', 'appointment_date', 'queue_number', 'status', 'notes', 'cancellation_reason']
        read_only_fields = ['queue_number', 'status']

    def create(self, validated_data):
        # Get the doctor and date
        doctor = validated_data['doctor']
        appointment_date = validated_data['appointment_date']

        # Get the last queue number for this doctor and date
        last_appointment = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date
        ).order_by('-queue_number').first()

        # Set the new queue number
        validated_data['queue_number'] = (last_appointment.queue_number + 1) if last_appointment else 1

        return super().create(validated_data)

class AppointmentListSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    doctor = DoctorListSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'doctor', 'appointment_date', 'appointment_time',
                 'status', 'status_display', 'created_at']

class AppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time', 'notes']

    def validate(self, attrs):
        # Check if the appointment time is available
        doctor = attrs['doctor']
        date = attrs['appointment_date']
        time = attrs['appointment_time']

        # Check if there's already an appointment at this time
        if Appointment.objects.filter(
            doctor=doctor,
            appointment_date=date,
            appointment_time=time,
            status__in=['pending', 'confirmed']
        ).exists():
            raise serializers.ValidationError({
                'appointment_time': 'This time slot is already booked.'
            })

        return attrs

class AppointmentDetailSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    doctor = DoctorListSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'doctor', 'appointment_date', 'appointment_time',
                 'status', 'status_display', 'notes', 'cancellation_reason',
                 'created_at', 'updated_at']

class AppointmentCancelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['cancellation_reason']

    def update(self, instance, validated_data):
        instance.status = 'cancelled'
        instance.cancellation_reason = validated_data.get('cancellation_reason', '')
        instance.save()
        return instance 