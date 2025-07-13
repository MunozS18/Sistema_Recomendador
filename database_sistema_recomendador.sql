-- Script para Crear la Base de Datos del Sistema Recomendador de Hoteles Cartagena
CREATE DATABASE IF NOT EXISTS sistema_recomendador_hoteles;
USE sistema_recomendador_hoteles;
drop database sistema_recomendador_hoteles;

-- Borrar tablas en el orden correcto para evitar problemas con las claves foráneas, bueno si ellas existen, sino puedes crearlas sin problemas, pero mejor ejecutalo
DROP TABLE IF EXISTS reviews_scraping;
DROP TABLE IF EXISTS interacciones_usuario;
DROP TABLE IF EXISTS valoraciones;
DROP TABLE IF EXISTS preferencias_usuario;
DROP TABLE IF EXISTS hoteles;
DROP TABLE IF EXISTS usuario;
DROP TABLE IF EXISTS codigo_verificacion;

-- 1. Crear la tabla 'usuario'
CREATE TABLE usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    ultimo_login DATETIME NULL,
    es_admin BOOLEAN DEFAULT FALSE,
    avatar_url VARCHAR(255) DEFAULT NULL,
    
    -- Índices para optimizar consultas
    INDEX idx_usuario_email (email),
    INDEX idx_usuario_admin (es_admin),
    INDEX idx_usuario_fecha_registro (fecha_registro)
);


-- 2. Crear la tabla 'hoteles' 
CREATE TABLE hoteles (
    id_hotel INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Información básica del hotel
    nombre VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    descripcion TEXT NULL,
    ubicacion VARCHAR(255) NULL,
    
    -- Sistema de precios avanzado
    precio_amount INT NULL,
    precio_currency VARCHAR(10) DEFAULT 'COP',
    precio_formatted VARCHAR(50) NULL,
    precio_source VARCHAR(50) NULL,
    
    -- Sistema de calificaciones profesional
    rating_score FLOAT NULL,
    rating_max_score INT DEFAULT 10,
    rating_formatted VARCHAR(20) NULL,
    
    -- Sistema de estrellas
    stars_count INT NULL,
    stars_formatted VARCHAR(20) NULL,
    reviews_count INT DEFAULT 0,
    
    -- Amenities y servicios (JSON para flexibilidad)
    amenities TEXT NULL,  -- JSON string con lista de amenities normalizadas
    amenities_raw TEXT NULL,  -- Amenities originales del scraping
    
    -- Sistema de imágenes múltiples
    imagen_url VARCHAR(512) NULL,  -- Imagen principal
    imagenes TEXT NULL,  -- JSON string con lista de URLs de imágenes
    
    -- Sistema de reviews y opiniones
    reviews TEXT NULL,  -- JSON string con lista de reviews
    reviews_summary VARCHAR(255) NULL,
    
    -- Información de contacto profesional
    telefono VARCHAR(50) NULL,
    email VARCHAR(120) NULL,
    website VARCHAR(1024) NULL,
    
    -- Ubicación geográfica (para mapas y proximidad)
    latitud FLOAT NULL,
    longitud FLOAT NULL,
    
    -- Enlaces a fuentes externas
    link_booking VARCHAR(1024),
    link_trivago VARCHAR(1024) NULL,
    fuente_principal VARCHAR(50) DEFAULT 'booking',
    
    -- Metadatos de scraping (para auditoría y calidad)
    fecha_scraping DATETIME DEFAULT CURRENT_TIMESTAMP,
    version_scraping VARCHAR(20) DEFAULT '2.0',
    metadata_scraping TEXT NULL,  -- JSON con metadatos adicionales
    
    -- Campos legacy para compatibilidad (migración suave)
    rating FLOAT NULL,  -- Campo legacy
    precio_promedio INT NULL,  -- Campo legacy
    imagen_url_legacy VARCHAR(1024),  -- Campo legacy
    fuente VARCHAR(50) NULL,  -- Campo legacy
    
    -- Sistema de puntuaciones detalladas (para recomendaciones avanzadas)
    puntuacion_personal FLOAT DEFAULT 0,
    puntuacion_instalaciones FLOAT DEFAULT 0,
    puntuacion_limpieza FLOAT DEFAULT 0,
    puntuacion_confort FLOAT DEFAULT 0,
    puntuacion_calidad_precio FLOAT DEFAULT 0,
    puntuacion_ubicacion FLOAT DEFAULT 0,
    
    -- Timestamps para auditoría
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 3. Crear la tabla 'preferencias_usuario' (Sistema de personalización)
CREATE TABLE preferencias_usuario (
    id_preferencias INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    tipo_viaje VARCHAR(50) NULL,
    presupuesto VARCHAR(20) NULL,
    ubicacion_preferida VARCHAR(100) NULL,
    amenities_importantes TEXT NULL,
    rating_minimo FLOAT DEFAULT 0,
    estrellas VARCHAR(50) NULL,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Relación con usuario
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    
    -- Índices para optimizar consultas de recomendación
    INDEX idx_preferencias_usuario (id_usuario),
    INDEX idx_preferencias_tipo_viaje (tipo_viaje),
    INDEX idx_preferencias_presupuesto (presupuesto),
    INDEX idx_preferencias_rating (rating_minimo)
);

-- 4. Crear la tabla 'valoraciones' (Sistema de reviews de usuarios)
CREATE TABLE valoraciones (
    id_valoracion INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_hotel_int INT,  
    puntuacion FLOAT NOT NULL,
    comentario TEXT NULL,
    fecha_valoracion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_hotel) REFERENCES hoteles(id_hotel) ON DELETE CASCADE,
    INDEX idx_valoraciones_usuario (id_usuario),
    INDEX idx_valoraciones_hotel (id_hotel),
    INDEX idx_valoraciones_fecha (fecha_valoracion),
    INDEX idx_valoraciones_puntuacion (puntuacion)
);
-- Te Sugiero que ejecutes está parte 
   UPDATE valoraciones v
   JOIN hoteles h ON v.id_hotel = h.nombre
   SET v.id_hotel_int = h.id_hotel;
      ALTER TABLE valoraciones ADD CONSTRAINT fk_valoraciones_hotel FOREIGN KEY (id_hotel) REFERENCES hoteles(id_hotel) ON DELETE CASCADE;
      ALTER TABLE valoraciones DROP COLUMN id_hotel;
   ALTER TABLE valoraciones CHANGE id_hotel_int id_hotel INT NOT NULL;

