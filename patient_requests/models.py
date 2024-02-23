from django.db import models

class MicrophoneBedPatient(models.Model):
    microphone_id = models.IntegerField(unique=True)
    bed_id  = models.CharField(max_length=100)
    patient_id = models.CharField(max_length=100)
    practitioner_id = models.CharField(max_length=100)

    def __str__(self):
        return f'MicrophoneBedPatient: {self.microphone_id} - {self.bed_id} - {self.patient_id}'
