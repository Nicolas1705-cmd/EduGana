/**
 * Nombre del archivo: historial.js
 * Descripción: Consume el endpoint GET /listAsistencia para mostrar el historial.
 */

// ==========================================
// 1. CONFIGURACIÓN
// ==========================================
const API_URL = 'http://172.60.15.207:5000/'; // Asegúrate que sea el puerto de tu Flask
const ENDPOINT_HISTORIAL = '/listAsistencia'; // Tu ruta específica GET

// Variables de estado
let historialGlobal = [];
let historialFiltrado = [];
let paginaActual = 1;
const registrosPorPagina = 10;

// ==========================================
// 2. INICIALIZACIÓN (Al cargar la página)
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    // Cargar datos inmediatamente
    cargarHistorial();

    // Configurar listeners de los filtros (Desktop y Móvil)
    const formDesktop = document.getElementById('filtrosDesktop');
    const formMovil = document.getElementById('filtrosMovil');

    if (formDesktop) formDesktop.addEventListener('submit', filtrarHistorial);
    if (formMovil) formMovil.addEventListener('submit', filtrarHistorial);

    // Refresco automático (Opcional: cada 30 seg)
    setInterval(cargarHistorial, 30000);
});

// ==========================================
// 3. CONSUMO DEL API (GET /listAsistencia)
// ==========================================
async function cargarHistorial() {
    try {
        mostrarCargando(true);

        // Petición GET al backend Python
        const response = await fetch(`${API_URL}${ENDPOINT_HISTORIAL}`);

        if (!response.ok) {
            throw new Error(`Error de conexión: ${response.status}`);
        }

        // Tu Python devuelve una lista directa: [ {id, nombre_estudiante...}, ... ]
        // O un JSON: { data: [...] }. Este código soporta ambos.
        const data = await response.json();
        
        historialGlobal = Array.isArray(data) ? data : (data.data || []);
        
        // Al inicio, lo filtrado es igual a todo lo recibido
        historialFiltrado = [...historialGlobal];

        // Renderizar en HTML
        renderizarVista();
        actualizarFechaHora();

    } catch (error) {
        console.error('Error cargando historial:', error);
        mostrarError('No se pudo cargar el historial de asistencias.');
    } finally {
        mostrarCargando(false);
    }
}

