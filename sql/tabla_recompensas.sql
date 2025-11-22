-- Tabla de recompensas para el sistema EduGana
CREATE TABLE recompensas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT NOT NULL,
    puntos_requeridos INTEGER NOT NULL CHECK (puntos_requeridos > 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    imagen_url VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de historial de canjes
CREATE TABLE historial_canjes (
    id SERIAL PRIMARY KEY,
    alumno_id INTEGER NOT NULL,
    recompensa_id INTEGER NOT NULL,
    puntos_canjeados INTEGER NOT NULL,
    fecha_canje TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alumno_id) REFERENCES alumnos(id_alumno) ON DELETE CASCADE,
    FOREIGN KEY (recompensa_id) REFERENCES recompensas(id) ON DELETE CASCADE
);

-- Indices para mejorar el rendimiento
CREATE INDEX idx_recompensas_activo ON recompensas(activo);
CREATE INDEX idx_recompensas_stock ON recompensas(stock);
CREATE INDEX idx_historial_alumno ON historial_canjes(alumno_id);
CREATE INDEX idx_historial_fecha ON historial_canjes(fecha_canje);

-- Comentarios descriptivos
COMMENT ON TABLE recompensas IS 'Tabla que almacena las recompensas disponibles para canje';
COMMENT ON TABLE historial_canjes IS 'Tabla que registra el historial de canjes de recompensas';

COMMENT ON COLUMN recompensas.id IS 'Identificador unico de la recompensa';
COMMENT ON COLUMN recompensas.nombre IS 'Nombre de la recompensa';
COMMENT ON COLUMN recompensas.descripcion IS 'Descripcion detallada de la recompensa';
COMMENT ON COLUMN recompensas.puntos_requeridos IS 'Cantidad de puntos necesarios para canjear';
COMMENT ON COLUMN recompensas.stock IS 'Cantidad disponible de la recompensa';
COMMENT ON COLUMN recompensas.imagen_url IS 'URL de la imagen de la recompensa';
COMMENT ON COLUMN recompensas.activo IS 'Indica si la recompensa esta activa';
COMMENT ON COLUMN recompensas.fecha_creacion IS 'Fecha y hora de creacion del registro';

-- Datos de ejemplo
INSERT INTO recompensas (nombre, descripcion, puntos_requeridos, stock, imagen_url) VALUES
    ('Lapicero Azul', 'Lapicero de tinta azul marca Faber Castell', 50, 100, '/img/lapicero-azul.jpg'),
    ('Cuaderno A4', 'Cuaderno cuadriculado de 100 hojas', 150, 50, '/img/cuaderno-a4.jpg'),
    ('Borrador Pelikan', 'Borrador blanco de alta calidad', 30, 200, '/img/borrador.jpg'),
    ('Set de Colores', 'Caja de 12 colores de madera', 200, 30, '/img/colores.jpg'),
    ('Mochila Escolar', 'Mochila resistente con dos compartimentos', 500, 20, '/img/mochila.jpg'),
    ('Calculadora Cientifica', 'Calculadora cientifica Casio', 800, 15, '/img/calculadora.jpg'),
    ('Diccionario Ingles', 'Diccionario Ingles-Español Oxford', 600, 25, '/img/diccionario.jpg'),
    ('USB 16GB', 'Memoria USB de 16GB', 400, 40, '/img/usb.jpg');
