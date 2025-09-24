from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AcuicolaViewSet, TipoUsuarioViewSet, EstanqueViewSet, 
    SiembraViewSet, CalidadAguaViewSet, ObservacionViewSet, TratamientoViewSet,
    AlimentarViewSet, DietaViewSet, AdicionViewSet, CrecimientoViewSet, 
    CosechaViewSet, ProductoViewSet, ProveedorViewSet, EntradaViewSet, 
    EntradaUnitariaViewSet, SalidaViewSet, SalidaUnitariaViewSet, SalidaEstanqueViewSet,
    RubroViewSet, RegistroUsuarioView, PerfilViewSet, ConfiguracionNominaViewSet,
    HistorialSueldoViewSet, TipoGastoViewSet, GastoViewSet
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import CustomLoginView
# 📌 Creamos un router y registramos los ViewSets
router = DefaultRouter()
router.register(r'acuicola', AcuicolaViewSet)
router.register(r'tipo-usuario', TipoUsuarioViewSet)
router.register(r'estanque', EstanqueViewSet)
router.register(r'siembra', SiembraViewSet)
router.register(r'calidad-agua', CalidadAguaViewSet)
router.register(r'observacion', ObservacionViewSet)
router.register(r'tratamiento', TratamientoViewSet)
router.register(r'alimentar', AlimentarViewSet)
router.register(r'dieta', DietaViewSet)
router.register(r'adicion', AdicionViewSet)
router.register(r'rubro', RubroViewSet)
router.register(r'crecimiento', CrecimientoViewSet)
router.register(r'cosecha', CosechaViewSet)
router.register(r'producto', ProductoViewSet)
router.register(r'proveedor', ProveedorViewSet)
router.register(r'entrada', EntradaViewSet)
router.register(r'entrada-unitaria', EntradaUnitariaViewSet)
router.register(r'salida', SalidaViewSet)
router.register(r'salida-unitaria', SalidaUnitariaViewSet)
router.register(r'salida-estanque',SalidaEstanqueViewSet)
router.register(r'perfiles', PerfilViewSet)
router.register(r'nomina', ConfiguracionNominaViewSet, basename='nomina')
router.register(r'historial-sueldo', HistorialSueldoViewSet, basename='historial-sueldo')
router.register(r'tipos-gasto', TipoGastoViewSet)
router.register(r'gastos', GastoViewSet)
# 📌 Definimos las rutas de la API
urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='custom_login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('usuario/registrar/', RegistroUsuarioView.as_view(), name='registrar_usuario'),
    path('', include(router.urls)),
]
