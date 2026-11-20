-- db_auditoria · ejecutar con un usuario administrador (root) una sola vez.
-- En docker-compose se monta en /docker-entrypoint-initdb.d y MySQL lo ejecuta al crear el volumen.
-- ⚠️ Cambia la contraseña antes de usarlo fuera de desarrollo (y que coincida con el Secret DB_PASSWORD).

CREATE DATABASE IF NOT EXISTS db_auditoria CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE db_auditoria;

CREATE TABLE IF NOT EXISTS registros_auditoria (
  id                  BIGINT       NOT NULL AUTO_INCREMENT,
  evento_id           VARCHAR(100) NOT NULL,
  usuario_id          BIGINT       NULL,
  fecha_hora          DATETIME     NOT NULL,
  servicio_origen     VARCHAR(50)  NOT NULL,
  tipo_operacion      VARCHAR(50)  NOT NULL,
  producto_id         BIGINT       NULL,
  cantidad_anterior   INT          NULL,
  cantidad_modificada INT          NULL,
  motivo              VARCHAR(255) NULL,
  referencia          VARCHAR(100) NULL,
  registrado_en       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_evento (evento_id),
  KEY ix_usuario (usuario_id),
  KEY ix_fecha (fecha_hora),
  KEY ix_producto_fecha (producto_id, fecha_hora),
  KEY ix_tipo (tipo_operacion),
  KEY ix_referencia (referencia)
) ENGINE=InnoDB;

-- Tercera barrera de inmutabilidad: ni siquiera un usuario con más permisos puede editar o borrar
DROP TRIGGER IF EXISTS trg_auditoria_sin_update;
CREATE TRIGGER trg_auditoria_sin_update BEFORE UPDATE ON registros_auditoria
  FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'registros_auditoria es inmutable';

DROP TRIGGER IF EXISTS trg_auditoria_sin_delete;
CREATE TRIGGER trg_auditoria_sin_delete BEFORE DELETE ON registros_auditoria
  FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'registros_auditoria es inmutable';

-- Usuario de la aplicación: SOLO INSERT y SELECT (diapositiva 9)
CREATE USER IF NOT EXISTS 'auditoria'@'%' IDENTIFIED BY 'auditoria_pass';
GRANT SELECT, INSERT ON db_auditoria.registros_auditoria TO 'auditoria'@'%';
FLUSH PRIVILEGES;
