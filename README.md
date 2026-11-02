# Marea Pública — fase 1

Observatorio ciudadano de la contratación pública en el Caribe colombiano (Atlántico, Bolívar, Cesar, Córdoba, La Guajira, Magdalena, Sucre y San Andrés, Providencia y Santa Catalina), con datos abiertos de SECOP II.

## Qué hay en esta carpeta

| Archivo | Para qué sirve |
|---|---|
| `site/index.html` | La página completa: veeduría, licitaciones abiertas y metodología. |
| `site/data.json` | Los datos que lee la página. Se regenera solo cada noche. |
| `etl/build_data.py` | El motor: consulta SECOP II y produce `data.json`. No necesita librerías externas. |
| `.github/workflows/actualizar-datos.yml` | La tarea nocturna que corre el motor y publica el sitio. |

## Cómo funciona

1. Todos los días a las 3:17 a. m. (hora de Colombia), GitHub Actions ejecuta `etl/build_data.py`.
2. El motor consulta la API abierta de datos.gov.co: contratos firmados desde enero de 2024 y procesos con cierre en los próximos 30 días.
3. Si los totales cuadran, reemplaza `site/data.json` y publica la carpeta `site` en GitHub Pages.
4. Si la fuente falla o trae datos incompletos, no reemplaza nada: el sitio sigue con los datos del día anterior.

Costo de esta fase: cero pesos en hosting. Solo pagas el dominio.

## Puesta en marcha (una sola vez, unos 20 minutos)

1. **Crea una cuenta en GitHub** (github.com) si no tienes, y un repositorio nuevo llamado `marea-publica`. Puede ser privado.
2. **Sube esta carpeta completa** al repositorio (botón "Add file › Upload files", arrastrando las carpetas `site`, `etl` y `.github` y este README).
3. **Activa GitHub Pages:** en el repositorio, *Settings › Pages › Build and deployment › Source: GitHub Actions*.
4. **Pide un token gratuito de datos.gov.co** (opcional pero recomendado, evita límites de consultas): crea una cuenta en datos.gov.co, entra a *Developer Settings* y genera un *App Token*. Luego en GitHub: *Settings › Secrets and variables › Actions › New repository secret*, nombre `SOCRATA_APP_TOKEN`.
5. **Corre la primera actualización:** pestaña *Actions › Actualizar datos y publicar › Run workflow*. En unos 5 a 10 minutos el sitio queda en `https://TU-USUARIO.github.io/marea-publica/`.

## Conectar el dominio mareapublica.co

1. Registra `mareapublica.co` (y si quieres `.com` y `.com.co`) en un registrador como GoDaddy, Namecheap o Cloudflare.
2. En GitHub: *Settings › Pages › Custom domain*, escribe `mareapublica.co` y guarda. Marca *Enforce HTTPS* cuando aparezca disponible.
3. En el registrador, en la zona DNS del dominio, crea estos registros:
   - Cuatro registros **A** para `@` con las IP de GitHub Pages: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`.
   - Un registro **CNAME** para `www` que apunte a `TU-USUARIO.github.io`.
4. La propagación toma entre unos minutos y 24 horas.

## Correr el motor en tu computador (opcional)

Con Python 3.10 o superior:

```bash
python etl/build_data.py
```

Para ver el sitio localmente, desde la carpeta `site`:

```bash
python -m http.server 8000
```

y abre `http://localhost:8000`.

## Antes de lanzar al público

- **Responsable identificado:** la página de metodología debe decir quién está detrás del proyecto (persona o entidad) y un correo de contacto para correcciones y réplicas. Hoy dice "corrección y réplica" pero no tiene canal.
- **Política de tratamiento de datos y términos de uso:** aunque no se publican personas naturales, el sitio debe tener ambos documentos (Ley 1581 de 2012 y Decreto 1377 de 2013).
- **Aviso en Licitaciones:** la información es un resumen; el pliego y las adendas en SECOP II prevalecen.
- **Marca:** búsqueda de antecedentes y solicitud de registro de "Marea Pública" ante la SIC (clases 35, 41 y 42).

## Lo que viene (fases 2 y 3)

- Lectura de pliegos con IA: resumen de requisitos habilitantes para oferentes y bandera de pliego "sastre".
- Alertas por correo o WhatsApp por municipio y por sector.
- Radar de Ley de Garantías para las elecciones territoriales de 2027.
- Seguimiento de los contratos derivados que firman las intermediarias (EDUBAR, Puerta de Oro, EDURBE y otras).
- Plan de suscripción para empresas en el frente de Licitaciones.
