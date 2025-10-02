import { createRouter, createWebHistory } from 'vue-router';
import ProductionOne from '@/components/ProductionOne.vue';
import ReportOne from '@/components/ReportOne.vue';
import WarehouseOne from '@/components/WarehouseOne.vue';
import StatisticsOne from '@/components/StatisticsOne.vue';
import AccountingOne from '@/components/AccountingOne.vue';
import AccountOne from '@/components/AccountOne.vue';

import VentanaSiembra from '@/components/conector/VentanaSiembra.vue';
import VentanaAlimentar from '@/components/conector/VentanaAlimentar.vue';
import VentanaCalidadAgua from '@/components/conector/VentanaCalidadAgua.vue';
import VentanaCosecha from '@/components/conector/VentanaCosecha.vue';
import VentanaCrecimiento from '@/components/conector/VentanaCrecimiento.vue';
import VentanaCuarentena from '@/components/conector/VentanaCuarentena.vue';
import VentanaDieta from '@/components/conector/VentanaDieta.vue';
import VentanaEstanques from '@/components/conector/VentanaEstanques.vue';
import VentanaFichaTecnica from '@/components/conector/VentanaFichaTecnica.vue';
import VentanaTratamientos from '@/components/conector/VentanaTratamientos.vue';

import AgregarEstanque from '@/components/producción/AgregarEstanque.vue';
import Siembra from '@/components/producción/Siembra.vue';
import Alimentar from '@/components/producción/Alimentar.vue';
import CalidadAgua from '@/components/producción/CalidadAgua.vue';
import Dieta from '@/components/producción/Dieta.vue';
import FichaTecnica from '@/components/producción/FichaTecnica.vue';
import Crecimiento from '@/components/producción/Crecimiento.vue';
import Cosecha from '@/components/producción/Cosecha.vue';
import Proyeccion from '@/components/producción/Proyeccion.vue';
import Adicion from '@/components/producción/Adicion.vue';
import Tratamientos from '@/components/producción/Tratamientos.vue';
import Cuarentena from '@/components/producción/Cuarentena.vue';

import Inventario from '@/components/almacén/Inventario.vue';
import Proveedores from '@/components/almacén/Proveedores.vue';
import AltaMaterial from '@/components/almacén/AltaMaterial.vue';
import AltaProveedores from '@/components/almacén/AltaProveedores.vue';
import Entradas from '@/components/almacén/Entradas.vue';
import Salidas from '@/components/almacén/Salidas.vue';
import InventarioFisico from '@/components/almacén/InventarioFisico.vue';

import ANOVA from '@/components/estadístico/ANOVA.vue';
import KolmogorovSmirnov from '@/components/estadístico/Kolmogorov-Smirnov.vue';
import ShapiroWilk from '@/components/estadístico/Shapiro-Wilk.vue';

import RGeneral from '@/components/reporte/general.vue';
import REstanque from '@/components/reporte/estanque.vue';
import RLote from '@/components/reporte/lote.vue';
import RCrecimiento from '@/components/reporte/crecimiento.vue';
import RGananciaProduccionCiclo from '@/components/reporte/gpc.vue';
import RCalidadAgua from '@/components/reporte/calidad-agua.vue';

import CNomina from '@/components/contaduría/Nomina.vue';
import CSalarios from '@/components/contaduría/salarios.vue';
import CPagosServicios from '@/components/contaduría/pagos-servicios.vue';
import CCompras from '@/components/contaduría/Compras.vue';
import CMantenimiento from '@/components/contaduría/mantenimiento.vue';
import CCostosOperativos from '@/components/contaduría/costos-operativos.vue';
import CVentas from '@/components/contaduría/ventas.vue';

