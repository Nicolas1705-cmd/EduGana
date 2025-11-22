document.addEventListener("DOMContentLoaded", function () {

    const form = document.querySelector("form");

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const inputs = document.querySelectorAll("input, select");

        // Crear objeto con los datos
        const data = {
            "Nombre_Completo": inputs[0].value,
            "Fecha_de_Nacimiento": inputs[1].value,
            "Genero": inputs[2].value,
            "Documento_de_Identidad": inputs[3].value,
            "Nombre_del_Padre/Tutor": inputs[4].value,
            "Telefono_de_Contacto": inputs[5].value,
            "Correo_Electronico": inputs[6].value,
            "Colegio": inputs[7].value
        };

        // Convertir a parámetros de URL codificados
        const queryString = new URLSearchParams(data).toString();

        const url = `/addMatricula?${queryString}`;

        console.log("URL generada:", url);

        try {
            const response = await fetch(url, {
                method: "GET"
            });

            const result = await response.json();

            if (response.ok) {
                alert("✅ Matrícula registrada correctamente.\nDocumento: " + result.documento);
                form.reset();
            } else {
                alert("⚠️ Error: " + (result.error || "Error desconocido"));
            }

        } catch (error) {
            console.error("Error al enviar:", error);
            alert("❌ Error al conectar con la API.");
        }

    });

});
