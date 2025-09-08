<template>
  <div class="registro-siembra">
    <h1>Ficha Técnica</h1>
    <div class="form-group" v-for="(valor, key) in fichaTecnica" :key="key">
      <label>{{ key }}</label>
      <p>{{ valor }}</p>
    </div>
  </div>
</template>

<script>
import axios from '@/services/axios';
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';

export default {
  name: 'FichaTecnica',
  setup() {
    const fichaTecnica = ref({});
    const route = useRoute();

    const cargarDatos = async () => {
      const siembraId = parseInt(route.params.id);
      try {
        const [siembraRes, alimentarRes, crecimientoRes] = await Promise.all([
          axios.get(`/siembra/${siembraId}/`),
          axios.get(`/alimentar/?siembra=${siembraId}`),
          axios.get(`/crecimiento/?siembra=${siembraId}`)
        ]);

        const siembra = siembraRes.data;
        const alimentaciones = alimentarRes.data;
        const crecimientos = crecimientoRes.data;

        const kgAcumulado = alimentaciones.reduce((sum, a) => sum + (a.kg || 0), 0);
        const fechaSiembra = new Date(siembra.fecha);
        const diasDesdeSiembra = Math.floor((new Date() - fechaSiembra) / (1000 * 60 * 60 * 24));

        const totalMortalidad = alimentaciones.reduce((sum, a) => sum + (a.mortalidad || 0), 0);
        const organismosVivos = siembra.cantidad_organismos - totalMortalidad;

        let pesoPromedio = siembra.peso_promedio;
        if (crecimientos.length > 0) {
          const fechas = [...new Set(crecimientos.map(c => c.fecha))].sort();
          const ultimaFecha = fechas.at(-1);
          const crecimientosUltimos = crecimientos.filter(c => c.fecha === ultimaFecha);
          const sumaUltimos = crecimientosUltimos.reduce((sum, c) => sum + (c.gramos_organismo || 0), 0);
          pesoPromedio = sumaUltimos / crecimientosUltimos.length;
        }

        const biomasaEstim = (organismosVivos * pesoPromedio / 1000).toFixed(2);

        const diferenciaPeso = pesoPromedio - siembra.peso_promedio;
        const fcaAcumulado = diferenciaPeso > 0 ? (kgAcumulado / diferenciaPeso).toFixed(2) : 'N/A';

        let fcaAnterior = 'N/A';
        if (crecimientos.length > 1) {
          const fechas = [...new Set(crecimientos.map(c => c.fecha))].sort();
          const ultima = fechas.at(-1);
          const penultima = fechas.at(-2);

          const ultimos = crecimientos.filter(c => c.fecha === ultima);
          const penultimos = crecimientos.filter(c => c.fecha === penultima);

          const promUltimos = ultimos.reduce((sum, c) => sum + c.gramos_organismo, 0) / ultimos.length;
          const promPenultimos = penultimos.reduce((sum, c) => sum + c.gramos_organismo, 0) / penultimos.length;

          const alimentacionSemana = alimentaciones.filter(a => {
            const fecha = new Date(a.fecha);
            const desde = new Date(ultima);
            desde.setDate(desde.getDate() - 7);
            return fecha >= desde && fecha <= new Date(ultima);
          });

          const sumaSemana = alimentacionSemana.reduce((sum, a) => sum + (a.kg || 0), 0);
          const diff = promUltimos - promPenultimos;
          fcaAnterior = diff > 0 ? (sumaSemana / diff).toFixed(2) : 'N/A';
        }

        fichaTecnica.value = {
          'Especie cultivada': siembra.especie,
          'Kilogramos de alimento suministrado': `${kgAcumulado.toFixed(2)} kg`,
          'Días desde la siembra inicial': `${diasDesdeSiembra} días`,
          'Biomasa estimada': `${biomasaEstim} kg`,
          'Siembra inicial': `${siembra.cantidad_organismos} peces`,
          'FCA Acumulado': fcaAcumulado,
          'FCA Anterior': fcaAnterior
        };
      } catch (error) {
        console.error('Error cargando ficha técnica:', error);
      }
    };

    onMounted(cargarDatos);

    return { fichaTecnica };
  }
};
</script>

<style scoped>
.registro-siembra {
  font-family: 'Poppins', sans-serif;
  max-width: auto;
  margin: 30px auto;
  padding: 25px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease-in-out;
}

.registro-siembra:hover {
  box-shadow: 0px 6px 15px rgba(0, 0, 0, 0.15);
}

h1 {
  text-align: center;
  color: #333;
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
}

label {
  font-weight: 600;
  margin-bottom: 8px;
  color: #444;
  font-size: 14px;
}

p {
  margin: 0;
  padding: 8px;
  background-color: #f1f1f1;
  border-radius: 5px;
}
</style>