import CrearUsuario from '@/components/CrearUsuario.vue'
import { compare } from 'mathjs';
const routes = [

  {
    path: '/registrarusuario',
    component: CrearUsuario,
  },
  {
    path: '/producción',
    component: ProductionOne,
  },
  { 
    path: '/producción/siembra', 
    component: VentanaSiembra 
  },
  {
    path: '/producción/alimentar',
    component: VentanaAlimentar
  },
  { path: '/producción/calidad-agua', 
    component: VentanaCalidadAgua
  },
  {
    path: '/producción/cosecha',
    component: VentanaCosecha
  },
  {
    path: '/producción/crecimiento',
    component: VentanaCrecimiento
  },
  {
    path: '/producción/cuarentena',
    component: VentanaCuarentena
  },
  {
    path: '/producción/dieta',
    component: VentanaDieta
  },
  {
    path: '/producción/estanques',
    component: VentanaEstanques
  },
  {
    path: '/producción/ficha-técnica',
    component: VentanaFichaTecnica
  },
  {
    path: '/producción/tratamientos',
    component: VentanaTratamientos
  },
  
  { path: '/producción/agregar-estanque', 
    component: AgregarEstanque },
  { path: '/producción/siembra/registro/:id',
    component: Siembra, props: true,},
  { path: '/producción/alimentar/registro/:id', 
    component: Alimentar, props: true  },
  { path: '/producción/calidad-agua/registro/:id', 
    component: CalidadAgua, props: true },
  { path: '/producción/dieta/registro/:id', 
    component: Dieta, props: true  },
  { path: '/producción/ficha-técnica/registro/:id',
    component: FichaTecnica, props: true  },
  { path: '/producción/crecimiento/registro/:id', 
    component: Crecimiento, props: true  },
  { path: '/producción/cosecha/registro/:id', 
    component: Cosecha, props: true  },
  { path: '/producción/proyeccion/', 
    component: Proyeccion, props: true  },
  { path: '/producción/adición/registro/:id', 
    component: Adicion, props: true  },
  { path: '/producción/tratamientos/registro/:id', 
    component: Tratamientos, props: true  },
  { path: '/producción/cuarentena/registro/:id', 
    component: Cuarentena, props: true  },
  {
      path: '/reporte',
      component: ReportOne,
  },
  { path: '/reporte/General', 
    component: RGeneral },
  { path: '/reporte/Estanque', 
    component: REstanque },
  { path: '/reporte/Lote', 
    component: RLote },
  { path: '/reporte/Crecimiento', 
    component: RCrecimiento },
  { path: '/reporte/gpc', 
    component: RGananciaProduccionCiclo },
  { path: '/reporte/Calidad-agua', 
    component: RCalidadAgua },
  {
    path: '/almacén',
    component: WarehouseOne,
  },
  { path: '/almacén/inventario', 
    component: Inventario },
  { path: '/almacén/proveedores', 
    component: Proveedores },
  { path: '/almacén/alta-material', 
    component: AltaMaterial },
  { path: '/almacén/alta-proveedores', 
    component: AltaProveedores },
  { path: '/almacén/entradas', 
    component: Entradas },
  { path: '/almacén/salidas', 
    component: Salidas },
  { path: '/almacén/inventario-físico', 
    component: InventarioFisico },
  {
    path: '/estadistico',
    component: StatisticsOne,
  },
  { path: '/estadístico/ANOVA', 
    component: ANOVA },
  { path: '/estadístico/Kolmogorov-Smirnov', 
    component: KolmogorovSmirnov },
  { path: '/estadístico/Shapiro-Wilk',
    component: ShapiroWilk },
 
  {
    path: '/contaduría',
    component: AccountingOne,
  },
  { path: '/contaduría/nomina', 
    component: CNomina },
  { path: '/contaduría/salarios', 
    component: CSalarios },
  { path: '/contaduría/pagos-servicios', 
    component: CPagosServicios },
  { path: '/contaduría/compras', 
    component: CCompras },
  { path: '/contaduría/mantenimiento', 
    component: CMantenimiento },
  { path: '/contaduría/costos-operativos', 
    component: CCostosOperativos },
  { path: '/contaduría/ventas', 
    component: CVentas },
  {
    path: '/cuenta',
    component: AccountOne,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;