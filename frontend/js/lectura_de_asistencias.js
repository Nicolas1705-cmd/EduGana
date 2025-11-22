/**
 * Archivo: app.js
 * Funcionalidad: Manejar el envío del formulario para registrar asistencia.
 */

document.addEventListener('DOMContentLoaded', () => {
    // -----------------------------------------------------------
    // 1. CONFIGURACIÓN
    // -----------------------------------------------------------
    // Asegúrate de que esta URL coincida con dónde corre tu API de Flask
    const API_BASE_URL = '/'; 
    const ENDPOINT_REGISTRO = '/registrarAsistencia'; // Endpoint POST de tu código Python

    const asistenciaForm = document.getElementById('asistencia-form');
    const registroIdInput = document.getElementById('registro_id');

    // -----------------------------------------------------------
    // 2. FUNCIÓN PARA REGISTRAR ASISTENCIA (POST)
    // -----------------------------------------------------------
    asistenciaForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // Detener el envío normal del formulario

        const id_ingresado = registroIdInput.value.trim();
        
        if (!id_ingresado) {
            alert('🚨 Por favor, ingresa el ID (DNI) para marcar asistencia.');
            return;
        }

        // Obtener la fecha y hora actuales en formato compatible con PostgreSQL/JSON
        const now = new Date();
        const fecha = now.toISOString().split('T')[0]; // "YYYY-MM-DD"
        // Aseguramos el formato "HH:MM:SS" (ej. "14:54:34")
        const hora = now.toTimeString().split(' ')[0].substring(0, 8); 

        // ⚠️ Estructura de datos requerida por tu función registrar_asistencia() en Flask
        const dataToSend = {
            "id_registro": id_ingresado, 
            "dni": id_ingresado,       
            "fecha": fecha,
            "hora": hora,
            "estado_asistencia": "Presente" // O el estado que decidas usar por defecto
        };

        try {
            // Realizar la solicitud POST a la API
            const response = await fetch(API_BASE_URL + ENDPOINT_REGISTRO, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(dataToSend) // Convertir los datos a JSON
            });

            // Leer la respuesta de la API (JSON)
            const result = await response.json();
            
            if (response.ok) {
                // Registro exitoso (código 201 en tu Flask)
                alert(`✅ ¡Registro exitoso! ID: ${id_ingresado}. Mensaje: ${result.mensaje}`);
                registroIdInput.value = ''; // Limpiar campo
                // Opcional: Recargar la lista de asistencias si tienes una función para eso (ej: cargarAsistencias())
            } else {
                // Error de validación o del servidor (código 400 o 500)
                alert(`❌ Error al registrar asistencia. Mensaje del servidor: ${result.mensaje}`);
                console.error("Detalles del error:", result);
            }
        } catch (error) {
            // Error de red (el servidor no responde)
            console.error('Error de red o CORS:', error);
            alert('🚫 No se pudo conectar con el servidor Flask. Verifica la URL y que el servidor esté corriendo.');
        }
    });

    // -----------------------------------------------------------
    // 3. FUNCIÓN PARA LIMPIAR CAMPO (Botón "Limpiar Campo")
    // -----------------------------------------------------------
    // Asignar el evento de limpiar si tienes un botón de reset
    const limpiarButton = asistenciaForm.querySelector('button[type="reset"]');
    if (limpiarButton) {
        limpiarButton.addEventListener('click', () => {
            registroIdInput.value = '';
            registroIdInput.focus(); // Dejar el foco listo para el siguiente ingreso
        });
    }

    // Opcional: Función para cargar asistencias (si la necesitas para recargar la tabla)
    // async function cargarAsistencias() { ... } 
    // cargarAsistencias(); 
});