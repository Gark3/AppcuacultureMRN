<template>
  <div class="contenedor-siembra">
    <h1>Siembras Activas</h1>
    <input v-model="busqueda" placeholder="Buscar siembra..." class="buscador" />

    <div class="tarjetas">
      <div
        v-for="siembra in siembrasFiltradas"
        :key="siembra.id_siembra"
        class="tarjeta"
      >
        <h2>{{ siembra.estanque_nombre }}</h2>
        <p><strong>Superficie:</strong> {{ siembra.estanque_superficie }} m²</p>
        <p><strong>Profundidad:</strong> {{ siembra.estanque_profundidad }} m</p>
        <p><strong>Infraestructura:</strong> {{ siembra.estanque_infraestructura }}</p>
        <p><strong>Ubicación:</strong> {{ siembra.estanque_ubicacion }}</p>
        <p><strong>Especie:</strong> {{ siembra.especie }}</p>
        <p><strong>Fecha de Siembra:</strong> {{ siembra.fecha }}</p>
        <p><strong>Etapa:</strong> {{ siembra.etapa }}</p>
        <button @click="registrarCalidad(siembra.id_siembra)">Observar Ficha Técnica</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '@/services/axios';

export default {
  data() {
    return {
      siembras: [],
      busqueda: ''
    };
  },
  computed: {
    siembrasFiltradas() {
      const filtro = this.busqueda.toLowerCase();
      return this.siembras.filter(siembra =>
        Object.values(siembra).some(valor =>
          String(valor).toLowerCase().includes(filtro)
        )
      );
    }
  },
  methods: {
    async obtenerSiembras() {
  try {
    const user = JSON.parse(localStorage.getItem('user'));

    const [siembrasRes, estanquesRes] = await Promise.all([
      axios.get('/siembra/'),
      axios.get('/estanque/')
    ]);

    const estanques = estanquesRes.data;

    this.siembras = siembrasRes.data
      .filter(s => s.estado === 1 && s.acuicola === user.acuicola)
      .map(s => {
        const estanque = estanques.find(e => e.id_estanque === s.estanque) || {};
        return {
          ...s,
          estanque_nombre: estanque.nombre || '',
          estanque_superficie: estanque.superficie || '',
          estanque_profundidad: estanque.profundidad || '',
          estanque_infraestructura: estanque.infraestructura || '',
          estanque_ubicacion: estanque.ubicacion || ''
        };
      });

  } catch (error) {
    console.error('Error al obtener siembras o estanques:', error);
  }
},

    registrarCalidad(id) {
      this.$router.push(`/producción/ficha-técnica/registro/${id}`);
    }
  },
  mounted() {
    this.obtenerSiembras();
  }
};
</script>

<style scoped>
.contenedor-siembra {
  max-width: auto;
  margin: auto;
  padding: 20px;
}
h1 {
  text-align: center;
  margin-bottom: 20px;
}
.buscador {
  width: 100%;
  padding: 12px;
  margin-bottom: 20px;
  font-size: 16px;
}
.tarjetas {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}
.tarjeta {
  background: #f9f9f9;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.1);
}
.tarjeta h2 {
  margin-bottom: 10px;
  color: #333;
}
.tarjeta p {
  margin: 5px 0;
  font-size: 14px;
}
button {
  margin-top: 10px;
  padding: 10px;
  background: #007bff;
  border: none;
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  width: 100%;
}
button:hover {
  background: #0056b3;
}
</style>
