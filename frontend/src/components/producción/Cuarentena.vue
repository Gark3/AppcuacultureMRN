<template>
  <section class="cuarentena container">
    <!-- Encabezado -->
    <header class="cz-header card">
      <div class="cz-header__title">
        <h1>Registrar cuarentena</h1>
        <p class="text-muted">
          Registra el motivo y la descripción del evento. Sólo se mostrarán los estanques de tu acuícola.
        </p>
      </div>
      <div class="cz-header__actions">
        <button class="btn btn--ghost btn--sm" type="button" @click="resetForm" :disabled="loading">
          Limpiar
        </button>
      </div>
    </header>

    <!-- Contenido: formulario + ayuda -->
    <div class="cz-grid">
      <!-- Formulario -->
      <form class="card cz-form" @submit.prevent="registrarCuarentena" novalidate>
        <!-- Estanque -->
        <div class="field">
          <label for="estanque">Estanque</label>
          <select id="estanque" class="select" v-model="cuarentena.estanque" required>
            <option value="" disabled>Selecciona un estanque…</option>
            <option v-for="e in estanques" :key="e.id" :value="e.id">
              {{ e.nombre }}
            </option>
          </select>
          <small v-if="errors.estanque" class="error">{{ errors.estanque }}</small>
        </div>

        <!-- Motivo -->
        <div class="field">
          <label for="motivo">Motivo</label>
          <input
            id="motivo"
            class="input"
            type="text"
            v-model.trim="cuarentena.motivo"
            :maxlength="60"
            required
          />
          <div class="field__meta">
            <small class="text-muted">{{ (cuarentena.motivo || '').length }}/60</small>
          </div>
          <small v-if="errors.motivo" class="error">{{ errors.motivo }}</small>
        </div>

        <!-- Descripción -->
        <div class="field">
          <label for="descripcion">Descripción</label>
          <textarea
            id="descripcion"
            class="textarea"
            rows="5"
            v-model.trim="cuarentena.descripcion"
            :maxlength="600"
            required
          ></textarea>
          <div class="field__meta">
            <small class="text-muted">{{ (cuarentena.descripcion || '').length }}/600</small>
          </div>
          <small v-if="errors.descripcion" class="error">{{ errors.descripcion }}</small>
        </div>

        <!-- Botón -->
        <button class="btn btn--accent btn--lg" type="submit" :disabled="loading">
          <span v-if="!loading">Registrar cuarentena</span>
          <span v-else>Registrando…</span>
        </button>
      </form>

      <!-- Panel lateral / Ayuda -->
      <aside class="card cz-aside">
        <h3 class="card__title">Buenas prácticas</h3>
        <ul class="cz-tips">
          <li>Especifica un motivo claro (p. ej. “sospecha de parásitos”, “baja de oxígeno”).</li>
          <li>Agrega datos observables: olor, color del agua, mortalidad, comportamiento.</li>
          <li>Incluye acciones tomadas (aeración extra, muestreo, aislamiento, etc.).</li>
          <li>Si procede, vincula el reporte de Calidad de agua del día.</li>
        </ul>

        <!-- (Opcional) resumen del estanque seleccionado -->
        <div v-if="selectedEstanque" class="cz-estanque card row-card mt-2">
          <div class="card__header">
            <strong>Estanque seleccionado</strong>
          </div>
          <div>
            <div class="stat"><span>Nombre</span><strong>{{ selectedEstanque.nombre }}</strong></div>
            <div class="stat mt-1"><span>ID</span><strong>#{{ selectedEstanque.id }}</strong></div>
          </div>
        </div>
      </aside>
    </div>

    <!-- (Opcional) Tabla de historial de cuarentenas recientes -->
    <section v-if="historial.length" class="card mt-4">
      <div class="card__header">
        <h3 class="card__title">Cuarentenas recientes</h3>
        <p class="card__sub">Últimos 10 registros</p>
      </div>
      <div class="table-wrap">
        <table class="table table--zebra table--sticky">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Estanque</th>
              <th>Motivo</th>
              <th>Descripción</th>
              <th>Registrado por</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(r, i) in historial" :key="i">
              <td>{{ r.fecha }}</td>
              <td>{{ r.estanque }}</td>
              <td>{{ r.motivo }}</td>
              <td>{{ r.descripcion }}</td>
              <td>{{ r.usuario }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </section>
</template>

<script>
import { ref, reactive, computed, onMounted } from "vue";
import axios from "axios";

export default {
  name: "Cuarentena",
  setup() {
    const apiBase = import.meta.env.VITE_API_URL || "/api";

    // estado
    const estanques = ref([]);
    const historial = ref([]); // opcional, para mostrar últimos registros
    const loading = ref(false);
    const errors = reactive({ estanque: "", motivo: "", descripcion: "" });

    const cuarentena = reactive({
      estanque: "",
      motivo: "",
      descripcion: "",
    });

    const selectedEstanque = computed(() =>
      estanques.value.find((e) => e.id === cuarentena.estanque)
    );

    // --- helpers
    const validate = () => {
      errors.estanque = cuarentena.estanque ? "" : "Selecciona un estanque.";
      errors.motivo =
        cuarentena.motivo?.length ? "" : "Escribe el motivo de la cuarentena.";
      errors.descripcion =
        cuarentena.descripcion?.length ? "" : "Describe lo sucedido.";
      return !errors.estanque && !errors.motivo && !errors.descripcion;
    };

    const resetForm = () => {
      cuarentena.estanque = "";
      cuarentena.motivo = "";
      cuarentena.descripcion = "";
      errors.estanque = errors.motivo = errors.descripcion = "";
    };

    // --- carga de datos
    const fetchEstanques = async () => {
      try {
        // Back real sugerido: `${apiBase}/estanques/` (ya scopiado por acuícola)
        const { data } = await axios.get(`${apiBase}/estanques/`);
        // Espera objetos {id, nombre}. Si tu endpoint difiere, ajusta aquí:
        estanques.value = Array.isArray(data) ? data : [];
      } catch (e) {
        // Fallback demo para no romper la vista si el endpoint aún no está listo
        console.warn("Fallo al cargar estanques, usando demo:", e?.message);
        estanques.value = [
          { id: 1, nombre: "Estanque 1" },
          { id: 2, nombre: "Estanque 2" },
          { id: 3, nombre: "Estanque 3" },
        ];
      }
    };

    const fetchHistorial = async () => {
      try {
        // Sugerido: `${apiBase}/cuarentena/?limit=10` (ajusta al endpoint real)
        // const { data } = await axios.get(`${apiBase}/cuarentena/?limit=10`);
        // historial.value = data.results || data;

        // Demo
        historial.value = [];
      } catch (e) {
        console.warn("No fue posible cargar historial:", e?.message);
      }
    };

    // --- submit
    const registrarCuarentena = async () => {
      if (!validate()) return;
      loading.value = true;
      try {
        // Endpoint sugerido: POST `${apiBase}/cuarentena/`
        // await axios.post(`${apiBase}/cuarentena/`, { ...cuarentena });

        // Demo de latencia
        await new Promise((r) => setTimeout(r, 900));
        // UI
        resetForm();
        await fetchHistorial();
        alert("Cuarentena registrada exitosamente.");
      } catch (error) {
        console.error("Error al registrar cuarentena:", error);
        alert("Error al registrar la cuarentena.");
      } finally {
        loading.value = false;
      }
    };

    onMounted(async () => {
      await Promise.all([fetchEstanques(), fetchHistorial()]);
    });

    return {
      apiBase,
      estanques,
      historial,
      cuarentena,
      selectedEstanque,
      loading,
      errors,
      registrarCuarentena,
      resetForm,
    };
  },
};
</script>

<style scoped>
/* ========== Layout ========== */
.cuarentena { padding-block: 16px; }
.cz-header {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px;
}
.cz-header__title h1 { margin: 0 0 6px; }
.cz-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
  margin-top: 12px;
}
.cz-form { display: flex; flex-direction: column; gap: 14px; }
.cz-aside { align-self: start; }
.cz-tips { margin: 4px 0 0; padding-left: 18px; }
.cz-tips li { margin: 6px 0; }

