from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from scipy.stats import f_oneway
from io import BytesIO
from reportlab.pdfgen import canvas
from .models import Estanque  # Ajusta este import al modelo correcto

class AnovaAnalysisView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        estanques_ids = request.data.get("estanques", [])
        parametro = request.data.get("parametro", "")

        if not estanques_ids or not parametro:
            return JsonResponse({"error": "Faltan datos en la solicitud"}, status=400)

        # Recolectar los datos por estanque
        datos_por_estanque = []
        for id_estanque in estanques_ids:
            try:
                estanque = Estanque.objects.get(id=id_estanque)
                valores = getattr(estanque, parametro, None)
                if valores is None:
                    return JsonResponse({"error": f"Parametro '{parametro}' no encontrado en estanque {id_estanque}"}, status=400)
                datos_por_estanque.append(valores)
            except Estanque.DoesNotExist:
                return JsonResponse({"error": f"Estanque {id_estanque} no existe"}, status=404)

        # Verifica que haya suficientes grupos
        if len(datos_por_estanque) < 2:
            return JsonResponse({"error": "Se necesitan al menos dos grupos para hacer ANOVA"}, status=400)

        # Realizar ANOVA
        resultado = f_oneway(*datos_por_estanque)

        # Crear PDF en memoria
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont("Helvetica", 12)
        p.drawString(100, 800, "Resultado del ANOVA")
        p.drawString(100, 780, f"Parametro: {parametro}")
        p.drawString(100, 760, f"F-statistic: {resultado.statistic:.4f}")
        p.drawString(100, 740, f"p-value: {resultado.pvalue:.4f}")
        p.save()

        buffer.seek(0)
        response = HttpResponse(buffer, content_type="application/pdf")
        response['Content-Disposition'] = 'attachment; filename="anova_resultado.pdf"'
        return response
