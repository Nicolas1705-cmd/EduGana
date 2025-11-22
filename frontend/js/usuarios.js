document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");

    form.addEventListener("submit", async function (e) {
        e.preventDefault(); // Evita recargar la página

        // Obtener valores del formulario
        const nombre = document.querySelectorAll("input")[0].value.trim();
        const apellido = document.querySelectorAll("input")[1].value.trim();
        const correo = document.querySelectorAll("input")[2].value.trim();
        const contrasena = document.querySelectorAll("input")[3].value.trim();
        const rol = document.querySelector("select").value;

        // Validar campos
        if (!nombre || !apellido || !correo || !contrasena || rol === "Seleccionar rol...") {
            alert("Todos los campos son obligatorios");
            return;
        }

        // Crear objeto
        const usuarioData = {
            nombre_usuario: nombre,
            apellido_usuario: apellido,
            correo: correo,
            contrasena: contrasena,
            rol_usuario: rol
        };

        try {
            const response = await fetch("http://127.0.0.1:5000/api/registrarUsuario", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(usuarioData)
            });

            const data = await response.json();

            if (response.status === 201) {
                alert("✔ Usuario registrado correctamente");
                form.reset();
            } else {
                alert("⚠ " + data.mensaje);
            }

        } catch (error) {
            console.error("ERROR:", error);
            alert("Error al conectar con el servidor.");
        }
    });
});
