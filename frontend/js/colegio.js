// registro.js

// URL del endpoint de Flask. Debe ser el mismo que configures en Flask.
const URL_BACKEND = 'http://127.0.0.1:5000/colegios'; 

document.addEventListener('DOMContentLoaded', () => {
    // Obtenemos el formulario
    const form = document.querySelector('form');
    
    // Asignar 100 puntos por defecto (solo para ejemplo visual)
    const userPointsElement = document.getElementById('userPoints');
    if (userPointsElement) {
        userPointsElement.textContent = '100 Pts';
    }

    // Escuchamos el evento de envío del formulario
    if (form) {
        form.addEventListener('submit', manejarEnvioFormulario);
    }
});

/**
 * Intercepta el envío del formulario, extrae los datos y los envía al backend.
 * @param {Event} event - El evento de envío del formulario.
 */
async function manejarEnvioFormulario(event) {
    event.preventDefault(); // Evita que el formulario se envíe de forma tradicional (recarga de página)
    
    const submitButton = event.target.querySelector('button[type="submit"]');

    // Validación de campos requeridos (mínima)
    const tipoColegio = document.getElementById('tipo_colegio').value;
    if (tipoColegio === "") {
        alert("⚠️ Por favor, seleccione un 'Tipo de Gestión'.");
        return; 
    }
    
    // Activar estado de carga
    if (submitButton) {
        submitButton.classList.add('is-loading');
    }

    try {
        // Recolectar datos del formulario
        const datosDelFormulario = {
            // NOTA: id_colegio NO se envía, debe ser generado por el backend.
            codigo_modular_r: document.getElementById('codigo').value,
            nombre_colegio: document.getElementById('nombre').value,
            tipo_gestion: tipoColegio, 
            direccion_comple: document.getElementById('direccion').value,
            departamento: document.getElementById('departamento').value,
            provincia: document.getElementById('provincia').value,
            distrito: document.getElementById('distrito').value,
            // Si está vacío, se envía null para que PostgreSQL lo maneje como NULL
            telefono: document.getElementById('telefono').value.trim() || null, 
            email_institucion: document.getElementById('email').value,
            nombre_director: document.getElementById('director').value
        };
        
        console.log("Datos a enviar:", datosDelFormulario);

        const respuesta = await fetch(URL_BACKEND, {
            method: 'POST', // Debe ser POST para enviar datos
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(datosDelFormulario),
        });

        if (respuesta.ok) {
            const resultado = await respuesta.json();
            
            alert(`✅ Registro exitoso!\nID Generado: ${resultado.id_colegio}\n${resultado.mensaje}`);
            
            // Limpiar el formulario y actualizar el campo de ID
            event.target.reset();
            const idColegioInput = document.getElementById('id_colegio');
            if (idColegioInput) {
                idColegioInput.value = resultado.id_colegio; // Muestra el ID generado
            }
            
        } else {
            const errorData = await respuesta.json();
            throw new Error(errorData.error || `Error HTTP: ${respuesta.status}`);
        }

    } catch (error) {
        console.error('❌ Error en la conexión/registro:', error);
        alert(`Error al registrar el colegio:\n${error.message}`);
        
    } finally {
        // Quitar el estado de carga del botón al finalizar
        if (submitButton) {
            submitButton.classList.remove('is-loading');
        }
    }
}