-- 5. Crear la tabla 'interacciones_usuario' (Sistema de tracking de comportamiento)
CREATE TABLE interacciones_usuario (
    id_interaccion INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_hotel INT NOT NULL,
    tipo_interaccion ENUM('vista', 'valoracion', 'favorito') NOT NULL,
    valor DECIMAL(3,2) NOT NULL,
    fecha_interaccion DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Relaciones
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_hotel) REFERENCES hoteles(id_hotel) ON DELETE CASCADE,
    
    -- Índices para análisis de comportamiento
    INDEX idx_interacciones_usuario (id_usuario),
    INDEX idx_interacciones_hotel (id_hotel),
    INDEX idx_interacciones_tipo (tipo_interaccion),
    INDEX idx_interacciones_fecha (fecha_interaccion),
    
    -- Índice compuesto para consultas frecuentes
    INDEX idx_interacciones_usuario_tipo (id_usuario, tipo_interaccion)
);

-- 6. Crear la tabla 'reviews_scraping' (Sistema de reviews externos)
CREATE TABLE reviews_scraping (
    id_review INT AUTO_INCREMENT PRIMARY KEY,
    id_hotel INT NOT NULL,
    puntuacion DECIMAL(3,2) NOT NULL,
    comentario TEXT NULL,
    fecha_review DATE NULL,
    fuente VARCHAR(50) NULL,
    fecha_scraping DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Relación con hotel
    FOREIGN KEY (id_hotel) REFERENCES hoteles(id_hotel) ON DELETE CASCADE,
    
    -- Índices para análisis de reviews
    INDEX idx_reviews_hotel (id_hotel),
    INDEX idx_reviews_fuente (fuente),
    INDEX idx_reviews_fecha (fecha_scraping),
    INDEX idx_reviews_puntuacion (puntuacion)
);

CREATE TABLE codigo_verificacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    canal VARCHAR(20) NOT NULL,
    codigo VARCHAR(10) NOT NULL,
    expiracion DATETIME NOT NULL,
    usado BOOLEAN DEFAULT FALSE,
    fecha_envio DATETIME NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
);

