from django.db import models

# Create your models here.

class DatosEnviados(models.Model):
    id = models.AutoField(primary_key=True)
    id_sig = models.IntegerField()
    tipo_documento = models.CharField(max_length=20)
    numero_documento = models.CharField(max_length=20)
    numero_telefono = models.CharField(max_length=15)
    operadora = models.CharField(max_length=50)
    fecha_consulta = models.DateTimeField(auto_now_add=True)
    enviado_bot = models.BooleanField(default=False)
    respuesta_bot = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.id_sig} - {self.numero_documento}"
