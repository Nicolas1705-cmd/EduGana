// ==========================================================
// LÓGICA DE INTEGRACIÓN CON EL API DE PYTHON (JavaScript)
// Este script maneja el registro y la visualización de asistencias
// ==========================================================

// Asegúrate de que esta URL coincida con la dirección donde se ejecuta tu API de Flask.
const API_BASE_URL = 'http://localhost:5000/api/asistencia'; 

// Referencias a elementos del DOM
const formRegistro = document.getElementById('asistencia-form');
const inputID = document.getElementById('registro_id');
const tablaCuerpo = document.getElementById('asistencia-body');
const notificationBox = document.getElementById('notification-box');

// --- Utilidades ---

/**
 * Muestra una notificación temporal en la esquina superior derecha.
 * @param {string} message - Mensaje a mostrar.
 * @param {boolean} isSuccess - Si es true, usa color verde (éxito); si es false, color rojo (error).
 */
function showNotification(message, isSuccess = true) {
    const colorClass = isSuccess ? 'is-success' : 'is-danger';
    const iconClass = isSuccess ? 'fa-check-circle' : 'fa-times-circle';
    
    const notification = document.createElement('div');
    notification.className = `notification ${colorClass} is-light`;
    notification.style.display = 'flex';
    notification.style.alignItems = 'center';
    notification.innerHTML = `
        <button class="delete"></button>
        <span class="icon is-medium mr-2"><i class="fas ${iconClass}"></i></span>
        <span>${message}</span>
    `;
    
    // Agregar manejador para cerrar la notificación
    notification.querySelector('.delete').addEventListener('click', () => {
        notification.remove();
    });

    // Mostrar y ocultar automáticamente después de 5 segundos
    notificationBox.prepend(notification); // Mostrar la más reciente primero
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

/**
 * Obtiene la fecha actual en formato YYYY-MM-DD.
 * @returns {string} Fecha actual.
 */
function getCurrentDate() {
    return new Date().toISOString().split('T')[0];
}

/**
 * Obtiene la hora actual en formato HH:MM (24h).
 * @returns {string} Hora actual.
 */
function getCurrentTime() {
    // Usamos formato 24h para facilitar el guardado en la BD
    return new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', hour12: false });
}

/**
 * Función simulada para obtener el nombre completo a partir del DNI/ID.
 * NOTA: En un sistema real, esto sería otra llamada al API.
 * @param {string} id - El DNI o ID del usuario.
 * @returns {string} Nombre completo o un placeholder.
 */
function buscarNombrePorID(id) {
    const datosUsuarios = {
        'A00123': 'Ana Lucía Flores',
        'C00456': 'Carlos Miguel Pérez',
        'D00789': 'Diana Sofía Herrera',
        'E01011': 'Ernesto Gómez Paz',
    };
    return datosUsuarios[id] || `Usuario: ${id}`;
}

// --- API Handlers ---

/**
 * Llama al endpoint POST para registrar una nueva asistencia.
 * @param {string} idIngresado - DNI o ID del empleado/estudiante.
 * @returns {Promise<boolean>} True si el registro fue exitoso, false en caso contrario.
 */
async function registrarAsistenciaAPI(idIngresado) {
    const data = {
        // En tu código Flask, usas id_registro y dni. Asumimos que el ID/DNI ingresado es ambos.
        id_registro: idIngresado, 
        dni: idIngresado, 
        fecha: getCurrentDate(),
        hora: getCurrentTime(),
        // Usamos 'Presente' como estado por defecto para una nueva marcación de ENTRADA.
        estado_asistencia: 'Presente' 
    };

    try {
        const response = await fetch(API_BASE_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        const result = await response.json();
        
        if (response.ok) {
            showNotification(`✅ Éxito: ${result.mensaje}. ID: ${result.id_registro}`, true);
            return true;
        } else {
            showNotification(`❌ Error (${response.status}): ${result.mensaje || 'Error desconocido del servidor.'}`, false);
            return false;
        }

    } catch (error) {
        console.error('Error de red al registrar:', error);
        showNotification('❌ Error de conexión: No se pudo contactar al servidor API. ¿Está Flask corriendo?', false);
        return false;
    }
}

/**
 * Llama al endpoint GET para obtener todos los registros de asistencia.
 */
async function listarAsistenciasAPI() {
    tablaCuerpo.innerHTML = `<tr><td colspan="6" class="has-text-centered">Cargando registros del API...</td></tr>`;

    try {
        const response = await fetch(API_BASE_URL);

        if (!response.ok) {
            const errorData = await response.json();
            tablaCuerpo.innerHTML = `<tr><td colspan="6" class="has-text-centered has-text-danger">Error ${response.status}: ${errorData.mensaje || 'No se pudieron cargar los datos.'}</td></tr>`;
            return;
        }

        const asistencias = await response.json();
        renderizarTabla(asistencias);

    } catch (error) {
        console.error('Error de red al listar:', error);
        tablaCuerpo.innerHTML = `<tr><td colspan="6" class="has-text-centered has-text-danger">Error de conexión con el servidor.</td></tr>`;
    }
}

// --- Renderización de la Tabla ---

/**
 * Toma los datos de asistencia y los renderiza en la tabla HTML.
 * @param {Array<Object>} data - Lista de objetos de asistencia del API.
 */
function renderizarTabla(data) {
    tablaCuerpo.innerHTML = '';
    if (data.length === 0) {
        tablaCuerpo.innerHTML = `<tr><td colspan="6" class="has-text-centered">No hay registros de asistencia.</td></tr>`;
        return;
    }

    // Usamos reverse() para que el más reciente aparezca primero si tu API no ordena por defecto
    data.reverse().forEach((item, index) => {
        const nombre = buscarNombrePorID(item.dni); // Nombre simulado
        let tagClass = 'is-light'; 
        let displayHora = item.hora ? item.hora.substring(0, 5) : '-'; // Formato HH:MM
        
        // Asignar colores de Bulma en base al estado_asistencia
        switch(item.estado_asistencia) {
            case 'Presente':
                tagClass = 'is-success';
                break;
            case 'Tardanza':
                tagClass = 'is-warning';
                break;
            case 'Ausente':
                tagClass = 'is-danger';
                displayHora = '-'; 
                break;
            case 'Salida':
                tagClass = 'is-info';
                break;
            case 'Justificada':
                tagClass = 'is-link';
                break;
            default:
                tagClass = 'is-light';
        }

        const nuevaFila = document.createElement('tr');
        nuevaFila.innerHTML = `
            <td>${index + 1}</td>
            <td>${nombre}</td>
            <td>${item.id_registro}</td>
            <td>${item.dni}</td>
            <td><span class="tag ${tagClass}">${item.estado_asistencia}</span></td>
            <td>${displayHora}</td>
        `;
        tablaCuerpo.appendChild(nuevaFila);
    });
}


// --- Inicialización y Event Listeners ---

// Manejar el envío del formulario (Marcar Asistencia - POST)
formRegistro.addEventListener('submit', async function(event) {
    event.preventDefault();

    const idIngresado = inputID.value.trim().toUpperCase();
    
    if (idIngresado.length === 0) {
        showNotification('Por favor, ingresa un ID/DNI válido.', false);
        return;
    }
    
    // Deshabilitar botón mientras se espera la respuesta del API
    const submitButton = formRegistro.querySelector('button[type="submit"]');
    submitButton.classList.add('is-loading');

    const success = await registrarAsistenciaAPI(idIngresado);

    submitButton.classList.remove('is-loading');

    if (success) {
        // Limpiar el campo y recargar la lista si el registro fue exitoso
        inputID.value = '';
        inputID.focus();
        await listarAsistenciasAPI();
    }
});

// Cargar los datos del API al iniciar la página (GET)
document.addEventListener('DOMContentLoaded', () => {
    listarAsistenciasAPI();
});