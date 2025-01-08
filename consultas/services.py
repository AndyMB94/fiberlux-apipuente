import requests
from datetime import datetime, timedelta
from django.utils.timezone import now
from .models import DatosEnviados
import logging

logger = logging.getLogger(__name__)

def limpiar_registros_antiguos():
    """
    Elimina registros con fecha_consulta mayor o igual a 30 días.
    """
    # Calcula la fecha límite con timezone-aware
    fecha_limite = now() - timedelta(days=30)
    
    # Elimina registros antiguos
    eliminados = DatosEnviados.objects.filter(fecha_consulta__lte=fecha_limite).delete()
    logger.info(f"Registros eliminados por antigüedad: {eliminados}")

def enviar_json_al_bot(data):
    """
    Envía un JSON al bot con los datos del registro.
    """
    bot_endpoint = "https://url-del-bot.com/api/receive-data"  # Cambia esta URL por la del bot
    try:
        response = requests.post(bot_endpoint, json=data)
        response.raise_for_status()
        logger.info(f"JSON enviado al bot correctamente: {data}")
        return {"message": "JSON enviado al bot correctamente"}
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al enviar JSON al bot: {e}")
        return {"error": str(e)}

def consumir_datos_externos(numero_documento, numero_telefono):
    """
    Consume la API externa y gestiona los registros en la base de datos.
    """
    # URL de la API externa
    url = "https://fiberlux-consultas.onrender.com/api/consultas/"

    # Limpia registros antiguos
    limpiar_registros_antiguos()

    try:
        # Realiza la solicitud GET con los parámetros
        response = requests.get(url, params={"numero_documento": numero_documento, "numero_telefono": numero_telefono})
        response.raise_for_status()
        data = response.json()

        # Obtener el último registro de la respuesta de la API
        if not data:
            logger.info("No se encontraron datos en la API externa")
            return {"message": "No se encontraron datos en la API externa"}

        ultimo_registro = max(data, key=lambda x: x["id"])
        logger.info(f"Procesando último registro: {ultimo_registro}")

        id_sig = ultimo_registro.get("id_sig")
        tipo_documento = ultimo_registro.get("tipo_documento")
        numero_documento = ultimo_registro.get("numero_documento")
        numero_telefono = ultimo_registro.get("numero_telefono")
        operadora = ultimo_registro.get("operadora")

        # Verificar si ya existe un registro reciente con los filtros
        fecha_limite = now() - timedelta(days=30)

        existe_registro = DatosEnviados.objects.filter(
            numero_documento=numero_documento,
            numero_telefono=numero_telefono,
            fecha_consulta__gte=fecha_limite
        ).exists()

        if existe_registro:
            # Crear un nuevo registro con enviado_bot=0
            nuevo_registro = DatosEnviados.objects.create(
                id_sig=id_sig,
                tipo_documento=tipo_documento,
                numero_documento=numero_documento,
                numero_telefono=numero_telefono,
                operadora=operadora,
                fecha_consulta=now(),  # Usa la fecha y hora actual con zona horaria
                enviado_bot=False
            )
            logger.info(f"Nuevo registro creado con enviado_bot=0: {nuevo_registro}")
        else:
            # Crear un nuevo registro con enviado_bot=1
            nuevo_registro = DatosEnviados.objects.create(
                id_sig=id_sig,
                tipo_documento=tipo_documento,
                numero_documento=numero_documento,
                numero_telefono=numero_telefono,
                operadora=operadora,
                fecha_consulta=now(),  # Usa la fecha y hora actual con zona horaria
                enviado_bot=True
            )
            logger.info(f"Nuevo registro creado con enviado_bot=1: {nuevo_registro}")

            # Si enviado_bot=1, enviar JSON al bot
            json_data = {
                "id": nuevo_registro.id,
                "id_sig": nuevo_registro.id_sig,
                "tipo_documento": nuevo_registro.tipo_documento,
                "numero_documento": nuevo_registro.numero_documento,
                "numero_telefono": nuevo_registro.numero_telefono,
                "operadora": nuevo_registro.operadora
            }
            enviar_json_al_bot(json_data)

        return {"message": "Datos procesados correctamente"}

    except requests.exceptions.RequestException as e:
        logger.error(f"Error al consumir API externa: {e}")
        return {"error": str(e)}
