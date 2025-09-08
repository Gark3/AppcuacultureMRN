<template>
  <div class="registro-siembra">
    <h1>Registro de Siembra</h1>

    <form @submit.prevent="registrarSiembra">
      <!-- Selección de Especie -->
      <div class="form-group">
        <label for="especie">Selecciona la especie:</label>
        <select v-model="siembra.especie" id="especie" required>
          <optgroup label="Peces de agua dulce">
            <option>Tilapia - Oreochromis niloticus, Oreochromis aureus</option>
            <option>Tilapia GUASAVE - ALBERTO, Oreochromis aureus</option>
            <option>Carpa común - Cyprinus carpio</option>
            <option>Carpa plateada - Hypophthalmichthys molitrix</option>
            <option>Carpa herbívora - Ctenopharyngodon idella</option>
            <option>Pacu - Piaractus mesopotamicus</option>
            <option>Bagre o pez gato - Clarias gariepinus, Pangasius hypophthalmus</option>
          </optgroup>
          <optgroup label="Peces de agua salada">
            <option>Salmón del Atlántico - Salmo salar</option>
            <option>Trucha arcoíris - Oncorhynchus mykiss</option>
            <option>Lubina o robalo - Dicentrarchus labrax</option>
            <option>Dorada - Sparus aurata</option>
            <option>Lenguado - Solea solea</option>
          </optgroup>
          <optgroup label="Crustáceos">
            <option>Camarón blanco del Pacífico - Litopenaeus vannamei</option>
            <option>Camarón tigre gigante - Penaeus monodon</option>
            <option>Cangrejo azul - Callinectes sapidus</option>
          </optgroup>
          <optgroup label="Moluscos">
            <option>Mejillón azul - Mytilus edulis</option>
            <option>Ostra japonesa - Crassostrea gigas</option>
            <option>Vieira del Atlántico - Placopecten magellanicus</option>
            <option>Almeja japonesa - Ruditapes philippinarum</option>
          </optgroup>
        </select>
      </div>

      <!-- Detalles de Siembra -->
      <div class="form-group">
        <label for="numero-organismos">Número de organismos:</label>
        <input type="number" id="numero-organismos" v-model.number="siembra.cantidad_organismos" required />
      </div>

      <div class="form-group">
        <label for="peso-promedio">Peso promedio (g):</label>
        <input type="number" id="peso-promedio" v-model.number="siembra.peso_promedio" step="0.01" required />
      </div>

      <div class="form-group">
        <label for="tamano-promedio">Tamaño promedio (cm):</label>
        <input type="number" id="tamano-promedio" v-model.number="siembra.tamano_promedio" step="0.01" required />
      </div>

      <div class="form-group">
        <label for="etapa">Etapa:</label>
        <select id="etapa" v-model="siembra.etapa" required>
          <option>Maternidad</option>
          <option>Precria</option>
          <option>Engorda</option>
        </select>
      </div>

      <button type="submit" class="btn-registrar">Registrar Siembra</button>
    </form>
  </div>
</template>

<script>
import axios from "@/services/axios"; // Usa axios con token si ya lo tienes configurado

export default {
  props: ["id"], // Recibe el id del estanque desde la URL
  data() {
    return {
      siembra: {
        estanque: null,
        especie: '',
        cantidad_organismos: null,
        peso_promedio: null,
        tamano_promedio: null,
        etapa: '',
        usuario: null,
        acuicola: null,
        estado: 1
      }
    };
  },
  mounted() {
    const user = JSON.parse(localStorage.getItem("user"));
    this.siembra.estanque = this.id;
    this.siembra.usuario = user.usuario_id;
    this.siembra.acuicola = user.acuicola; // Asegúrate de incluirlo en el login
  },
  methods: {
    async registrarSiembra() {
      try {
        const response = await axios.post("/siembra/", this.siembra);
        alert("Siembra registrada correctamente.");
        this.$router.push("/estanques"); // o donde quieras redirigir
      } catch (error) {
        console.error("Error al registrar siembra:", error.response?.data || error.message);
        alert("Error al registrar siembra.");
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
