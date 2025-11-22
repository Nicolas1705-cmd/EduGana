// Variables globales
let recompensasData = [];
let recompensasFiltradas = [];
let paginaActual = 1;
let itemsPorPagina = 6;
let idCanjear = null;
let userPoints = 2500; // Puntos del usuario (se obtendría de la API de usuario)

// URL de la API
const API_URL = 'http://localhost:5000/listRecompensas';

// Cargar recompensas al iniciar
document.addEventListener('DOMContentLoaded', function() {
    cargarRecompensas();
});

// Función para cargar recompensas desde la API
async function cargarRecompensas() {
    const loader = document.getElementById('loader');
    const container = document.getElementById('recompensasContainer');
    
    loader.classList.add('is-active');
    container.style.display = 'none';

    try {
        const response = await fetch(API_URL);
        
        if (!response.ok) {
            throw new Error('Error al cargar recompensas');
        }
        
        const data = await response.json();
        
        // Mapear los datos de la API al formato del frontend
        recompensasData = (data.recompensas || []).map(r => ({
            id: r.id,
            nombre: r.nombre,
            descripcion: r.descripcion,
            puntos: r.puntos_requeridos,
            stock: r.stock,
            disponible: r.activo && r.stock > 0,
            icono: 'fa-gift', // Icono por defecto
            imagen: r.imagen_url
        }));
        
        recompensasFiltradas = [...recompensasData];
        mostrarRecompensas();
        
    } catch (error) {
        console.error('Error al cargar recompensas:', error);
        mostrarNotificacion('Error al cargar las recompensas. Verifica que el servidor esté corriendo en http://localhost:5000', 'danger');
        recompensasData = [];
        recompensasFiltradas = [];
        mostrarRecompensas();
    } finally {
        loader.classList.remove('is-active');
        container.style.display = 'block';
    }
}

// Función para mostrar recompensas en el grid
function mostrarRecompensas() {
    const grid = document.getElementById('recompensasGrid');
    const emptyState = document.getElementById('emptyState');
    const pagination = document.getElementById('pagination');
    
    grid.innerHTML = '';
    
    if (recompensasFiltradas.length === 0) {
        emptyState.style.display = 'block';
        pagination.style.display = 'none';
        return;
    }
    
    emptyState.style.display = 'none';
    
    // Calcular paginación
    const inicio = (paginaActual - 1) * itemsPorPagina;
    const fin = inicio + itemsPorPagina;
    const recompensasPagina = recompensasFiltradas.slice(inicio, fin);
    
    // Generar tarjetas
    recompensasPagina.forEach(recompensa => {
        const card = document.createElement('div');
        const tienePuntos = userPoints >= recompensa.puntos;
        const puedeRescatar = recompensa.disponible && tienePuntos;
        
        let cardClass = 'recompensa-card-main';
        if (!recompensa.disponible) {
            cardClass += ' no-disponible';
        } else if (!tienePuntos) {
            cardClass += ' sin-puntos';
        }
        
        card.className = cardClass;
        
        const icono = recompensa.icono || 'fa-gift';
        const imagenUrl = recompensa.imagen || '';
        
        // Usar imagen si está disponible, sino usar ícono
        let contenidoVisual = '';
        if (imagenUrl) {
            contenidoVisual = `<img src="${imagenUrl}" alt="${recompensa.nombre}" class="card-image" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                <div class="card-icon" style="display: none;">
                    <i class="fas ${icono}"></i>
                </div>`;
        } else {
            contenidoVisual = `<div class="card-icon">
                    <i class="fas ${icono}"></i>
                </div>`;
        }
        
        let botonHtml = '';
        if (!recompensa.disponible) {
            botonHtml = `
                <div class="card-footer">
                    <div class="tags has-addons mb-3" style="justify-content: center;">
                        <span class="tag is-dark">Stock</span>
                        <span class="tag is-danger">${recompensa.stock} disponibles</span>
                    </div>
                    <button class="button is-light is-fullwidth" disabled>
                        <span class="icon"><i class="fas fa-ban"></i></span>
                        <span>No Disponible</span>
                    </button>
                </div>
            `;
        } else if (!tienePuntos) {
            botonHtml = `
                <div class="card-footer">
                    <div class="tags has-addons mb-3" style="justify-content: center;">
                        <span class="tag is-dark">Stock</span>
                        <span class="tag is-success">${recompensa.stock} disponibles</span>
                    </div>
                    <button class="button is-warning is-fullwidth" disabled>
                        <span class="icon"><i class="fas fa-coins"></i></span>
                        <span>Puntos Insuficientes</span>
                    </button>
                </div>
            `;
        } else {
            botonHtml = `
                <div class="card-footer">
                    <div class="tags has-addons mb-3" style="justify-content: center;">
                        <span class="tag is-dark">Stock</span>
                        <span class="tag is-success">${recompensa.stock} disponibles</span>
                    </div>
                    <div class="button-group">
                        <button class="button is-info" onclick="verDetalle(${recompensa.id})">
                            <span class="icon"><i class="fas fa-info-circle"></i></span>
                            <span>Ver Detalle</span>
                        </button>
                        <button class="button is-primary" onclick="abrirModalCanjear(${recompensa.id}, '${recompensa.nombre.replace(/'/g, "\\'")}', ${recompensa.puntos})">
                            <span class="icon"><i class="fas fa-gift"></i></span>
                            <span>Canjear</span>
                        </button>
                    </div>
                </div>
            `;
        }
        
        card.innerHTML = `
            ${contenidoVisual}
            <h3 class="card-title">${recompensa.nombre}</h3>
            <p class="card-description">${recompensa.descripcion}</p>
            <div class="card-points">
                <i class="fas fa-coins"></i>
                <span>${recompensa.puntos} puntos</span>
            </div>
            ${botonHtml}
        `;
        
        grid.appendChild(card);
    });
    
    // Mostrar/ocultar paginación
    const totalPaginas = Math.ceil(recompensasFiltradas.length / itemsPorPagina);
    if (totalPaginas > 1) {
        pagination.style.display = 'flex';
        document.getElementById('currentPage').textContent = paginaActual;
        document.getElementById('totalPages').textContent = totalPaginas;
        
        // Habilitar/deshabilitar botones
        const btnAnterior = document.getElementById('btnAnterior');
        const btnSiguiente = document.getElementById('btnSiguiente');
        
        if (paginaActual === 1) {
            btnAnterior.disabled = true;
        } else {
            btnAnterior.disabled = false;
        }
        
        if (paginaActual === totalPaginas) {
            btnSiguiente.disabled = true;
        } else {
            btnSiguiente.disabled = false;
        }
    } else {
        pagination.style.display = 'none';
    }
}

