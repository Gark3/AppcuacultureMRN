<template>
  <section class="card">
    <div class="card__header">
      <h2 class="card__title">Agregar Estanque</h2>
      <p class="card__sub">Captura los datos del estanque y selecciona su ubicación en el mapa.</p>
    </div>

    <form @submit.prevent="guardarEstanque">
      <div class="field">
        <label for="nombre">Nombre</label>
        <input class="input" type="text" id="nombre" v-model="estanque.nombre" required />
      </div>

      <div class="field">
        <label for="forma">Forma</label>
        <input class="input" type="text" id="forma" v-model="estanque.forma" required />
      </div>

      <div class="field">
        <label for="superficie">Superficie (m²)</label>
        <input class="input" type="number" id="superficie" v-model.number="estanque.superficie" min="0" step="0.0001" required />
      </div>

      <div class="field">
        <label for="profundidad">Profundidad (m)</label>
        <input class="input" type="number" id="profundidad" v-model.number="estanque.profundidad" min="0" step="0.01" required />
      </div>

      <div class="field">
        <label for="infraestructura">Infraestructura</label>
        <input class="input" type="text" id="infraestructura" v-model="estanque.infraestructura" required />
      </div>

      <div class="field">
        <label>Ubicación</label>
        <div class="map-container" ref="mapContainer"></div>
        <p class="small text-muted mt-2">
          Click en el mapa para fijar el marcador. Arrástralo para ajustar la posición.
        </p>
      </div>

      <div class="mt-3">
        <button type="submit" class="btn btn--accent btn--lg">Guardar</button>
      </div>
    </form>
  </section>
</template>

<script>
import { onMounted, reactive, ref, nextTick } from "vue";
import axios from "axios";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import markerIconPath from "@/assets/custom_marker.png";

export default {
  name: "AgregarEstanque",
  setup() {
    const userData = JSON.parse(localStorage.getItem("user"));
    const estanque = reactive({
      nombre: "",
      forma: "",
      superficie: null,
      profundidad: null,
      infraestructura: "",
      ubicacion: { lat: 25.547546, lng: -108.481789 },
    });

    const mapContainer = ref(null);
    let map, marker;

    const markerIcon = L.icon({
      iconUrl: markerIconPath,
      iconSize: [25, 25],
    });

    const initMap = () => {
      if (!mapContainer.value) return;

      map = L.map(mapContainer.value).setView([estanque.ubicacion.lat, estanque.ubicacion.lng], 13);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      }).addTo(map);

      marker = L.marker([estanque.ubicacion.lat, estanque.ubicacion.lng], {
        icon: markerIcon,
        draggable: true,
      }).addTo(map);

      marker.on("dragend", () => {
        const { lat, lng } = marker.getLatLng();
        estanque.ubicacion.lat = lat;
        estanque.ubicacion.lng = lng;
      });

      map.on("click", (e) => {
        const { lat, lng } = e.latlng;
        marker.setLatLng([lat, lng]);
        estanque.ubicacion.lat = lat;
        estanque.ubicacion.lng = lng;
      });
    };

    const guardarEstanque = async () => {
      if (
        !estanque.nombre ||
        !estanque.forma ||
        !estanque.infraestructura ||
        !(estanque.superficie > 0) ||
        !(estanque.profundidad > 0)
      ) {
        alert("Por favor, complete todos los campos correctamente.");
        return;
      }

      try {
        const userData = JSON.parse(localStorage.getItem("user"));
        const ubicacionStr = `${estanque.ubicacion.lat}//${estanque.ubicacion.lng}`;

        const response = await axios.post("http://localhost:8000/api/estanque/", {
          estado: 1,
          nombre: estanque.nombre,
          forma: estanque.forma,
          superficie: estanque.superficie,
          profundidad: estanque.profundidad,
          infraestructura: estanque.infraestructura,
          ubicacion: ubicacionStr, // el backend espera string "lat//lng"
          estatus: true,
          usuario: userData.usuario_id,
          acuicola: userData.acuicola,
        });

        alert("Estanque guardado correctamente.");
        console.log("Respuesta del backend:", response.data);

        // Limpiar formulario (sin romper ubicacion como objeto)
        estanque.nombre = "";
        estanque.forma = "";
        estanque.superficie = null;
        estanque.profundidad = null;
        estanque.infraestructura = "";
        estanque.ubicacion = { lat: 25.547546, lng: -108.481789 };
        if (marker) marker.setLatLng([estanque.ubicacion.lat, estanque.ubicacion.lng]);
        if (map) map.setView([estanque.ubicacion.lat, estanque.ubicacion.lng], 13);
      } catch (error) {
        console.error("Error al guardar el estanque:", error);
        alert("Hubo un error al guardar el estanque.");
      }
    };

    onMounted(() => {
      nextTick(() => initMap());
    });

    return { estanque, guardarEstanque, mapContainer };
  },
};
</script>

<style scoped>
/* Alto y estilo del contenedor del mapa usando variables del tema global */
.map-container {
  height: 320px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}
</style>