-- 7. Crear índices avanzados para optimizar rendimiento
-- Índices para hoteles (consultas frecuentes)
CREATE INDEX idx_hoteles_slug ON hoteles(slug);
CREATE INDEX idx_hoteles_precio_amount ON hoteles(precio_amount);
CREATE INDEX idx_hoteles_rating_score ON hoteles(rating_score);
CREATE INDEX idx_hoteles_stars_count ON hoteles(stars_count);
CREATE INDEX idx_hoteles_fuente_principal ON hoteles(fuente_principal);
CREATE INDEX idx_hoteles_fecha_scraping ON hoteles(fecha_scraping);
CREATE INDEX idx_hoteles_ubicacion ON hoteles(ubicacion);

-- Índices compuestos para consultas complejas
CREATE INDEX idx_hoteles_precio_rating ON hoteles(precio_amount, rating_score);
CREATE INDEX idx_hoteles_stars_rating ON hoteles(stars_count, rating_score);
CREATE INDEX idx_hoteles_ubicacion_precio ON hoteles(ubicacion, precio_amount);

-- 8. Insertar usuario administrador por defecto (password: admin123)
INSERT INTO usuario (nombre_usuario, email, password_hash, es_admin) VALUES 
('admin', 'admin@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3ZxQQxq6re', TRUE);

-- 9. Crear vistas para consultas frecuentes (optimización)
CREATE VIEW vista_hoteles_completos AS
SELECT 
    h.*,
    COUNT(DISTINCT i.id_interaccion) as total_interacciones,
    COUNT(DISTINCT v.id_valoracion) as total_valoraciones,
    AVG(v.puntuacion) as valoracion_promedio
FROM hoteles h
LEFT JOIN interacciones_usuario i ON h.id_hotel = i.id_hotel
LEFT JOIN valoraciones v ON h.nombre = v.id_hotel
GROUP BY h.id_hotel;

CREATE VIEW vista_usuarios_activos AS
SELECT 
    u.*,
    COUNT(DISTINCT i.id_interaccion) as total_interacciones,
    COUNT(DISTINCT v.id_valoracion) as total_valoraciones,
    MAX(u.ultimo_login) as ultima_actividad
FROM usuario u
LEFT JOIN interacciones_usuario i ON u.id_usuario = i.id_usuario
LEFT JOIN valoraciones v ON u.id_usuario = v.id_usuario
GROUP BY u.id_usuario;

-- 10. Crear procedimientos almacenados para operaciones comunes
DELIMITER //

-- Procedimiento para obtener hoteles recomendados
CREATE PROCEDURE obtener_hoteles_recomendados(
    IN p_id_usuario INT,
    IN p_limit INT
)
BEGIN
    SELECT DISTINCT h.*
    FROM hoteles h
    LEFT JOIN interacciones_usuario i ON h.id_hotel = i.id_hotel
    WHERE i.id_usuario = p_id_usuario 
       OR h.rating_score >= 8.0
    ORDER BY h.rating_score DESC, h.reviews_count DESC
    LIMIT p_limit;
END //

-- Procedimiento para actualizar estadísticas de hotel
CREATE PROCEDURE actualizar_estadisticas_hotel(
    IN p_id_hotel INT
)
BEGIN
    UPDATE hoteles h
    SET 
        reviews_count = (SELECT COUNT(*) FROM reviews_scraping WHERE id_hotel = p_id_hotel),
        rating_score = (SELECT AVG(puntuacion) FROM reviews_scraping WHERE id_hotel = p_id_hotel)
    WHERE h.id_hotel = p_id_hotel;
END //

DELIMITER ;

-- 11. Crear triggers para mantener integridad de datos
DELIMITER //

-- Trigger para actualizar timestamp de hotel
CREATE TRIGGER actualizar_timestamp_hotel
BEFORE UPDATE ON hoteles
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END //

-- Trigger para validar puntuación
CREATE TRIGGER validar_puntuacion
BEFORE INSERT ON valoraciones
FOR EACH ROW
BEGIN
    IF NEW.puntuacion < 0 OR NEW.puntuacion > 10 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Puntuación debe estar entre 0 y 10';
    END IF;
END //

DELIMITER ;

-- Usa esto para crear el usuario admin o puedes hacerlo desde VisualStudio Code    (python -m flask crear_admin) escribelo en la terminal  
select * from usuario;
SELECT * FROM usuario WHERE email = 'admin@gmail.com';
DELETE FROM usuario WHERE email = 'admin@gmail.com';
-- Insertar usuario administrador por defecto (password: admin123)
-- USUARIO: admin@gmail.com
-- CONTRASEÑA: admin123
INSERT INTO usuario (nombre_usuario, email, password_hash, es_admin) VALUES 
('admin', 'admin@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3ZxQQxq6re', TRUE);