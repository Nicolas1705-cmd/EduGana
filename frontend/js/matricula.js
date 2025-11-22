    // Variables de entorno proporcionadas por Canvas (requeridas para el uso de Firestore y API Keys)
        const apiKey = ""; // La clave API se proporcionará automáticamente en tiempo de ejecución por Canvas.
        const apiUrlBase = "https://generativelanguage.googleapis.com/v1beta/models/";
        const modelName = "gemini-2.5-flash-preview-09-2025";
        const apiUrl = `${apiUrlBase}${modelName}:generateContent?key=${apiKey}`;

        // Referencias a elementos del DOM
        const inputTextElement = document.getElementById('inputText');
        const targetLanguageElement = document.getElementById('targetLanguage');
        const translateButton = document.getElementById('translateButton');
        const translationOutput = document.getElementById('translationOutput');
        const statusMessage = document.getElementById('statusMessage');

        /**
         * Función genérica para manejar llamadas a la API de Gemini con retroceso exponencial.
         * @param {Object} payload - El cuerpo de la solicitud JSON.
         * @param {number} maxRetries - El número máximo de reintentos.
         * @returns {Promise<Object>} La respuesta JSON de la API.
         */
        async function fetchWithExponentialBackoff(payload, maxRetries = 5) {
            for (let attempt = 0; attempt < maxRetries; attempt++) {
                try {
                    const response = await fetch(apiUrl, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(payload)
                    });

                    if (response.ok) {
                        return await response.json();
                    } else if (response.status === 429 && attempt < maxRetries - 1) {
                        // Código 429: Demasiadas solicitudes. Esperar y reintentar.
                        const delay = Math.pow(2, attempt) * 1000 + Math.random() * 1000;
                        console.warn(`Intento ${attempt + 1} fallido. Reintentando en ${delay / 1000}s...`);
                        await new Promise(resolve => setTimeout(resolve, delay));
                    } else {
                        // Otros errores o último intento fallido
                        const errorData = await response.json();
                        throw new Error(`Error de la API (${response.status}): ${errorData.error?.message || response.statusText}`);
                    }
                } catch (error) {
                    if (attempt === maxRetries - 1) {
                        console.error('Error final después de reintentos:', error);
                        throw new Error(`Fallo en la conexión: ${error.message}`);
                    }
                    // Si es un error de red, solo se registra y se deja que el bucle reintente.
                    console.error(`Error en el intento ${attempt + 1}: ${error.message}`);
                }
            }
            throw new Error("Máximo de reintentos alcanzado sin éxito.");
        }

        /**
         * Realiza la traducción llamando a la API de Gemini.
         */
        async function translateText() {
            const textToTranslate = inputTextElement.value.trim();
            const language = targetLanguageElement.value;

            if (!textToTranslate) {
                statusMessage.textContent = "Por favor, introduce el texto a traducir.";
                statusMessage.classList.remove('text-green-600', 'text-red-600');
                statusMessage.classList.add('text-yellow-600');
                translationOutput.textContent = "(La traducción aparecerá aquí.)";
                return;
            }

            // Configurar la interfaz de usuario para el estado de carga
            translateButton.disabled = true;
            translateButton.textContent = "Traduciendo...";
            translateButton.classList.add('bg-gray-400', 'cursor-not-allowed');
            translateButton.classList.remove('bg-indigo-600', 'hover:bg-indigo-700');
            statusMessage.textContent = "Conectando con Gemini...";
            statusMessage.classList.remove('text-yellow-600', 'text-red-600');
            statusMessage.classList.add('text-blue-600');
            translationOutput.textContent = "";


            try {
                // El System Instruction guía al modelo sobre su rol
                const systemPrompt = `Actúa como un traductor profesional. Tu única tarea es traducir el texto proporcionado por el usuario al idioma objetivo. No añadas ninguna explicación, comentario o texto adicional. Sólo devuelve el texto traducido.`;

                // El Query del usuario incluye la instrucción de traducción y el texto.
                const userQuery = `Traduce el siguiente texto a ${language}:\n\n"${textToTranslate}"`;

                const payload = {
                    contents: [{
                        parts: [{
                            text: userQuery
                        }]
                    }],
                    systemInstruction: {
                        parts: [{
                            text: systemPrompt
                        }]
                    },
                    // Desactivar el grounding para la traducción
                    tools: []
                };

                const result = await fetchWithExponentialBackoff(payload);
                const text = result.candidates?.[0]?.content?.parts?.[0]?.text;

                if (text) {
                    translationOutput.textContent = text.trim();
                    statusMessage.textContent = "Traducción completada con éxito.";
                    statusMessage.classList.remove('text-blue-600', 'text-red-600');
                    statusMessage.classList.add('text-green-600');
                } else {
                    translationOutput.textContent = "No se pudo obtener la traducción. Inténtalo de nuevo.";
                    statusMessage.textContent = "Error: Respuesta vacía de la API.";
                    statusMessage.classList.remove('text-blue-600', 'text-green-600');
                    statusMessage.classList.add('text-red-600');
                }

            } catch (error) {
                console.error("Fallo general de traducción:", error);
                translationOutput.textContent = "Ocurrió un error al intentar traducir el texto. Por favor, verifica tu entrada e inténtalo de nuevo.";
                statusMessage.textContent = `Error: ${error.message}`;
                statusMessage.classList.remove('text-blue-600', 'text-green-600');
                statusMessage.classList.add('text-red-600');
            } finally {
                // Restablecer la interfaz de usuario
                translateButton.disabled = false;
                translateButton.textContent = "Traducir Texto";
                translateButton.classList.remove('bg-gray-400', 'cursor-not-allowed');
                translateButton.classList.add('bg-indigo-600', 'hover:bg-indigo-700');
            }
        }

        // Asignar el listener de eventos al botón cuando el DOM esté completamente cargado.
        window.onload = function() {
            translateButton.addEventListener('click', translateText);
            // Mensaje inicial
            statusMessage.textContent = "Listo para traducir.";
            statusMessage.classList.add('text-gray-500');
        };