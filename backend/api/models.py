from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
# ------------------------------------------------------------
# Modelos que ya tenías (Acuicola, TipoUsuario, etc.)
# ------------------------------------------------------------
class Acuicola(models.Model):
    id_acuicola = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    RFC = models.CharField(max_length=13, unique=True)
    ubicacion = models.TextField()
    telefono = models.CharField(max_length=15)

class TipoUsuario(models.Model):
    id_tipo_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)

# NOTA: Se elimina (o comenta) el modelo Usuario personalizado,
# ya que usaremos el modelo de usuario por defecto que ya provee Django.
"""
class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    acuicola = models.ForeignKey(Acuicola, on_delete=models.CASCADE, blank=True, null=True)
    tipo_usuario = models.ForeignKey(TipoUsuario, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    usuario = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15)
    sueldo = models.FloatField()
    
    @property
    def id(self):
        return self.id_usuario
"""

# ------------------------------------------------------------
# BaseModel: Actualizamos la referencia del usuario
# ------------------------------------------------------------
class BaseModel(models.Model):
    # Ahora usamos settings.AUTH_USER_MODEL para referenciar al usuario (por defecto, auth.User)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    acuicola = models.ForeignKey(Acuicola, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.IntegerField(default=1)  # 1 = Activo, 2 = Oculto, 3 = Eliminado

    class Meta:
        abstract = True

# ------------------------------------------------------------
# Resto de tus modelos
# ------------------------------------------------------------
class Estanque(BaseModel):
    id_estanque = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    forma = models.CharField(max_length=255)
    superficie = models.FloatField()
    profundidad = models.FloatField()
    infraestructura = models.CharField(max_length=255)
    ubicacion = models.TextField()
    estatus = models.BooleanField(default=0)

class Siembra(BaseModel):
    id_siembra = models.AutoField(primary_key=True)
    estanque = models.ForeignKey(Estanque, on_delete=models.CASCADE)
    especie = models.CharField(max_length=255)
    cantidad_organismos = models.IntegerField()
    peso_promedio = models.FloatField()
    tamano_promedio = models.FloatField()
    etapa = models.CharField(max_length=255)
    
class CalidadAgua(BaseModel):
    id_calidad_agua = models.AutoField(primary_key=True)
    siembra = models.ForeignKey(Siembra, on_delete=models.CASCADE)
    temperatura = models.FloatField()
    oxigeno_disuelto = models.FloatField()
    ph = models.FloatField()
    nitritos = models.FloatField()
    nitratos = models.FloatField()
    sulfato = models.FloatField()
    fosfato = models.FloatField()
    cloro = models.FloatField()
    salinidad = models.FloatField()
    amonio = models.FloatField()

class Observacion(BaseModel):
    id_observacion = models.AutoField(primary_key=True)
    observacion = models.TextField()

class Tratamiento(BaseModel):
    id_tratamiento = models.AutoField(primary_key=True)
    siembra = models.ForeignKey(Siembra, on_delete=models.CASCADE)
    motivo = models.TextField()
    tipo = models.TextField()
    cantidad = models.FloatField()
    frecuencia = models.TextField()
    observacion = models.CharField(max_length=255)

class Alimentar(BaseModel):
    id_alimento = models.AutoField(primary_key=True)
    siembra = models.ForeignKey(Siembra, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=255)
    lote = models.CharField(max_length=30)
    kg = models.FloatField()
    supervivencia = models.FloatField()
    clima = models.CharField(max_length=255)
    observacion = models.CharField(max_length=255)
  
class Dieta(BaseModel):
    id_dieta = models.AutoField(primary_key=True)
    siembra = models.ForeignKey(Siembra, on_delete=models.CASCADE)
    alimento = models.ForeignKey(Alimentar, on_delete=models.CASCADE)
    kg_diarios = models.FloatField()
    peso_meta = models.FloatField()
    tiempo_dias = models.IntegerField()
    frecuencia = models.IntegerField()
    notas = models.CharField(max_length=255)

class Adicion(BaseModel):
    id_adicion = models.AutoField(primary_key=True)
    siembra = models.ForeignKey(Siembra, on_delete=models.CASCADE)
    cantidad_organismos = models.IntegerField()
    peso_promedio = models.FloatField()

class Rubro(BaseModel):
    id_rubro = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    unidad = models.CharField(max_length=255)

