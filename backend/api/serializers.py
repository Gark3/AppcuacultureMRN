from django.contrib.auth.models import User
from rest_framework import serializers
from .models import (
    Acuicola, TipoUsuario, Estanque, Siembra, CalidadAgua, Observacion,
    Tratamiento, Alimentar, Dieta, Adicion, Crecimiento, Cosecha, Producto,
    Proveedor, Entrada, EntradaUnitaria, Salida, SalidaUnitaria, SalidaEstanque,
    Rubro, Perfil, ConfiguracionNomina, PagoNomina, HistorialSueldo, TipoGasto, 
    Gasto
)

class AcuicolaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acuicola
        fields = '__all__'

class TipoUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoUsuario
        fields = '__all__'

# --- SERIALIZER PARA REGISTRO DE USUARIO (User + Perfil) ---
class RegistroUsuarioSerializer(serializers.Serializer):
    # Campos para el modelo User
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    
    # Campos para el modelo Perfil
    telefono = serializers.CharField(required=True)
    sueldo = serializers.FloatField(required=True)
    acuicola = serializers.IntegerField(required=False, allow_null=True)
    tipo_usuario = serializers.IntegerField(default=1)

    def create(self, validated_data):
        # Crear el usuario de Django
        user = User(
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data['last_name'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])  # Usa set_password para encriptar
        user.save()
        
        # Crear el perfil asociado usando el id del usuario recién creado como FK.
        Perfil.objects.create(
            user=user,
            telefono=validated_data['telefono'],
            sueldo=validated_data['sueldo'],
            acuicola_id=validated_data.get('acuicola'),
            tipo_usuario_id=validated_data.get('tipo_usuario', 1)
        )
        return user

# --- Resto de serializers (los dejamos sin cambios) ---

class EstanqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estanque
        fields = '__all__'

class SiembraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Siembra
        fields = '__all__'

class CalidadAguaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalidadAgua
        fields = '__all__'

class ObservacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observacion
        fields = '__all__'

class TratamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tratamiento
        fields = '__all__'

class AlimentarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alimentar
        fields = '__all__'

class DietaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dieta
        fields = '__all__'

class AdicionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adicion
        fields = '__all__'

class CrecimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crecimiento
        fields = '__all__'

class RubroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rubro
        fields = '__all__'

class CosechaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cosecha
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'

class EntradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entrada
        fields = '__all__'

class EntradaUnitariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntradaUnitaria
        fields = '__all__'

class SalidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salida
        fields = '__all__'

class SalidaUnitariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalidaUnitaria
        fields = '__all__'

class SalidaEstanqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalidaEstanque
        fields = '__all__'

# --- SERIALIZADORES PERSONALIZADOS ---

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class PerfilSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer()

    class Meta:
        model = Perfil
        fields = ['id', 'user', 'sueldo', 'acuicola']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)

        # Solo reasigna si el ID del usuario es diferente
        if user_data and user_data.get('id') != instance.user.id:
            try:
                user = User.objects.get(id=user_data['id'])
                instance.user = user
            except User.DoesNotExist:
                raise serializers.ValidationError({"user": "Usuario no encontrado"})

        # Asigna solo los campos enviados (parcial o completo)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class ConfiguracionNominaSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source='perfil.user.get_full_name', read_only=True)
    sueldo = serializers.FloatField(source='perfil.sueldo', read_only=True)
    user_id = serializers.IntegerField(source='perfil.user.id', read_only=True)

    class Meta:
        model = ConfiguracionNomina
        fields = ['id', 'perfil', 'user_id', 'nombre', 'sueldo', 'incluir_en_nomina']

class PagoNominaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagoNomina
        fields = '__all__'

class HistorialSueldoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialSueldo
        fields = '__all__'

class TipoGastoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoGasto
        fields = '__all__'

class GastoSerializer(serializers.ModelSerializer):
    tipo_nombre = serializers.CharField(source='tipo.nombre', read_only=True)
    siembra_id = serializers.IntegerField(required=False, allow_null=True)
    registrado_por_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Gasto
        fields = [
            'id',
            'tipo',
            'tipo_nombre',
            'descripcion',
            'monto',
            'fecha',
            'es_general',
            'siembra',
            'registrado_por',
        ]
        read_only_fields = ['registrado_por']