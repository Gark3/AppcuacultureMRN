from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .serializers import RegistroUsuarioSerializer
from rest_framework import status, permissions
from django.utils import timezone
from rest_framework.decorators import action

from .models import (
    Acuicola, TipoUsuario, Estanque, Siembra, CalidadAgua,
    Observacion, Tratamiento, Alimentar, Dieta, Adicion, Crecimiento,
    Cosecha, Producto, Proveedor, Entrada, EntradaUnitaria, Salida,
    SalidaUnitaria, SalidaEstanque, Rubro, Perfil, ConfiguracionNomina, 
    PagoNomina, HistorialSueldo, TipoGasto, Gasto
    # No se importa Usuario, ya no se usa
)
from .serializers import (
    AcuicolaSerializer, TipoUsuarioSerializer,
    EstanqueSerializer, SiembraSerializer, CalidadAguaSerializer,
    ObservacionSerializer, TratamientoSerializer, AlimentarSerializer,
    DietaSerializer, AdicionSerializer, CrecimientoSerializer,
    CosechaSerializer, ProductoSerializer, ProveedorSerializer,
    EntradaSerializer, EntradaUnitariaSerializer, SalidaSerializer,
    SalidaUnitariaSerializer, SalidaEstanqueSerializer, RubroSerializer,
    RegistroUsuarioSerializer, PerfilSerializer, ConfiguracionNominaSerializer, 
    PagoNominaSerializer, HistorialSueldoSerializer, TipoGastoSerializer, 
    GastoSerializer  # Serializer para crear usuario y Perfil
)

# ----------------------------------------------------------
# VIEWSETS existentes (sin el antiguo UsuarioViewSet)
# ----------------------------------------------------------

class AcuicolaViewSet(viewsets.ModelViewSet):
    queryset = Acuicola.objects.all()
    serializer_class = AcuicolaSerializer

class TipoUsuarioViewSet(viewsets.ModelViewSet):
    queryset = TipoUsuario.objects.all()
    serializer_class = TipoUsuarioSerializer

class EstanqueViewSet(viewsets.ModelViewSet):
    queryset = Estanque.objects.all()
    serializer_class = EstanqueSerializer

class SiembraViewSet(viewsets.ModelViewSet):
    queryset = Siembra.objects.all()
    serializer_class = SiembraSerializer

class CalidadAguaViewSet(viewsets.ModelViewSet):
    queryset = CalidadAgua.objects.all()
    serializer_class = CalidadAguaSerializer

class ObservacionViewSet(viewsets.ModelViewSet):
    queryset = Observacion.objects.all()
    serializer_class = ObservacionSerializer

class TratamientoViewSet(viewsets.ModelViewSet):
    queryset = Tratamiento.objects.all()
    serializer_class = TratamientoSerializer

class AlimentarViewSet(viewsets.ModelViewSet):
    queryset = Alimentar.objects.all()
    serializer_class = AlimentarSerializer

class DietaViewSet(viewsets.ModelViewSet):
    queryset = Dieta.objects.all()
    serializer_class = DietaSerializer

class AdicionViewSet(viewsets.ModelViewSet):
    queryset = Adicion.objects.all()
    serializer_class = AdicionSerializer

class RubroViewSet(viewsets.ModelViewSet):
    queryset = Rubro.objects.all()
    serializer_class = RubroSerializer

class CrecimientoViewSet(viewsets.ModelViewSet):
    queryset = Crecimiento.objects.all()
    serializer_class = CrecimientoSerializer

class CosechaViewSet(viewsets.ModelViewSet):
    queryset = Cosecha.objects.all()
    serializer_class = CosechaSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer

class EntradaViewSet(viewsets.ModelViewSet):
    queryset = Entrada.objects.all()
    serializer_class = EntradaSerializer

class EntradaUnitariaViewSet(viewsets.ModelViewSet):
    queryset = EntradaUnitaria.objects.all()
    serializer_class = EntradaUnitariaSerializer

class SalidaViewSet(viewsets.ModelViewSet):
    queryset = Salida.objects.all()
    serializer_class = SalidaSerializer

class SalidaUnitariaViewSet(viewsets.ModelViewSet):
    queryset = SalidaUnitaria.objects.all()
    serializer_class = SalidaUnitariaSerializer

class SalidaEstanqueViewSet(viewsets.ModelViewSet):
    queryset = SalidaEstanque.objects.all()
    serializer_class = SalidaEstanqueSerializer

class PerfilViewSet(viewsets.ModelViewSet):
    queryset = Perfil.objects.all()
    serializer_class = PerfilSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Perfil.objects.filter(acuicola=user.perfil.acuicola)
    
    def perform_update(self, serializer):
        instancia = self.get_object()
        salario_anterior = instancia.sueldo
        instancia_modificada = serializer.save()
        diferencia = instancia_modificada.sueldo - salario_anterior
        print(f"[MODIFICACIÓN DE SUELDO] Usuario: {instancia_modificada.user.username} | Cambio: {salario_anterior} → {instancia_modificada.sueldo} (Diferencia: {diferencia})")
