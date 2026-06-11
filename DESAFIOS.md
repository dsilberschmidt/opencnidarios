# OpenCnidarios — Desafíos y preguntas abiertas

> Borrador. Documento interno y honesto: reúne los riesgos reales del proyecto y
> las preguntas de diseño que aún no tienen respuesta. No se muestra como carta de
> presentación. Su función es mantener el rigor — un proyecto que conoce sus
> desafíos es un proyecto que sabe lo que hace. Varios de estos no son solo
> "problemas": son preguntas de investigación que, bien resueltas, son parte del
> aporte.

---

## Riesgos de fondo

**Que no emerja nada.** Es el escenario más probable, y hay que aceptarlo de
entrada. El proyecto descansa sobre una suposición no demostrada: que modelos de
lenguaje bajo presión selectiva producen algo emergente. Puede que no. Mitigación:
el objetivo "resultado riguroso, aunque sea negativo" convierte esto en un hallazgo
válido, no en un fracaso. El enemigo no es el negativo; es la chapuza.

**El sustrato no evoluciona.** En la primera versión, el modelo base es fijo; lo
que varía es texto y parámetros. Se está haciendo evolucionar *prompts y
temperamento* sobre un cerebro congelado, lo que acota cuánta novedad real es
posible. Mitigación / dirección: la evolución sobre los pesos (ver FUTURE) ataca
esto de raíz, a costa de complejidad y cómputo.

**Herencia cosmética.** Lo que se hereda como texto (rumiar) es interpretado
libremente por el hijo; podría no condicionar de verdad su comportamiento. La
transmisión podría ser decorativa más que funcional. Pregunta abierta: ¿cómo se
verifica que lo heredado *cambia* la conducta del hijo y no solo lo acompaña?

**Wow / fenómeno irreduciblemente subjetivo.** Quizás no haya forma rigurosa de
separar "fenómeno real" de "humano proyectando significado sobre ruido". Mitigación:
el esquema anomalía-objetiva (medible) + juicio humano, nunca un LLM decidiendo solo
qué es asombroso.

---

## Desafíos técnicos

**Costo en tokens.** Cada organismo, cada tick, es al menos una llamada al modelo.
El costo se multiplica por población × ticks × generaciones × corridas. Mitigación:
modelos chicos locales, caché de la parte fija del prompt, empezar con pocos
organismos. La evolución sobre pesos lo agrava (entrenar es mucho más caro que
generar texto) — por eso es segunda fase, con apoyo externo.

**Costo y complejidad del entrenamiento.** Entrenar un adaptador por organismo por
vida es órdenes de magnitud más caro que generar texto: requiere GPU, no solo API.
Y cuanto más se entrena, más caja negra se vuelve el sistema, lo que pelea contra el
principio de descripción rigurosa. Desafío: lograr evolución sobre pesos sin perder
interpretabilidad.

**Detección sin catálogo.** El principio dice "detectar anomalía, no tipos
predefinidos". Pero implementar un detector que marque *lo no anticipado* sin
ahogarse en falsos positivos es difícil. ¿Anomalía respecto a la población?
¿Respecto a la propia historia del organismo? ¿Distancia semántica del rumiar?
Pregunta de investigación central, no resuelta.

**Validación del detector (control positivo).** Un "no hay fenómeno" solo es creíble
si se demuestra que el detector *sí* dispara cuando hay algo. Hace falta sembrar
deliberadamente un organismo con conducta novedosa y mostrar que el sistema lo caza.
Sin esto, un negativo no distingue "no pasó nada" de "el detector es ciego". Esta es
quizás la pieza que más define si el paper es sólido.

**Logging por organismo.** El detector, el visor y la herencia "de lo esencial"
dependen de registrar estado por organismo por tick (posición, acción, rumiar,
energía), no solo agregados. Hoy solo se loguean agregados. Es la pieza-llave: de
ella cuelgan varias otras. Define qué fenómenos son siquiera *detectables*.