// Función de búsqueda
function buscarRecompensas() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    
    if (searchTerm === '') {
        recompensasFiltradas = [...recompensasData];
    } else {
        recompensasFiltradas = recompensasData.filter(r => 
            r.nombre.toLowerCase().includes(searchTerm) ||
            r.descripcion.toLowerCase().includes(searchTerm)
        );
    }
    
    paginaActual = 1;
    mostrarRecompensas();
}

// Limpiar búsqueda
function limpiarBusqueda() {
    document.getElementById('searchInput').value = '';
    buscarRecompensas();
}

// Enter en búsqueda
document.getElementById('searchInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        buscarRecompensas();
    }
});

// Cambiar página
function cambiarPagina(direccion) {
    const totalPaginas = Math.ceil(recompensasFiltradas.length / itemsPorPagina);
    paginaActual += direccion;
    
    if (paginaActual < 1) paginaActual = 1;
    if (paginaActual > totalPaginas) paginaActual = totalPaginas;
    
    mostrarRecompensas();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Ver detalle
function verDetalle(id) {
    const recompensa = recompensasData.find(r => r.id === id);
    if (recompensa) {
        document.getElementById('detailNombre').textContent = recompensa.nombre;
        document.getElementById('detailDescripcion').textContent = recompensa.descripcion;
        document.getElementById('detailPuntos').textContent = recompensa.puntos + ' puntos';
        document.getElementById('detailEstado').innerHTML = recompensa.disponible 
            ? '<span class="tag is-success is-large">Disponible</span>'
            : '<span class="tag is-danger is-large">No Disponible</span>';
        
        document.getElementById('detailModal').classList.add('is-active');
    }
}

function cerrarModalDetalle() {
    document.getElementById('detailModal').classList.remove('is-active');
}

// Modal de canjear
function abrirModalCanjear(id, nombre, puntos) {
    idCanjear = id;
    document.getElementById('recompensaNombre').textContent = nombre;
    document.getElementById('recompensaPuntos').textContent = puntos;
    
    const tienePuntos = userPoints >= puntos;
    const btnConfirmar = document.getElementById('btnConfirmarCanje');
    const warningPuntos = document.getElementById('sinPuntosWarning');
    
    if (!tienePuntos) {
        const faltantes = puntos - userPoints;
        document.getElementById('puntosFaltantes').textContent = faltantes;
        warningPuntos.style.display = 'block';
        btnConfirmar.disabled = true;
    } else {
        warningPuntos.style.display = 'none';
        btnConfirmar.disabled = false;
    }
    
    document.getElementById('canjearModal').classList.add('is-active');
}

function cerrarModal() {
    document.getElementById('canjearModal').classList.remove('is-active');
    idCanjear = null;
}

async function confirmarCanje() {
    if (idCanjear === null) return;
    
    const recompensa = recompensasData.find(r => r.id === idCanjear);
    
    if (!recompensa || userPoints < recompensa.puntos) {
        mostrarNotificacion('No tienes suficientes puntos', 'danger');
        return;
    }
    
    try {
        // Aquí llamarías a tu API para canjear
        // const response = await fetch(`http://localhost:5000/canjear/${idCanjear}`, {
        //     method: 'POST'
        // });
        
        // Simular canje exitoso
        userPoints -= recompensa.puntos;
        document.getElementById('userPoints').textContent = userPoints;
        
        cerrarModal();
        mostrarNotificacion('¡Recompensa canjeada exitosamente! 🎉', 'success');
        
        // Actualizar las tarjetas para reflejar los nuevos puntos
        mostrarRecompensas();
        
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al canjear la recompensa', 'danger');
    }
}

// Función para mostrar notificaciones
function mostrarNotificacion(mensaje, tipo) {
    const notification = document.createElement('div');
    notification.className = `notification is-${tipo} is-light`;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    notification.innerHTML = `
        <button class="delete" onclick="this.parentElement.remove()"></button>
        ${mensaje}
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 4000);
}
