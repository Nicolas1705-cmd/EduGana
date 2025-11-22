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
        
        const response = await fetch(`${API_URL}/asistencias`);
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        asistenciasGlobales = Array.isArray(data) ? data : [];
        asistenciasFiltradas = [...asistenciasGlobales];
        
        mostrarAsistencias();
        actualizarFechaActualizacion();
        
    } catch (error) {
        console.error('Error al cargar asistencias:', error);
        mostrarError(`No se pudieron cargar las asistencias. ${error.message}`);
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
            tbodyDesktop.innerHTML = '<tr><td colspan="6" class="has-text-centered">No hay registros de asistencia</td></tr>';
        } else {
            asistenciasPagina.forEach(asistencia => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${asistencia.id || '---'}</td>
                    <td>${asistencia.nombre_estudiante || 'Sin nombre'}</td>
                    <td>${formatearFecha(asistencia.fecha)}</td>
                    <td>${asistencia.hora_entrada || '---'}</td>
                    <td>${getTagEstado(asistencia.asistencia)}</td>
                    <td><strong>${asistencia.observaciones || 'Sin especificar'}</strong></td>
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
            contenedorMovil.innerHTML = '<p class="has-text-centered has-text-grey">No hay registros para mostrar</p>';
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
                <span class="mobile-card-label">Nombres:</span>
                <span class="mobile-card-value">${asistencia.nombre_estudiante || 'Sin nombre'}</span>
            </div>
            <div class="mobile-card-row">
                <span class="mobile-card-label">ID.Reg:</span>
                <span class="mobile-card-value">${asistencia.estudiante_id || '---'}</span>
            </div>
            <div class="mobile-card-row">
                <span class="mobile-card-label">Movimiento:</span>
                <span class="mobile-card-value">${getTagEstado(asistencia.asistencia)}</span>
            </div>
            <div class="mobile-card-row">
                <span class="mobile-card-label">Hora:</span>
                <span class="mobile-card-value">${asistencia.hora_entrada || '---'}</span>
            </div>
            <div class="mobile-card-row">
                <span class="mobile-card-label">Observaciones:</span>
                <span class="mobile-card-value">${asistencia.observaciones || 'Sin especificar'}</span>
            </div>
        </div>
    `;
}

// ========================================
// FORMATEAR FECHA
// ========================================
function formatearFecha(fecha) {
    if (!fecha) return '---';
    const date = new Date(fecha + 'T00:00:00');
    const opciones = { year: 'numeric', month: '2-digit', day: '2-digit' };
    return date.toLocaleDateString('es-PE', opciones);
}

// ========================================
// OBTENER TAG DE ESTADO
// ========================================
function getTagEstado(estado) {
    const estados = {
        'Presente': '<span class="tag is-success is-light">Presente</span>',
        'Ausente': '<span class="tag is-danger is-light">Ausente</span>'
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
    const colegio = document.getElementById(esMovil ? 'colegioMovil' : 'colegioDesktop').value.toLowerCase();

    asistenciasFiltradas = asistenciasGlobales.filter(asistencia => {
        let cumpleFecha = true;
        let cumpleColegio = true;

        // Filtro por fecha de inicio
        if (fechaInicio && asistencia.fecha) {
            cumpleFecha = asistencia.fecha >= fechaInicio;
        }

        // Filtro por fecha fin
        if (fechaFin && asistencia.fecha && cumpleFecha) {
            cumpleFecha = asistencia.fecha <= fechaFin;
        }

        // Filtro por colegio (usando observaciones)
        if (colegio && asistencia.observaciones) {
            cumpleColegio = asistencia.observaciones.toLowerCase().includes(colegio);
        }

        return cumpleFecha && cumpleColegio;
    });

    paginaActual = 1;
    mostrarAsistencias();
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
        } else {
            btnAnterior.removeAttribute('disabled');
            btnAnterior.onclick = () => cambiarPagina(paginaActual - 1);
        }
    }

    // Botón siguiente
    if (btnSiguiente) {
        if (paginaActual === totalPaginas) {
            btnSiguiente.setAttribute('disabled', 'disabled');
        } else {
            btnSiguiente.removeAttribute('disabled');
            btnSiguiente.onclick = () => cambiarPagina(paginaActual + 1);
        }
    }

    // Lista de páginas
    if (listaPaginas) {
        listaPaginas.innerHTML = '';
        for (let i = 1; i <= totalPaginas; i++) {
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.classList.add('pagination-link');
            if (i === paginaActual) {
                a.classList.add('is-current');
            }
            a.textContent = i;
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
}

// ========================================
// CARGAR MÁS REGISTROS (MÓVIL)
// ========================================
function cargarMasRegistros() {
    if (paginaActual * registrosPorPagina < asistenciasFiltradas.length) {
        paginaActual++;
        mostrarAsistencias();
    }
}

// ========================================
// MOSTRAR CARGANDO
// ========================================
function mostrarCargando(mostrar) {
    const tbodyDesktop = document.getElementById('tablaAsistenciasDesktop');
    const contenedorMovil = document.getElementById('tarjetasAsistenciasMovil');
    
    const spinnerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
        </div>
    `;
    
    if (mostrar) {
        if (tbodyDesktop) {
            tbodyDesktop.innerHTML = `<tr><td colspan="6" class="has-text-centered">${spinnerHTML}</td></tr>`;
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
            <span class="icon"><i class="fas fa-exclamation-triangle"></i></span>
            <span>${mensaje}</span>
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
    const elementoFecha = document.getElementById('fechaActualizacion');
    if (!elementoFecha) return;
    
    const ahora = new Date();
    const opciones = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    const fechaFormateada = ahora.toLocaleDateString('es-PE', opciones);
    elementoFecha.textContent = `Datos actualizados al ${fechaFormateada}`;
}

// ========================================
// EVENTOS AL CARGAR LA PÁGINA
// ========================================
document.addEventListener('DOMContentLoaded', () => {
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
    setInterval(cargarAsistencias, 30000);
});