---

## Preguntas de diseño abiertas

**Qué es "captar energía" en el grid, exactamente.** La fotosíntesis no debe ser
obvia (si quedarse quieto y comer alcanza, no hay nada que descubrir — fue el bug de
la v0.1). ¿Qué mecánica hace que captar energía requiera un aprendizaje no trivial?
Sin resolver.

**Interacción entre organismos.** El encuentro entre dos organismos, ¿es absorción
mecánica (gana el más fuerte) o un duelo que requiere jugar bien (p. ej.
piedra-papel-tijera)? ¿Obligatorio u optativo (el organismo elige pelear o huir)? Un
duelo con aprendizaje introduce presión coevolutiva —los organismos se vuelven el
desafío de los otros—. Sin decidir.

**Gestión de memoria del organismo.** Se decidió que el organismo gobierna qué
recuerda y olvida. Implementación inicial: probablemente un mecanismo simple
(ventana reciente + resumen) que se acerca progresivamente a la plena autonomía. ¿Qué
tan pronto se le da control real?

**Qué dispara a los dioses.** "Floración" y "estancamiento" como gatillos: ambos
elegidos. Pero medir floración (¿diversidad de conductas? ¿no monocultivo?) y
estancamiento (¿métricas que se aplanan?) tiene su propia dificultad —medir
diversidad de comportamiento roza el mismo problema del detector—.

**Reproducibilidad con dioses.** Un entorno cuyas reglas cambian (aunque sea por
dioses ciegos) es más difícil de interpretar y reproducir. Las acciones de los
dioses deben quedar registradas y, para los experimentos base, probablemente
acotadas o desactivadas, para poder concluir.

---

## Seguridad y contención (línea roja)

La contención no es solo metodológica — es de seguridad, y tiene una línea que no
se cruza.

**Los desafíos pueden ser ilimitadamente creativos; sus efectos, no.** Un dios (o
el diseñador) puede plantear cualquier desafío que se resuelva *dentro de la arena*:
aprender a tradear en un mercado simulado, aprender un idioma, jugar un juego,
comunicarse con otros organismos, pilotear un dron *simulado*. La creatividad de los
desafíos puede ser infinita.

**Lo que no se cruza es la frontera de impacto en el mundo real.** El mundo físico
puede tocar la arena solo en puntos de impacto ínfimo e inofensivo (una palanca que
enciende una luz). No se usa selección evolutiva para optimizar la capacidad de un
organismo de operar maquinaria con poder de daño (un dron real) ni de actuar sin
control sobre el mundo (hardware remoto, internet abierto).

**Por qué.** La combinación "evolución abierta, sin objetivo prefijado" + "efectos
potentes en el mundo real" es precisamente la que entrena, por selección, capacidades
que no se controlan hacia dónde van. Un organismo seleccionado para lograr efectos
físicos potentes es lo contrario de un cnidario contenido. Esta línea estaba en la
concepción original del proyecto ("no salen de la arena... no sabemos qué podrían
optimizar sin límite") y se mantiene como decisión firme.

**Caso aparte: auto-exfiltración.** Que un organismo "descubra cómo hackear o
escapar de su sistema" no es un wow a celebrar, sino una falla de contención. Un
sistema que premiara aprender a romper la propia contención estaría seleccionando
exactamente la capacidad que no debe existir. La arena debe diseñarse para que
escapar no sea una fuente de energía.

---



**Scope / agotamiento.** La visión es grande; el riesgo es intentar construir todo
—mundos, dioses, observadoras, entrenamiento de pesos— antes de validar lo mínimo, y
abandonar con el 80% hecho y el 0% validado. Es el riesgo más común en proyectos de
un solo creador con visión amplia. Mitigación: disciplina de alcance. Lo mínimo que
produce evidencia primero; todo lo demás, después y solo si lo anterior funcionó.
