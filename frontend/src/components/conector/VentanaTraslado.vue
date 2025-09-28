<template>
  <div class="ventana-estanques">
    <h1>Lista de Estanques</h1>
    <div v-if="estanques.length">
      <button v-for="estanque in estanques" :key="estanque.id" @click="irACalidadAgua(estanque.id)">
        {{ estanque.nombre }}
      </button>
    </div>
    <p v-else>Cargando estanques...</p>
  </div>
</template>
  
  <script>
  import axios from 'axios';
import { useRouter } from 'vue-router';

export default {
  data() {
    return {
      estanques: []
    };
  },
  setup() {
    const router = useRouter();
    return { router };
  },
  created() {
    this.obtenerEstanques();
  },
  methods: {
    async obtenerEstanques() {
      try {
        const response = await axios.get("/estanque/");
        this.estanques = response.data;

      } catch (error) {
        console.error('Error al obtener estanques:', error);
      }
    },
    irACalidadAgua(id) {
      this.router.push({ path: '/calidad-agua', query: { estanque_id: id } });
    }
  }
};
  </script>
  
  <style scoped>
  .ventana-estanques {
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

  