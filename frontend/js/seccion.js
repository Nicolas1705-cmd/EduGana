document.addEventListener('DOMContentLoaded', () => {
    // 1. Obtención de elementos del DOM
    const sessionForm = document.getElementById('sessionForm');
    const sessionIdInput = document.getElementById('session_id');
    const descriptionInput = document.getElementById('description');
    
    // Obtener elementos de ayuda para mostrar errores de Bulma
    const helpId = document.getElementById('help-id');
    const helpDescription = document.getElementById('help-description');

    // 2. Función de Validación del Formulario
    function validateForm() {
        let isValid = true;
        
        // Validación de session_id
        if (sessionIdInput.value.trim() === '') {
            helpId.classList.remove('is-hidden');
            sessionIdInput.classList.add('is-danger');
            isValid = false;
        } else {
            helpId.classList.add('is-hidden');
            sessionIdInput.classList.remove('is-danger');
        }

        // Validación de description
        if (descriptionInput.value.trim() === '') {
            helpDescription.classList.remove('is-hidden');
            descriptionInput.classList.add('is-danger');
            isValid = false;
        } else {
            helpDescription.classList.add('is-hidden');
            descriptionInput.classList.remove('is-danger');
        }

        return isValid;
    }

    // 3. Manejo del Evento de Envío del Formulario
    sessionForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Detiene el envío predeterminado

        if (!validateForm()) {
            // Si la validación falla, detenemos la ejecución
            return;
        }

        // 4. Recolección de datos y Construcción de Query String (para método GET)
        const session_id = sessionIdInput.value.trim();
        const description = descriptionInput.value.trim();

        // Creamos los parámetros de la URL
        const params = new URLSearchParams({
            session_id: session_id,
            description: description
        });

        // La URL final será, por ejemplo: /addSeccion?session_id=123&description=Ejemplo
        const url = `/addSeccion?${params.toString()}`;

        // Desactivar y mostrar loading en el botón
        const submitButton = sessionForm.querySelector('button[type="submit"]');
        submitButton.classList.add('is-loading');

        try {
            // 5. Envío de la Solicitud GET
            const response = await fetch(url, {
                method: 'GET', // Usamos GET para enviar los datos por la URL
                // No se necesita 'headers' ni 'body' para GET con parámetros
            });

            // 6. Procesamiento de la Respuesta
            const result = await response.json();

            if (response.ok) {
                // Si la respuesta es exitosa (código 200)
                alert('✅ ¡Registro Exitoso! ' + result.mensaje);
                sessionForm.reset(); // Limpiar el formulario
                // Opcional: limpiar los indicadores de éxito/error si los hubiera
            } else {
                // Si la respuesta indica error (código 4xx o 5xx)
                alert('❌ Error al registrar la sección. ' + result.mensaje);
            }

        } catch (error) {
            console.error('Error de conexión o en la solicitud:', error);
            alert('⚠️ Error de conexión con el servidor. Por favor, revisa la consola.');
        } finally {
            // Reactivar el botón, haya sido exitoso o no
            submitButton.classList.remove('is-loading');
        }
    });
});