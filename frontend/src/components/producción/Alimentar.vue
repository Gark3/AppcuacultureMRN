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
        <label for="mortalidad">Mortalidad</label>
        <input type="number" id="mortalidad" v-model="registro.mortalidad" placeholder="Ingrese la mortalidad" />
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
import axios from '@/services/axios';

export default {
  props: ['id'], // ID de la siembra
  data() {
    return {
      alimentos: ["Pellets", "Harina de pescado", "Alimento balanceado"],
      registro: {
        tipo: "",
        lote: "",
        kg: null,
        mortalidad: null,
        clima: "",
        observacion: "",
        estado: 1,
        siembra: null,
        usuario: null,
        acuicola: null,
      },
    };
  },
  mounted() {
    const user = JSON.parse(localStorage.getItem("user"));
    this.registro.siembra = this.id;
    this.registro.usuario = user.usuario_id;
    this.registro.acuicola = user.acuicola;
  },
  methods: {
    async submitForm() {
      try {
        const response = await axios.post('/alimentar/', this.registro);
        alert("¡Registro de alimentación guardado exitosamente!");
        this.$router.push('/producción/alimentar');
      } catch (error) {
        console.error("Error al registrar alimentación:", error);
        alert("Ocurrió un error al guardar.");
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
