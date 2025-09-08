<template>
  <div class="registro-siembra">
    <h1>Calidad del Agua</h1>
    <form @submit.prevent="submitForm">
      <div class="form-group" v-for="(valor, campo) in calidadAgua" :key="campo">
        <label :for="campo">{{ etiquetas[campo] }}</label>
        <input
          type="number"
          :id="campo"
          v-model.number="calidadAgua[campo]"
          :placeholder="`Ingrese ${etiquetas[campo].toLowerCase()}`"
          step="0.01"
          required
        />
      </div>
      <button type="submit">Registrar Calidad del Agua</button>
    </form>
  </div>
</template>

<script>
import axios from '@/services/axios';

export default {
  props: ['id'], // id de la siembra
  data() {
    return {
      calidadAgua: {
        temperatura: null,
        oxigeno_disuelto: null,
        ph: null,
        nitritos: null,
        nitratos: null,
        sulfato: null,
        fosfato: null,
        cloro: null,
        salinidad: null,
        amonio: null
      },
      etiquetas: {
        temperatura: 'Temperatura (°C)',
        oxigeno_disuelto: 'Oxígeno disuelto (mg/L)',
        ph: 'pH',
        nitritos: 'Nitritos (mg/L)',
        nitratos: 'Nitratos (mg/L)',
        sulfato: 'Sulfato (mg/L)',
        fosfato: 'Fosfato (mg/L)',
        cloro: 'Cloro (mg/L)',
        salinidad: 'Salinidad (ppt)',
        amonio: 'Amonio (mg/L)'
      }
    };
  },
  methods: {
    async submitForm() {
      try {
        const user = JSON.parse(localStorage.getItem("user"));

        const payload = {
          ...this.calidadAgua,
          estado: 1,
          siembra: this.id,
          usuario: user.usuario_id,
          acuicola: user.acuicola
        };

        const response = await axios.post("/calidad-agua/", payload);
        alert("¡Calidad del agua registrada exitosamente!");
        this.$router.push("/producción/calidad-agua");
      } catch (error) {
        console.error("Error al registrar calidad del agua:", error);
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

