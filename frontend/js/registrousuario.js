// ================================
//  REGISTRO DE USUARIO - EduGana
// ================================

document.addEventListener("DOMContentLoaded", function () {

    const form = document.querySelector("form");

    form.addEventListener("submit", async function (e) {
        e.preventDefault(); // Evita recargar la página

        // Obtener los valores del formulario
        const nombre = document.querySelector('input[placeholder="Ejemplo: Juan"]').value;
        const apellido = document.querySelector('input[placeholder="Ejemplo: Pérez"]').value;
        const correo = document.querySelector('input[type="email"]').value;
        const contrasena = document.querySelector('input[type="password"]').value;
        const rol = document.querySelector("select").value;

        // Validación
        if (!nombre || !apellido || !correo || !contrasena || !rol) {
            alert("Todos los campos son obligatorios");
            return;
        }

        // Crear objeto para enviar
        const data = {
            nombre_usuario: nombre,
            apellido_usuario: apellido,
            correo: correo,
            contrasena: contrasena,
            rol: rol
        };

        try {
            const response = await fetch("http://127.0.0.1:5000/addregistrarUsuario", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                alert("Usuario registrado correctamente ✔");
                form.reset(); // Limpia el formulario
            } else {
                alert("⚠ Error: " + result.mensaje);
            }

        } catch (error) {
            console.error("Error:", error);
            alert("No se pudo conectar con el servidor 😢");
        }

    });

});
