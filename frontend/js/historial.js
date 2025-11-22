// ========================================
// CONFIGURACIÓN DE LA API
// ========================================
const API_URL = 'http://localhost:5000';
let asistenciasGlobales = [];
let asistenciasFiltradas = [];
let paginaActual = 1;
const registrosPorPagina = 10;

// ========================================
// FUNCIÓN PRINCIPAL: CARGAR ASISTENCIAS
// ========================================
async function cargarAsistencias() {
    try {
        mostrarCargando(true);
        
        const response = await fetch(`${API_URL}/listAsistencia`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Manejar la estructura de respuesta
        asistenciasGlobales = Array.isArray(data) ? data : [];
        asistenciasFiltradas = [...asistenciasGlobales];
        
        console.log('✅ Asistencias cargadas:', asistenciasGlobales.length);
        
        mostrarAsistencias();
        actualizarFechaActualizacion();
        
    } catch (error) {
        console.error('❌ Error al cargar asistencias:', error);
        mostrarError(`No se pudieron cargar las asistencias. Verifica que el servidor Flask esté ejecutándose en ${API_URL}. Error: ${error.message}`);
    } finally {
        mostrarCargando(false);
    }
}

// ========================================
// MOSTRAR ASISTENCIAS EN TABLA Y TARJETAS
// ========================================
function mostrarAsistencias() {
    const inicio = (paginaActual - 1) * registrosPorPagina;
    const fin = inicio + registrosPorPagina;
    const asistenciasPagina = asistenciasFiltradas.slice(inicio, fin);

    // TABLA DESKTOP
    const tbodyDesktop = document.getElementById('tablaAsistenciasDesktop');
    if (tbodyDesktop) {
        tbodyDesktop.innerHTML = '';
        
        if (asistenciasPagina.length === 0) {
            tbodyDesktop.innerHTML = '<tr><td colspan="6" class="has-text-centered has-text-grey">No hay registros de asistencia disponibles</td></tr>';
        } else {
            asistenciasPagina.forEach(asistencia => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${asistencia.id || '---'}</strong></td>
                    <td>${asistencia.nombre_estudiante || 'Sin nombre'}</td>
                    <td>${formatearFecha(asistencia.fecha)}</td>
                    <td><span class="icon-text">
                        <span class="icon"><i class="fas fa-clock"></i></span>
                        <span>${asistencia.hora_entrada || '---'}</span>
                    </span></td>
                    <td>${getTagEstado(asistencia.asistencia)}</td>
                    <td>${asistencia.observaciones || 'Sin observaciones'}</td>
                `;
                tbodyDesktop.appendChild(tr);
            });
        }
    }

    // TARJETAS MÓVIL
    const contenedorMovil = document.getElementById('tarjetasAsistenciasMovil');
    if (contenedorMovil) {
        contenedorMovil.innerHTML = '';
        
        if (asistenciasPagina.length === 0) {
            contenedorMovil.innerHTML = `
                <div class="notification is-info is-light">
                    <span class="icon"><i class="fas fa-info-circle"></i></span>
                    <span>No hay registros para mostrar</span>
                </div>
            `;
        } else {
            asistenciasPagina.forEach(asistencia => {
                const card = crearTarjetaMovil(asistencia);
                contenedorMovil.insertAdjacentHTML('beforeend', card);
            });
        }
    }

    // PAGINACIÓN
    mostrarPaginacion();
}

// ========================================
// CREAR TARJETA MÓVIL
// ========================================
function crearTarjetaMovil(asistencia) {
    return `
        <div class="mobile-card">
            <div class="mobile-card-date">
                <i class="fas fa-calendar-alt"></i> ${formatearFecha(asistencia.fecha)}
            </div>
            <div class="mobile-card-row">
                <span class="mobile-card-label"><i class="fas fa-user"></i> Nombres:</span>
                <span class="mobile-card-value"><strong>${asistencia.nombre_estudiante || 'Sin nombre'}</strong></span>
            </div>
            <div class="mobile-card-row">
                <span class="mobile-card-label"><i class="fas fa-id-card"></i> ID:</span>
                <span class="mobile-card-value">${asistencia.id || '---'}</span>
            </div>
            <div class="mobile-card-row">
                <span class="mobile-card-label"><i class="fas fa-check-circle"></i> Estado:</span>
                <span class="mobile-card-value">${getTagEstado(asistencia.asistencia)}</span>
            </div>
            <div class="mobile-card-row">
                <span class="mobile-card-label"><i class="fas fa-clock"></i> Hora:</span>
                <span class="mobile-card-value">${asistencia.hora_entrada || '---'}</span>
            </div>
            <div class="mobile-card-row">
                <span class="mobile-card-label"><i class="fas fa-comment"></i> Observaciones:</span>
                <span class="mobile-card-value">${asistencia.observaciones || 'Sin observaciones'}</span>
            </div>
        </div>
    `;
}

// ========================================
// FORMATEAR FECHA
// ========================================
function formatearFecha(fecha) {
    if (!fecha) return '---';
    try {
        const date = new Date(fecha + 'T00:00:00');
        const opciones = { year: 'numeric', month: '2-digit', day: '2-digit' };
        return date.toLocaleDateString('es-PE', opciones);
    } catch (error) {
        console.error('Error al formatear fecha:', error);
        return fecha;
    }
}

// ========================================
// OBTENER TAG DE ESTADO
// ========================================
function getTagEstado(estado) {
    const estados = {
        'Presente': '<span class="tag is-success is-light"><i class="fas fa-check mr-1"></i>Presente</span>',
        'Ausente': '<span class="tag is-danger is-light"><i class="fas fa-times mr-1"></i>Ausente</span>'
    };
    return estados[estado] || '<span class="tag is-light">---</span>';
}

// ========================================
// FILTRAR ASISTENCIAS
// ========================================
function aplicarFiltros(event) {
    event.preventDefault();
    
    const esMovil = window.innerWidth < 1024;
    const fechaInicio = document.getElementById(esMovil ? 'fechaInicioMovil' : 'fechaInicioDesktop').value;
    const fechaFin = document.getElementById(esMovil ? 'fechaFinMovil' : 'fechaFinDesktop').value;
    const nombreBusqueda = document.getElementById(esMovil ? 'colegioMovil' : 'colegioDesktop').value.toLowerCase().trim();

    asistenciasFiltradas = asistenciasGlobales.filter(asistencia => {
        let cumpleFecha = true;
        let cumpleNombre = true;

        // Filtro por fecha de inicio
        if (fechaInicio && asistencia.fecha) {
            cumpleFecha = asistencia.fecha >= fechaInicio;
        }

        // Filtro por fecha fin
        if (fechaFin && asistencia.fecha && cumpleFecha) {
            cumpleFecha = asistencia.fecha <= fechaFin;
        }

        // Filtro por nombre de estudiante
        if (nombreBusqueda && asistencia.nombre_estudiante) {
            cumpleNombre = asistencia.nombre_estudiante.toLowerCase().includes(nombreBusqueda);
        }

        return cumpleFecha && cumpleNombre;
    });

    paginaActual = 1;
    mostrarAsistencias();
    
    console.log(`🔍 Filtros aplicados: ${asistenciasFiltradas.length} de ${asistenciasGlobales.length} registros`);
}

// ========================================
// LIMPIAR FILTROS
// ========================================
function limpiarFiltros() {
    // Desktop
    const fechaInicioDesktop = document.getElementById('fechaInicioDesktop');
    const fechaFinDesktop = document.getElementById('fechaFinDesktop');
    const colegioDesktop = document.getElementById('colegioDesktop');
    
    if (fechaInicioDesktop) fechaInicioDesktop.value = '';
    if (fechaFinDesktop) fechaFinDesktop.value = '';
    if (colegioDesktop) colegioDesktop.value = '';
    
    // Móvil
    const fechaInicioMovil = document.getElementById('fechaInicioMovil');
    const fechaFinMovil = document.getElementById('fechaFinMovil');
    const colegioMovil = document.getElementById('colegioMovil');
    
    if (fechaInicioMovil) fechaInicioMovil.value = '';
    if (fechaFinMovil) fechaFinMovil.value = '';
    if (colegioMovil) colegioMovil.value = '';

    asistenciasFiltradas = [...asistenciasGlobales];
    paginaActual = 1;
    mostrarAsistencias();
    
    console.log('🔄 Filtros limpiados');
}

// ========================================
// PAGINACIÓN
// ========================================
function mostrarPaginacion() {
    const totalPaginas = Math.ceil(asistenciasFiltradas.length / registrosPorPagina);
    const paginacionDesktop = document.getElementById('paginacionDesktop');
    
    if (!paginacionDesktop) return;
    
    if (totalPaginas <= 1) {
        paginacionDesktop.style.display = 'none';
        return;
    }

    paginacionDesktop.style.display = 'flex';

    const btnAnterior = document.getElementById('btnAnterior');
    const btnSiguiente = document.getElementById('btnSiguiente');
    const listaPaginas = document.getElementById('listaPaginas');

    // Botón anterior
    if (btnAnterior) {
        if (paginaActual === 1) {
            btnAnterior.setAttribute('disabled', 'disabled');
            btnAnterior.classList.add('is-disabled');
        } else {
            btnAnterior.removeAttribute('disabled');
            btnAnterior.classList.remove('is-disabled');
            btnAnterior.onclick = () => cambiarPagina(paginaActual - 1);
        }
    }

    // Botón siguiente
    if (btnSiguiente) {
        if (paginaActual === totalPaginas) {
            btnSiguiente.setAttribute('disabled', 'disabled');
            btnSiguiente.classList.add('is-disabled');
        } else {
            btnSiguiente.removeAttribute('disabled');
            btnSiguiente.classList.remove('is-disabled');
            btnSiguiente.onclick = () => cambiarPagina(paginaActual + 1);
        }
    }

    // Lista de páginas (mostrar máximo 5 páginas)
    if (listaPaginas) {
        listaPaginas.innerHTML = '';
        
        let inicio = Math.max(1, paginaActual - 2);
        let fin = Math.min(totalPaginas, inicio + 4);
        
        if (fin - inicio < 4) {
            inicio = Math.max(1, fin - 4);
        }
        
        for (let i = inicio; i <= fin; i++) {
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.classList.add('pagination-link');
            
            if (i === paginaActual) {
                a.classList.add('is-current');
                a.setAttribute('aria-current', 'page');
            }
            
            a.textContent = i;
            a.setAttribute('aria-label', `Página ${i}`);
            a.onclick = () => cambiarPagina(i);
            
            li.appendChild(a);
            listaPaginas.appendChild(li);
        }
    }
}

function cambiarPagina(nuevaPagina) {
    paginaActual = nuevaPagina;
    mostrarAsistencias();
    window.scrollTo({ top: 0, behavior: 'smooth' });
    console.log(`📄 Página cambiada a: ${nuevaPagina}`);
}

// ========================================
// MOSTRAR CARGANDO
// ========================================
function mostrarCargando(mostrar) {
    const tbodyDesktop = document.getElementById('tablaAsistenciasDesktop');
    const contenedorMovil = document.getElementById('tarjetasAsistenciasMovil');
    
    if (mostrar) {
        const spinnerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <p class="has-text-grey mt-3">Cargando datos...</p>
            </div>
        `;
        
        if (tbodyDesktop) {
            tbodyDesktop.innerHTML = `<tr><td colspan="6">${spinnerHTML}</td></tr>`;
        }
        
        if (contenedorMovil) {
            contenedorMovil.innerHTML = spinnerHTML;
        }
    }
}

// ========================================
// MOSTRAR ERROR
// ========================================
function mostrarError(mensaje) {
    const tbodyDesktop = document.getElementById('tablaAsistenciasDesktop');
    const contenedorMovil = document.getElementById('tarjetasAsistenciasMovil');
    
    const errorHTML = `
        <div class="notification is-danger is-light">
            <button class="delete" onclick="this.parentElement.remove()"></button>
            <span class="icon has-text-danger">
                <i class="fas fa-exclamation-triangle"></i>
            </span>
            <span><strong>Error:</strong> ${mensaje}</span>
            <br>
            <small class="mt-2">
                <strong>Solución:</strong> Asegúrate de que el servidor Flask esté ejecutándose con <code>python api.py</code>
            </small>
        </div>
    `;
    
    if (tbodyDesktop) {
        tbodyDesktop.innerHTML = `<tr><td colspan="6">${errorHTML}</td></tr>`;
    }
    
    if (contenedorMovil) {
        contenedorMovil.innerHTML = errorHTML;
    }
}

// ========================================
// ACTUALIZAR FECHA DE ACTUALIZACIÓN
// ========================================
function actualizarFechaActualizacion() {
    const fechaElement = document.getElementById('fechaActualizacion');
    if (fechaElement) {
        const ahora = new Date();
        const opciones = { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        };
        const fechaFormateada = ahora.toLocaleDateString('es-PE', opciones);
        fechaElement.innerHTML = `
            <span class="icon-text">
                <span class="icon has-text-info"><i class="fas fa-sync-alt"></i></span>
                <span>Datos actualizados al ${fechaFormateada}</span>
            </span>
        `;
    }
}

// ========================================
// EVENTOS AL CARGAR LA PÁGINA
// ========================================
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Iniciando aplicación de Historial de Asistencias...');
    
    // Cargar asistencias inicial
    cargarAsistencias();

    // Eventos de formularios
    const filtrosDesktop = document.getElementById('filtrosDesktop');
    const filtrosMovil = document.getElementById('filtrosMovil');
    
    if (filtrosDesktop) {
        filtrosDesktop.addEventListener('submit', aplicarFiltros);
    }
    
    if (filtrosMovil) {
        filtrosMovil.addEventListener('submit', aplicarFiltros);
    }

    // Auto-actualización cada 30 segundos
    setInterval(() => {
        console.log('🔄 Auto-actualización de datos...');
        cargarAsistencias();
    }, 30000);
    
    console.log('✅ Aplicación iniciada correctamente');
});

// ========================================
// MANEJO DE ERRORES GLOBALES
// ========================================
window.addEventListener('error', (event) => {
    console.error('❌ Error global capturado:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('❌ Promesa rechazada no manejada:', event.reason);
});