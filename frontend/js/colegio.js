// registro.js

// URL del endpoint de Flask. Debe ser el mismo que configures en Flask.
const URL_BACKEND = '/addColegio';  

document.addEventListener('DOMContentLoaded', () => {
    // ... (El código de inicialización es el mismo) ...
    const form = document.querySelector('form');
    const userPointsElement = document.getElementById('userPoints');
    if (userPointsElement) {
        userPointsElement.textContent = '100 Pts';
    }
    if (form) {
        form.addEventListener('submit', manejarEnvioFormulario);
    }
});

/**
 * Intercepta el envío del formulario, extrae los datos y los envía al backend usando GET.
 * @param {Event} event - El evento de envío del formulario.
 */
async function manejarEnvioFormulario(event) {
    event.preventDefault(); // Evita el envío por defecto

    const submitButton = event.target.querySelector('button[type="submit"]');

    // Validación de campos requeridos (mínima)
    const tipoColegio = document.getElementById('tipo_colegio').value;
    if (tipoColegio === "") {
        alert("⚠️ Por favor, seleccione un 'Tipo de Gestión'.");
        return; 
    }
    
    if (submitButton) {
        submitButton.classList.add('is-loading');
    }

    try {
        // --- CONSTRUCCIÓN DE LA URL CON PARÁMETROS (GET) ---
        const params = new URLSearchParams({
            codigo_modular_r: document.getElementById('codigo').value,
            nombre_colegio: document.getElementById('nombre').value,
            tipo_gestion: tipoColegio, 
            direccion_comple: document.getElementById('direccion').value,
            departamento: document.getElementById('departamento').value,
            provincia: document.getElementById('provincia').value,
            distrito: document.getElementById('distrito').value,
            // Si está vacío, se envía un string vacío, el backend debe manejarlo
            telefono: document.getElementById('telefono').value.trim(), 
            email_institucion: document.getElementById('email').value,
            nombre_director: document.getElementById('director').value
        });

        // Construye la URL final: http://127.0.0.1:5000/addColegio?codigo_modular_r=...
        const urlFinal = `${URL_BASE}${URL_BACKEND}?${params.toString()}`;
        
        console.log("URL de la petición (GET):", urlFinal);

        const respuesta = await fetch(urlFinal, {
            method: 'GET', // Cambiado a GET
            // No se usa 'Content-Type': 'application/json' ni 'body' en GET
        });

        if (respuesta.ok) {
            const resultado = await respuesta.json();
            
            alert(`✅ Registro (GET) exitoso!\nID Generado: ${resultado.id_colegio}\n${resultado.mensaje}`);
            
            event.target.reset();
            const idColegioInput = document.getElementById('id_colegio');
            if (idColegioInput) {
                idColegioInput.value = resultado.id_colegio;
            }
            
        } else {
            const errorData = await respuesta.json();
            throw new Error(errorData.error || `Error HTTP: ${respuesta.status}`);
        }

    } catch (error) {
        console.error('❌ Error en la conexión/registro:', error);
        alert(`Error al registrar el colegio:\n${error.message}`);
        
    } finally {
        if (submitButton) {
            submitButton.classList.remove('is-loading');
        }
    }
}