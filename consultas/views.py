from django.http import JsonResponse
from .services import consumir_datos_externos
import logging
# Create your views here.


logger = logging.getLogger(__name__)
def filtrar_datos(request):
    numero_documento = request.GET.get("numero_documento")
    numero_telefono = request.GET.get("numero_telefono")

    logger.info(f"Filtrando datos para documento: {numero_documento}, teléfono: {numero_telefono}")

    if not numero_documento or not numero_telefono:
        logger.warning("Parámetros incompletos en la solicitud")
        return JsonResponse({"error": "Debe proporcionar numero_documento y numero_telefono"}, status=400)

    resultado = consumir_datos_externos(numero_documento, numero_telefono)
    if "error" in resultado:
        logger.error(f"Error al procesar datos: {resultado['error']}")
        return JsonResponse({"error": resultado["error"]}, status=500)
    return JsonResponse({"message": resultado["message"]}, status=200)