# Contribuir a TeleECOE

Gracias por querer mejorar TeleECOE. El proyecto busca ser libre, gratuito y modificable.

## Entorno de desarrollo

Linux/macOS:

```bash
./install.sh
./start.sh
```

Windows PowerShell:

```powershell
.\install.ps1
.\start.ps1
```

## Antes de enviar cambios

Ejecuta:

```bash
python scripts/check_release.py
```

En Windows:

```powershell
.\.venv\Scripts\python.exe scripts\check_release.py
```

## Reglas importantes

- No subir `.env`.
- No subir `go2rtc.yaml` real.
- No subir `evaluaciones.db` real.
- No subir grabaciones, logs ni backups.
- Si agregas campos de base de datos, agrega un script de migración o actualiza `scripts/init_db.py`.
- Documenta cambios funcionales en `docs/`.

## Seguridad

TeleECOE está pensado inicialmente para red local. Antes de exponerlo a internet se requiere autenticación, CSRF, configuración de producción y revisión de permisos.
