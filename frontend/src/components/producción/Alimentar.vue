<template>
  <div class="registro-siembra">
    <h1>Alimentación</h1>
    <form @submit.prevent="submitForm">
      <div class="form-group">
        <label for="tipoAlimento">Tipo de Alimento</label>
        <select id="tipoAlimento" v-model="registro.tipo" required>
          <option value="" disabled>Seleccione un tipo de alimento</option>
          <option v-for="alimento in alimentos" :key="alimento" :value="alimento">{{ alimento }}</option>
        </select>
      </div>
      <div class="form-group">
        <label for="lote">Lote</label>
        <input type="text" id="lote" v-model="registro.lote" placeholder="Ingrese el lote" required />
      </div>
      <div class="form-group">
        <label for="kg">Cantidad de Alimento (kg)</label>
        <input type="number" id="kg" v-model="registro.kg" placeholder="Ingrese la cantidad de alimento" step="0.01" required />
      </div>
      <div class="form-group">
        <label for="supervivencia">supervivencia</label>
        <input type="number" id="supervivencia" v-model="registro.supervivencia" placeholder="Ingrese la supervivencia" />
      </div>
      <div class="form-group">
        <label for="clima">Clima</label>
        <input type="text" id="clima" v-model="registro.clima" placeholder="Ingrese el clima actual" />
      </div>
      <div class="form-group">
        <label for="observacion">Comentarios</label>
        <textarea id="observacion" v-model="registro.observacion" placeholder="Ingrese algún comentario"></textarea>
      </div>
      <button type="submit">Registrar Alimentación</button>
    </form>
  </div>
</template>

<script>
import api from '@/services/axios'; // tu instancia con interceptores

export default {
  props: ['id'], // ID de la siembra (viene por ruta)
  data() {
    return {
      alimentos: ["Pellets", "Harina de pescado", "Alimento balanceado"],
      registro: {
        tipo: "",
        lote: "",
        kg: null,
        supervivencia: null,
        clima: "",
        observacion: "",
        // estado: 1, // si en el modelo tiene default=1, ni lo mandes; si no, descomenta
      },
      guardando: false,
    };
  },
  mounted() {
    // Forzamos la siembra a número desde la prop
    // (no lo guardo en registro para no mezclar campos controlados por back)
    this.siembraId = Number(this.id);
  },
  methods: {
    async submitForm() {
      try {
        this.guardando = true;

        // Validación básica
        if (!this.registro.tipo || !this.siembraId) {
          alert("Selecciona un tipo de alimento y verifica la siembra.");
          return;
        }

        // Armamos el payload SIN usuario/acuicola (los pone el backend)
        const payload = {
          tipo: String(this.registro.tipo).trim(),
          lote: this.registro.lote ? String(this.registro.lote).trim() : "",
          kg: this.registro.kg != null ? Number(this.registro.kg) : null,
          supervivencia: this.registro.supervivencia != null ? Number(this.registro.supervivencia) : null,
          clima: this.registro.clima ? String(this.registro.clima).trim() : "",
          observacion: this.registro.observacion ? String(this.registro.observacion).trim() : "",
          siembra: this.siembraId,         // <- numérico
          // estado: 1,                     // <- solo si tu modelo lo exige explícitamente
        };

        const { data } = await api.post('/alimentar/', payload);

        alert("¡Registro de alimentación guardado exitosamente!");
        // Redirección: ajusta la ruta si tu router no usa acentos
        this.$router.push('/producción/alimentar');
      } catch (error) {
        console.error("Error al registrar alimentación:", error);
        // Puedes mostrar un detalle si viene del backend:
        const msg = error?.response?.data?.detail || "Ocurrió un error al guardar.";
        alert(msg);
      } finally {
        this.guardando = false;
      }
    }
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

  input, select {
    width: 100%;
    padding: 12px;
    box-sizing: border-box;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 14px;
    transition: all 0.3s ease-in-out;
    background: #f8f9fa;
  }

  input:focus, select:focus {
    border-color: #28a745;
    outline: none;
    box-shadow: 0px 0px 5px rgba(40, 167, 69, 0.4);
  }

  button {
    background-color: #28a745;
    color: white;
    border: none;
    padding: 12px 15px;
    font-size: 16px;
    cursor: pointer;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s ease-in-out;
    text-transform: uppercase;
    letter-spacing: 1px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  button:hover {
    background-color: #218838;
    transform: scale(1.05);
  }

  button:active {
    transform: scale(0.98);
  }

  /* Responsive Design */
  @media (max-width: 768px) {
    .registro-siembra {
      padding: 20px;
    }

    h1 {
      font-size: 20px;
    }

    button {
      font-size: 14px;
      padding: 10px;
    }
  }
</style>