# ----------------------------------------------------------
# NUEVA VISTA: Registro de Usuario (GET y POST)
# ----------------------------------------------------------
# Se reemplaza la anterior implementación con APIView por una basada en ListCreateAPIView.
# Esto permite que la Browsable API muestre un formulario de entrada (GET) y realice la
# creación del usuario y Perfil asociado al enviar un POST.
class RegistroUsuarioView(APIView):
    permission_classes = [permissions.AllowAny]  # Permite el registro sin autenticación

    def post(self, request):
        serializer = RegistroUsuarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Crea el usuario y el perfil asociado.
            return Response({"detail": "Usuario creado exitosamente."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ----------------------------------------------------------
# Vista de Login (sin cambios, se conserva como APIView)
# ----------------------------------------------------------
class CustomLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        print("⚠️ CUSTOM LOGIN EJECUTADO")
        username = request.data.get("username")  # 👈 usa 'username' en vez de 'usuario'
        password = request.data.get("password")

        try:
            from django.contrib.auth.models import User
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'detail': 'Usuario no existe.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Verifica contraseña (opcional)
        if not user.check_password(password):
            return Response({'detail': 'Contraseña incorrecta.'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        perfil = getattr(user, 'perfil', None)
        acuicola_id = perfil.acuicola.id_acuicola if perfil and perfil.acuicola else None
        tipo_usuario_id = perfil.tipo_usuario.id_tipo_usuario if perfil else None

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'usuario_id': user.id,
            'nombre': user.first_name,
            'tipo_usuario': tipo_usuario_id,
            'acuicola': acuicola_id
        }, status=status.HTTP_200_OK)
    
class ConfiguracionNominaViewSet(viewsets.ModelViewSet):
    queryset = ConfiguracionNomina.objects.select_related('perfil__user').all()
    serializer_class = ConfiguracionNominaSerializer

    def list(self, request):
        perfiles = Perfil.objects.select_related('user').all()
        configuraciones = {cn.perfil_id: cn for cn in ConfiguracionNomina.objects.all()}
        resultado = []

        for perfil in perfiles:
            config = configuraciones.get(perfil.id)
            if config is None:
                config = ConfiguracionNomina.objects.create(perfil=perfil, incluir_en_nomina=True)
            resultado.append(config)

        # Ordenar: primero los incluidos, luego excluidos; ambos por nombre
        resultado.sort(key=lambda x: (not x.incluir_en_nomina, x.perfil.user.get_full_name().lower()))
        serializer = self.get_serializer(resultado, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='pagar')
    def pagar_nomina(self, request):
        user = request.user
        observacion = request.data.get("observaciones", "")
        fecha = timezone.now()

        configuraciones = ConfiguracionNomina.objects.filter(incluir_en_nomina=True).select_related('perfil')

        pagos_creados = []

        for config in configuraciones:
            perfil = config.perfil
            pago = PagoNomina.objects.create(
                perfil=perfil,
                cantidad_pagada=perfil.sueldo,
                observaciones=observacion,
                registrado_por=user
            )
            pagos_creados.append(pago)

        serializer = PagoNominaSerializer(pagos_creados, many=True)
        return Response({"pagos": serializer.data}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='actualizar-configuracion')
    def actualizar_configuracion(self, request):
        data = request.data.get('configuraciones', [])
        for item in data:
            config = ConfiguracionNomina.objects.filter(perfil_id=item['perfil']).first()
            if config:
                config.incluir_en_nomina = item['incluir_en_nomina']
                config.save()
        return Response({"message": "Configuración actualizada."})
    
class HistorialSueldoViewSet(viewsets.ModelViewSet):
    serializer_class = HistorialSueldoSerializer

    def get_queryset(self):
        perfil_id = self.request.query_params.get('perfil')
        if perfil_id:
            return HistorialSueldo.objects.filter(perfil_id=perfil_id).order_by('-fecha_cambio')
        return HistorialSueldo.objects.none()
    
class TipoGastoViewSet(viewsets.ModelViewSet):
    queryset = TipoGasto.objects.all()
    serializer_class = TipoGastoSerializer
    permission_classes = [permissions.IsAuthenticated]

class GastoViewSet(viewsets.ModelViewSet):
    queryset = Gasto.objects.select_related('tipo', 'siembra', 'registrado_por').all()
    serializer_class = GastoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(registrado_por=self.request.user)

    @action(detail=False, methods=['get'], url_path='por-ciclo/(?P<siembra_id>[^/.]+)')
    def gastos_por_ciclo(self, request, siembra_id=None):
        """
        Retorna todos los gastos que aplican a un ciclo de siembra:
        - Gastos generales proporcionalmente aplicables (si es_general=True)
        - Gastos específicos del ciclo (siembra=siembra_id)
        """
        gastos_generales = Gasto.objects.filter(es_general=True)
        gastos_especificos = Gasto.objects.filter(siembra_id=siembra_id)

        todos = list(gastos_generales) + list(gastos_especificos)
        serializer = self.get_serializer(todos, many=True)
        return Response(serializer.data)