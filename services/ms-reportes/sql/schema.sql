-- db_reportes · base de lectura de ms-reportes. Ejecutar como root una sola vez.
-- Tablas desnormalizadas y SIN llaves foráneas (se alimentan por eventos).
-- Cambiar la contraseña fuera de desarrollo (debe coincidir con el Secret DB_PASSWORD).

CREATE DATABASE IF NOT EXISTS db_reportes CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE db_reportes;

CREATE TABLE IF NOT EXISTS productos_rm (
  producto_id    BIGINT        NOT NULL,
  codigo         VARCHAR(50)   NULL,
  nombre         VARCHAR(200)  NULL,
  precio         DECIMAL(12,2) NULL,
  activo         BOOLEAN       NOT NULL DEFAULT TRUE,
  actualizado_en DATETIME      NULL,
  PRIMARY KEY (producto_id),
  KEY ix_productos_codigo (codigo)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS existencias_rm (
  producto_id    BIGINT      NOT NULL,
  bodega_id      BIGINT      NOT NULL,
  cantidad       INT         NOT NULL DEFAULT 0,
  estado         VARCHAR(20) NULL,
  actualizado_en DATETIME    NULL,
  PRIMARY KEY (producto_id, bodega_id),
  KEY ix_existencias_estado (estado)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS movimientos_rm (
  id            BIGINT       NOT NULL AUTO_INCREMENT,
  evento_id     VARCHAR(100) NOT NULL,
  movimiento_id BIGINT       NULL,
  producto_id   BIGINT       NOT NULL,
  bodega_id     BIGINT       NULL,
  tipo          VARCHAR(30)  NOT NULL,
  cantidad      INT          NOT NULL,
  fecha         DATETIME     NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_mov_evento (evento_id),
  KEY ix_mov_producto (producto_id),
  KEY ix_mov_tipo_fecha (tipo, fecha)
) ENGINE=InnoDB;

CREATE USER IF NOT EXISTS 'reportes'@'%' IDENTIFIED BY 'reportes_pass';
GRANT SELECT, INSERT, UPDATE, DELETE ON db_reportes.* TO 'reportes'@'%';
FLUSH PRIVILEGES;