class Crecimiento(BaseModel):
    id_crecimiento = models.AutoField(primary_key=True)
    siembra = models.ForeignKey(Siembra, on_delete=models.CASCADE)
    medicion = models.FloatField()
    rubro = models.ForeignKey(Rubro, on_delete=models.CASCADE, null=True, blank=True)
    
class Cosecha(BaseModel):
    id_cosecha = models.AutoField(primary_key=True)
    siembra = models.ForeignKey(Siembra, on_delete=models.CASCADE)
    biomasa_real = models.FloatField()
    destino = models.CharField(max_length=255)
    documento = models.TextField()
    transporte = models.TextField()
    
class Producto(BaseModel):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    rubro = models.CharField(max_length=255)
    porcentaje_proteina = models.FloatField()    
    presentacion = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=255)

class Proveedor(BaseModel):
    id_proveedor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    correo = models.CharField(max_length=255)
    telefono = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=255)
  
class Entrada(BaseModel):
    id_entrada_producto = models.AutoField(primary_key=True)
    provedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)

class EntradaUnitaria(BaseModel):
    id_entrada_unitaria = models.AutoField(primary_key=True)
    entrada = models.ForeignKey(Entrada, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_kg = models.FloatField()
    unidades = models.IntegerField()
    costo = models.FloatField()
    lote = models.CharField(max_length=255)

class Salida(BaseModel):
    id_salida_producto = models.AutoField(primary_key=True)
    solicitante = models.IntegerField()
    
class SalidaUnitaria(BaseModel):
    id_salida_unitaria = models.AutoField(primary_key=True)
    salida = models.ForeignKey(Salida, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    lote = models.CharField(max_length=255)
    cantidad = models.FloatField()
    cantidad_kg = models.FloatField()
    destino = models.TextField()

class SalidaEstanque(BaseModel):
    id_salida_estanque = models.AutoField(primary_key=True)
    salidaunitaria = models.ForeignKey(SalidaUnitaria, on_delete=models.CASCADE)
    siembra = models.ForeignKey(Siembra, on_delete=models.CASCADE)

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    acuicola = models.ForeignKey(Acuicola, on_delete=models.CASCADE, blank=True, null=True)
    tipo_usuario = models.ForeignKey(TipoUsuario, on_delete=models.CASCADE, default=1)
    telefono = models.CharField(max_length=15)
    sueldo = models.FloatField()

    def __str__(self):
        return self.user.username
    
class PagoNomina(models.Model):
    perfil = models.ForeignKey('Perfil', on_delete=models.CASCADE)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    cantidad_pagada = models.FloatField()
    observaciones = models.TextField(blank=True, null=True)
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.perfil.user.username} - {self.fecha_pago.date()} - ${self.cantidad_pagada}"
    
class ConfiguracionNomina(models.Model):
    perfil = models.OneToOneField('Perfil', on_delete=models.CASCADE)
    incluir_en_nomina = models.BooleanField(default=True)

    def __str__(self):
        estado = "Incluido" if self.incluir_en_nomina else "Excluido"
        return f"{self.perfil.user.get_full_name()} - {estado}"
    
class HistorialSueldo(models.Model):
    perfil = models.ForeignKey('Perfil', on_delete=models.CASCADE)
    sueldo_anterior = models.FloatField()
    sueldo_nuevo = models.FloatField()
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    cambiado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.perfil.user.username} | ${self.sueldo_anterior} → ${self.sueldo_nuevo} | {self.fecha_cambio.date()}"
    
class TipoGasto(models.Model):
    nombre = models.CharField(max_length=100)  # Ej: Mantenimiento, Servicios, Nomina
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Gasto(models.Model):
    tipo = models.ForeignKey(TipoGasto, on_delete=models.CASCADE, related_name='gastos')
    descripcion = models.TextField()
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField(default=timezone.now)
    
    # Este campo indica si se reparte entre todos los ciclos activos
    es_general = models.BooleanField(default=False)

    # Solo si no es general, se asigna a un ciclo de siembra específico
    siembra = models.ForeignKey(
        Siembra,  # Ajusta si tienes otro nombre
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='gastos_directos'
    )

    registrado_por = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.tipo.nombre} - ${self.monto} - {'General' if self.es_general else 'Específico'}"
