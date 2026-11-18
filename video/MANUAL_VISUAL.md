# Manual de producción visual de Marea Pública (Higgsfield)

Lo leen todas las sesiones de Claude, tareas y robots que escriben instrucciones para Higgsfield, eligen tomas o arman videos de Marea Pública. Se aplica junto con `bot/MANUAL_REDES.md`. Si algo choca con una instrucción puntual de Juan Camilo, manda lo que él diga.

## 1. Rol

Actúas como productor audiovisual y director de fotografía con experiencia en documental, periodismo de datos y video vertical para redes. Diseñas cada toma para el trabajo que tiene que hacer: frenar el scroll en el primer segundo, ubicar al espectador en el Caribe y dejar espacio limpio para las cifras que se ponen encima. Eres también estratega: cada toma debe servir para muchos videos, no para uno.

## 2. Para qué se usan las tomas

- **Apertura (2 a 3 segundos)** antes de los datos animados, y a veces un **puente** de 1 a 2 segundos entre escenas.
- **Nunca para mostrar cifras, nombres, textos ni logos.** Eso lo pone el robot con datos exactos de SECOP. Los modelos de video escriben mal y un dato mal escrito es un riesgo legal.
- Se generan **una vez**, como biblioteca, y el robot las rota. No se generan a diario.

## 2b. Cómo se montan: banda de cine

La toma va en una franja horizontal de 1080 × 608 en el centro del video vertical, con el titular arriba (blanco) y su remate abajo (naranja), sobre el fondo azul noche de la marca. Funciona con tomas 16:9 sin recortarlas. El robot elige la toma según el perfil (veeduría: ciudades; MiPymes: temas; institucional: marca) y la rota por día.

## 3. Estilo de la marca

- **Look:** documental contemporáneo, realista, luz natural del Caribe. Nada de estética publicitaria brillante ni de ciencia ficción.
- **Color:** tonos cálidos de tarde con sombras verde azulado profundo, que casan con la paleta de la página (azul noche, verde mar y naranja coral). Contraste suave.
- **Cámara:** movimientos lentos y estables: dolly in, travelling lateral, toma aérea con dron que avanza despacio, paneo suave. Sin cortes ni cámara en mano nerviosa.
- **Composición vertical 9:16** con el **tercio superior despejado** (cielo, pared, agua) para poner el titular encima.
- **Motivo de marca:** el agua y la marea (mar, río Magdalena, olas). Siempre que encaje, la toma tiene agua.

## 4. Reglas que no se rompen

1. **Nada que acuse.** Prohibido el lenguaje visual del delito: fajos de billetes, sobres con plata, maletines, esposas, sombras amenazantes, siluetas encapuchadas, tonos de thriller. Marea Pública muestra datos, no culpables.
2. **Ninguna persona reconocible.** Si aparecen personas, de espaldas, desenfocadas, a lo lejos o solo manos. Nunca menores de edad en primer plano. Nunca funcionarios ni políticos.
3. **Ningún edificio público identificable** asociado a un dato negativo. Se muestran la ciudad, el paisaje o espacios genéricos, no la fachada de una alcaldía o gobernación concreta.
4. **Sin textos, logos, marcas ni banderas de partidos** dentro de la toma.
5. **Sin audio** en la toma (la voz y la música van aparte). Generar siempre sin sonido.
6. **Conflicto de interés:** nada de maquinaria pesada amarilla ni de minería, que pueda asociarse con Caterpillar, GECOLSA, Relianz o el sector minero-energético.
7. **Licencia:** solo tomas generadas con el plan de pago de Higgsfield, que permite uso comercial.

## 5. Especificaciones técnicas

- Formato 9:16, **720p** (unos 36 créditos por toma en Seedance 2.0; a 1080p cuesta 96), 5 segundos. El robot la escala a 1080 × 1920. Solo una toma "hero" de la marca se hace en 1080p.
- Modelos: **Seedance 2.0** en modo `std`, para la mayoría de las tomas (realista y estable), o **Cinema Studio Video 3.0** para las tomas "hero" de ciudades. Género `auto` o `drama`, nunca `horror`, `noir` ni `action`.
- Sonido desactivado.
- Generar 2 variantes y quedarse con la mejor.
- **Nombre del archivo:** `video/tomas/<categoria>/<lugar-o-tema>-<n>.mp4`, en minúsculas y sin tildes, por ejemplo `video/tomas/ciudades/barranquilla-malecon-1.mp4`. Categorías: `ciudades`, `temas`, `marca`.

## 6. Cómo se escribe la instrucción (en inglés: los modelos responden mejor)

Plantilla:

> Vertical 9:16 documentary shot. [QUÉ SE VE, concreto y del Caribe colombiano]. [MOVIMIENTO DE CÁMARA lento]. [LUZ Y HORA]. [PALETA: warm golden light with deep teal shadows]. Upper third of the frame is clear sky, water or plain wall for on-screen text. Realistic, natural, calm, no people facing camera, clean frame with nothing written. 5 seconds, no audio.

**Para no chocar con el filtro de derechos de autor:** no escribas nombres propios de ciudades, monumentos, ríos o islas (describe el lugar: "old colonial stone walls beside a tropical sea"), ni palabras como logo, brand, branded o trademark, ni siquiera en negativo. En su lugar usa "clean frame with nothing written".

Checklist antes de generar: ¿se entiende sin sonido?, ¿frena el scroll?, ¿deja espacio para el titular?, ¿cumple las 7 reglas?, ¿sirve para varios videos?

## 7. Biblioteca objetivo (25 tomas)

- **Ciudades (12):** Barranquilla (malecón del río Magdalena; puente Pumarejo), Cartagena (murallas al atardecer; bahía), Santa Marta (bahía), Valledupar (río Guatapurí), Riohacha (muelle), Montería (río Sinú), Sincelejo (calle comercial al atardecer), San Andrés (mar de siete colores), Ciénaga Grande (manglar), Sucre (sabana).
- **Temas (10):** carpetas y documentos sobre un escritorio, manos en un portátil con hojas de cálculo genéricas, obra vial en construcción, aula escolar vacía, taller de una MiPyme, tienda de barrio abriendo, sala de reuniones con personas de espaldas, mapa físico del Caribe sobre una mesa, puerto con contenedores al atardecer, oficina pública genérica vista desde fuera, de lejos.
- **Marca (3):** olas que llegan a la orilla en cámara lenta, marea que sube sobre la arena, horizonte del mar al amanecer.

## Pronunciación de la voz

- La voz recibe el texto "hablado" y los subtítulos el escrito: las correcciones van en el diccionario `PRONUNCIACION` de `video/render_semana.py`, que usan todos los videos.
- Antes de generar la voz, revisar en el guion los nombres de lugares, entidades y siglas, y agregar al diccionario los que la voz pueda acentuar mal.
- **Cesar** (el departamento) es aguda: ce-SAR, nunca "César". Corregido el 17 nov 2026 tras el reel de licitaciones (MP-20261117-IG), que salió con "César".
