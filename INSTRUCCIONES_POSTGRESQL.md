# Guía rápida: Reinstalar PostgreSQL 17

## Problema actual
- El servicio PostgreSQL local se inicia y se detiene inmediatamente
- No conocemos la contraseña configurada
- El servidor remoto (35.237.18.79) no está accesible

## Solución: Reinstalación limpia

### Opción 1: Desinstalar y reinstalar (Recomendado)

1. **Desinstalar PostgreSQL 17:**
   - Panel de Control → Programas → Desinstalar un programa
   - Busca "PostgreSQL 17"
   - Clic derecho → Desinstalar
   - **IMPORTANTE:** Marca la opción para eliminar el directorio de datos

2. **Descargar PostgreSQL 17:**
   - https://www.postgresql.org/download/windows/
   - O usar el instalador que ya tienes

3. **Instalar con estos datos:**
   - Puerto: `5432` (default)
   - Contraseña para postgres: `postgres` (simple para desarrollo)
   - Locale: `C` (para evitar problemas de encoding)

4. **Después de instalar, actualizar configbd.py:**
   ```python
   DB_HOST = "localhost"
   DB_PASS = "postgres"
   ```

### Opción 2: Reparar instalación actual (Más rápido)

Ejecutar PowerShell **como Administrador**:

```powershell
# Detener el servicio
Stop-Service postgresql-x64-17 -Force

# Eliminar el directorio de datos corrupto
Remove-Item "C:\Program Files\PostgreSQL\17\data" -Recurse -Force

# Inicializar nuevo cluster con encoding UTF8
& "C:\Program Files\PostgreSQL\17\bin\initdb.exe" `
  -D "C:\Program Files\PostgreSQL\17\data" `
  -U postgres `
  -E UTF8 `
  --locale=C `
  --pwprompt

# Cuando pida contraseña, ingresa: postgres

# Iniciar el servicio
Start-Service postgresql-x64-17
```

### Opción 3: Usar SQLite temporalmente (Para desarrollo rápido)

Si solo necesitas probar la API rápidamente, puedo configurar SQLite que no requiere servidor:

```python
# Sin instalación adicional, solo Python
pip install sqlite3
```

## Después de solucionar

Actualiza `configbd.py`:
```python
DB_HOST = "localhost"
DB_PASS = "postgres"  # o la que configures
```

Y ejecuta los scripts SQL para crear las tablas `recompensas` e `historial_canjes`.

---

**¿Qué opción prefieres?**
- Opción 1: Más limpia pero toma más tiempo (15-20 min)
- Opción 2: Más rápida si funciona (5 min)
- Opción 3: Para pruebas rápidas sin PostgreSQL
