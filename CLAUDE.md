# Marea Pública

Observatorio ciudadano de la contratación pública del Caribe colombiano (www.mareapublica.com), con datos de SECOP II.

- `etl/build_data.py` genera `site/data.json` cada madrugada (workflow "Actualizar datos y publicar").
- `site/` es la página publicada en GitHub Pages.
- `video/` produce los videos (voz ElevenLabs, música en `video/musica/`, workflow "Video de prueba").
- `bot/` publica en Instagram y Facebook lo aprobado en `bot/cola/` (workflow "Publicar en redes").

**Antes de cualquier trabajo de redes sociales (temas, guiones, videos, carruseles, captions, programación, publicación o análisis), lee y aplica `bot/MANUAL_REDES.md`.** Ahí están el rol, los objetivos de crecimiento de audiencia, la voz y las reglas que no se rompen.

**Antes de escribir instrucciones para Higgsfield, elegir tomas o armar videos, lee y aplica también `video/MANUAL_VISUAL.md`** (rol de productor y director de fotografía, estilo, reglas y especificaciones).