/* ========== Fields ========== */
.field { display: flex; flex-direction: column; gap: 6px; }
.field > label { font-weight: 600; font-size: 14px; }
.field__meta { display: flex; justify-content: flex-end; }
.input, .select, .textarea {
  width: 100%; padding: 10px 12px;
  background: #f8f9fa; color: var(--color-text, #1f2937);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-md, 10px);
  font-size: 14px; transition: border-color .2s ease, box-shadow .2s ease, background .2s ease;
}
.input:focus, .select:focus, .textarea:focus {
  outline: none; background: #fff;
  box-shadow: var(--focus-ring, 0 0 0 3px rgba(0, 123, 255, .25));
  border-color: var(--color-primary, #007bff);
}
.error { color: #d11; }

/* ========== Buttons / Cards / Table  (alineado a tu appquaculture.css) ========== */
.card {
  background: var(--color-surface, #fff);
  color: var(--color-text, #1f2937);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-lg, 14px);
  box-shadow: var(--shadow-md, 0 4px 12px rgba(0,0,0,.10));
  padding: 16px;
}
.card__title { font-weight: 600; }
.card__sub { color: var(--color-muted, #6b7280); }

.btn {
  display: inline-flex; align-items: center; justify-content: center;
  padding: 10px 14px; font-weight: 600; font-size: 14px;
  border-radius: var(--radius-md, 10px); cursor: pointer; border: none;
  transition: transform .1s ease, filter .2s ease, background .2s ease;
}
.btn--lg { padding: 12px 18px; font-size: 15px; }
.btn--ghost { background: transparent; color: var(--color-text, #1f2937); }
.btn--ghost:hover { background: rgba(31,41,55,.06); }
.btn--accent { background: var(--color-accent, #3f55c2); color: #fff; }
.btn--accent:hover { filter: brightness(1.03); transform: translateY(-1px); }

/* ======= Tablas reutilizables (APLICA TAMBIÉN A PROYECCIÓN SEMANAL) ======= */
.table-wrap { overflow: auto; border: 1px solid var(--color-border, #e5e7eb); border-radius: var(--radius-lg, 14px); }
.table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 14px; }
.table th, .table td { padding: 10px 12px; border-bottom: 1px solid var(--color-border, #e5e7eb); text-align: left; background: var(--color-surface, #fff); }
.table th {
  position: sticky; top: 0; z-index: 1;
  background: #f8f9fa; color: #374151; font-weight: 600;
  box-shadow: 0 1px 0 var(--color-border, #e5e7eb);
}
.table--zebra tbody tr:nth-child(even) td { background: rgba(0,0,0,.02); }
.table tbody tr:hover td { background: #f3fdf6; } /* hover leve */
.table--sticky td:first-child, .table--sticky th:first-child {
  position: sticky; left: 0; z-index: 2;
  box-shadow: 1px 0 0 var(--color-border, #e5e7eb);
}
.table--sticky th:first-child { background: #f8f9fa; }

/* Responsive */
@media (max-width: 1100px) {
  .cz-grid { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .table { font-size: 13px; }
  .btn { font-size: 13px; padding: 9px 12px; }
}
</style>