// ==========================================
// 4. RENDERIZADO (Pintar tabla y tarjetas)
// ==========================================
function renderizarVista() {
    const inicio = (paginaActual - 1) * registrosPorPagina;
    const fin = inicio + registrosPorPagina;
    const datosPagina = historialFiltrado.slice(inicio, fin);

    // 4.1 Renderizar Tabla Desktop
    const tbody = document.getElementById('tablaAsistenciasDesktop');
    if (tbody) {
        tbody.innerHTML = '';
        
        if (datosPagina.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="has-text-centered py-4">No se encontraron registros.</td></tr>';
        } else {
            datosPagina.forEach(fila => {
                // Mapeo exacto de tus columnas SQL a la Tabla HTML
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${fila.id || fila.estudiante_id}</td>
                    <td class="has-text-weight-semibold is-uppercase-text">${fila.nombre_estudiante || 'Desconocido'}</td>
                    <td>${formatearFecha(fila.fecha)}</td>
                    <td>${fila.hora_entrada || '--:--'}</td>
                    <td>${generarEtiquetaEstado(fila.asistencia)}</td>
                    <td>${fila.colegio || '---'}</td> 
                `;
                tbody.appendChild(tr);
            });
        }
    }

    // 4.2 Renderizar Tarjetas Móvil
    const contenedorMovil = document.getElementById('tarjetasAsistenciasMovil');
    if (contenedorMovil) {
        contenedorMovil.innerHTML = '';

        if (datosPagina.length === 0) {
            contenedorMovil.innerHTML = '<div class="notification is-light has-text-centered">Sin datos</div>';
        } else {
            datosPagina.forEach(fila => {
                contenedorMovil.insertAdjacentHTML('beforeend', `
                    <div class="mobile-card">
                        <div class="mobile-card-date level is-mobile">
                            <div class="level-left">
                                <span class="icon mr-2"><i class="fas fa-calendar"></i></span>
                                <b>${formatearFecha(fila.fecha)}</b>
                            </div>
                            <div class="level-right">
                                ${generarEtiquetaEstado(fila.asistencia)}
                            </div>
                        </div>
                        <div class="mobile-card-row">
                            <span class="mobile-card-label">Nombre:</span>
                            <span class="mobile-card-value is-uppercase-text">${fila.nombre_estudiante}</span>
                        </div>
                         <div class="mobile-card-row">
                            <span class="mobile-card-label">Hora:</span>
                            <span class="mobile-card-value">${fila.hora_entrada}</span>
                        </div>
                        <div class="mobile-card-row">
                            <span class="mobile-card-label">Colegio:</span>
                            <span class="mobile-card-value">${fila.colegio || '---'}</span>
                        </div>
                    </div>
                `);
            });
        }
    }

    // 4.3 Actualizar Paginación
    renderizarPaginacion();
}

// ==========================================
// 5. FILTROS
// ==========================================
function filtrarHistorial(e) {
    if(e) e.preventDefault();

    const esMovil = window.innerWidth < 1024;
    
    // Obtener valores según la vista
    const fInicio = document.getElementById(esMovil ? 'fechaInicioMovil' : 'fechaInicioDesktop').value;
    const fFin = document.getElementById(esMovil ? 'fechaFinMovil' : 'fechaFinDesktop').value;
    const textoColegio = document.getElementById(esMovil ? 'colegioMovil' : 'colegioDesktop').value.toLowerCase();

    historialFiltrado = historialGlobal.filter(item => {
        let pasaFecha = true;
        let pasaColegio = true;

        // Filtro Fecha
        if (fInicio && item.fecha < fInicio) pasaFecha = false;
        if (fFin && item.fecha > fFin) pasaFecha = false;

        // Filtro Colegio (Búsqueda parcial)
        if (textoColegio && item.colegio) {
            pasaColegio = item.colegio.toLowerCase().includes(textoColegio);
        } else if (textoColegio && !item.colegio) {
            pasaColegio = false; // Buscamos algo pero el registro no tiene colegio
        }

        return pasaFecha && pasaColegio;
    });

    paginaActual = 1; // Volver a la primera página tras filtrar
    renderizarVista();
}

function limpiarFiltros() {
    // Limpiar inputs
    const ids = ['fechaInicioDesktop', 'fechaFinDesktop', 'colegioDesktop', 
                 'fechaInicioMovil', 'fechaFinMovil', 'colegioMovil'];
    ids.forEach(id => {
        const input = document.getElementById(id);
        if(input) input.value = '';
    });

    // Resetear datos
    historialFiltrado = [...historialGlobal];
    paginaActual = 1;
    renderizarVista();
}

// ==========================================
// 6. UTILIDADES Y AYUDAS VISUALES
// ==========================================

// Convierte el texto de la BD ('Presente', 'Ausente', booleanos) en HTML Bulma
function generarEtiquetaEstado(estado) {
    const st = String(estado).toLowerCase(); // Convertir a string y minúsculas para comparar seguro

    if (st.includes('presente') || st === 'true') {
        return `<span class="tag is-success is-light"><i class="fas fa-check mr-1"></i> Presente</span>`;
    } 
    if (st.includes('ausente') || st === 'false') {
        return `<span class="tag is-danger is-light"><i class="fas fa-times mr-1"></i> Ausente</span>`;
    }
    // Si tienes estados de entrada/salida
    if (st.includes('entrada')) return `<span class="tag is-info is-light">Entrada</span>`;
    if (st.includes('salida')) return `<span class="tag is-warning is-light">Salida</span>`;

    return `<span class="tag is-light">${estado}</span>`;
}

// Formatea YYYY-MM-DD a DD/MM/YYYY
function formatearFecha(fechaStr) {
    if (!fechaStr) return '--/--/----';
    const partes = fechaStr.split('-'); 
    // Si viene como 2025-10-25
    if (partes.length === 3) return `${partes[2]}/${partes[1]}/${partes[0]}`;
    return fechaStr;
}

// Manejo del spinner de carga
function mostrarCargando(activo) {
    const spinners = document.querySelectorAll('.loading-spinner');
    spinners.forEach(s => s.style.display = activo ? 'flex' : 'none');
}

// Manejo de errores visuales
function mostrarError(mensaje) {
    const tbody = document.getElementById('tablaAsistenciasDesktop');
    const movil = document.getElementById('tarjetasAsistenciasMovil');
    const alerta = `<div class="notification is-danger is-light">${mensaje}</div>`;

    if(tbody) tbody.innerHTML = `<tr><td colspan="6">${alerta}</td></tr>`;
    if(movil) movil.innerHTML = alerta;
}

function actualizarFechaHora() {
    const el = document.getElementById('fechaActualizacion');
    if(el) {
        const now = new Date();
        el.innerText = `Actualizado: ${now.toLocaleDateString()} ${now.toLocaleTimeString()}`;
    }
}

// ==========================================
// 7. PAGINACIÓN
// ==========================================
function renderizarPaginacion() {
    const paginacionDiv = document.getElementById('paginacionDesktop');
    if(!paginacionDiv) return;

    const totalPaginas = Math.ceil(historialFiltrado.length / registrosPorPagina);

    if (totalPaginas <= 1) {
        paginacionDiv.style.display = 'none';
        return;
    }
    paginacionDiv.style.display = 'flex';

    const ul = document.getElementById('listaPaginas');
    const btnPrev = document.getElementById('btnAnterior');
    const btnNext = document.getElementById('btnSiguiente');

    // Configurar botones
    btnPrev.onclick = () => cambiarPagina(paginaActual - 1);
    btnPrev.toggleAttribute('disabled', paginaActual === 1);

    btnNext.onclick = () => cambiarPagina(paginaActual + 1);
    btnNext.toggleAttribute('disabled', paginaActual === totalPaginas);

    // Dibujar números
    ul.innerHTML = '';
    // Lógica simplificada: mostrar todas o rango (aquí muestro un rango simple)
    for (let i = 1; i <= totalPaginas; i++) {
        // Mostrar primera, última y las cercanas a la actual
        if (i === 1 || i === totalPaginas || (i >= paginaActual - 1 && i <= paginaActual + 1)) {
            const li = document.createElement('li');
            li.innerHTML = `<a class="pagination-link ${i === paginaActual ? 'is-current' : ''}" onclick="cambiarPagina(${i})">${i}</a>`;
            ul.appendChild(li);
        }
    }
}

function cambiarPagina(nuevaPagina) {
    const totalPaginas = Math.ceil(historialFiltrado.length / registrosPorPagina);
    if (nuevaPagina >= 1 && nuevaPagina <= totalPaginas) {
        paginaActual = nuevaPagina;
        renderizarVista();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// Exportar funciones globales para usar en onclick del HTML (ej. Limpiar)
window.limpiarFiltros = limpiarFiltros;
window.cargarMasRegistros = () => {}; // Dejar vacío si no usas "cargar más" en móvil