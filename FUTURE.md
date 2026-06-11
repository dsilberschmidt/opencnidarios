# OpenCnidarios — Direcciones futuras

> Borrador. Recoge las direcciones hacia las que el proyecto podría crecer,
> ninguna comprometida. Todas son condicionales a que el experimento base
> —organismos evolucionando en el grid— muestre algo que valga la pena extender.
> Este documento se pule con el tiempo; hoy es una olla de ideas ordenadas.

---

## El arco del proyecto

**Primera versión (abordable).** Organismos LLM en el grid. Genoma de texto
(constitución + rumiar) y parámetros del modelo (temperamento). La energía es
latente: hay que descubrir la fotosíntesis. Dioses automáticos que cambian las
reglas de tanto en tanto. El objetivo es demostrar que algo emerge —o documentar
rigurosamente que no.

**Segunda versión (ambiciosa).** Evolución sobre los pesos: los organismos
aprenden durante su vida y heredan lo aprendido. Es el salto que hace al proyecto
genuinamente evolutivo, y el que justificaría apoyo externo —cómputo o
financiamiento de un laboratorio—. No se persigue de frente: se llega a él
mostrando tracción con la primera versión.

---

## Evolución sobre los pesos

Hoy lo heredable es texto y parámetros; el "cerebro" (los pesos del modelo) es fijo
y compartido. Eso acota cuánta novedad real es posible. La dirección profunda es
que los pesos también evolucionen:

- **Aprendizaje intra-vida.** El organismo ajusta un adaptador (tipo LoRA) mientras
  vive, reforzando lo que lo mantiene con energía. Aprende de verdad, en el mundo.
- **La supervivencia como recompensa natural.** No hay que diseñar una función de
  reward artificial: captar energía / no morir *es* la señal. El mundo provee el
  criterio.
- **Herencia lamarckiana de lo aprendido.** El hijo nace con el adaptador entrenado
  de la madre, con variación. Cada generación parte de lo que su linaje aprendió,
  no de cero.

Juntando las tres: organismos cuyo cerebro se ajusta al vivir, lo transmiten, y la
selección favorece a los linajes que aprendieron mejor. Texto, temperamento y pesos
evolucionando a la vez. (Costo y complejidad: ver DESAFIOS.)

---

## Una familia de mundos (alternativa abandonada por ahora)

Se consideró que hubiera varios tipos de mundo —ajedrez, sala de chat con humanos—
cada uno con su propia energía. La decisión actual es **un solo mundo** (el grid)
cuyas reglas varían por acción de los dioses, en lugar de muchos mundos distintos.
La familia de mundos queda registrada como posibilidad, no como plan: si el grid
con dioses no diera suficiente riqueza, se podría reconsiderar.

La idea estructural sigue valiendo: un mundo es un entorno donde la energía existe
pero captarla exige aprender algo no evidente. El grid cumple eso; otros entornos
también podrían.

---

## Los dioses

Uno o varios procesos que, sin intervenir sobre organismos individuales ni
perseguirlos, cada tanto inventan o quitan una regla de energía.

- **Cuándo actúan:** cuando el sistema florece (mucha diversidad — para ponerla a
  prueba) o cuando se estanca (nadie descubre nada nuevo — para sacudirlo). Muy de
  vez en cuando.
- **Inventar vs. quitar:** inventar abre una oportunidad nueva; quitar vuelve inútil
  una fotosíntesis aprendida y premia a quien acumuló diversidad de aprendizajes.
- **Dioses humanos:** a futuro, personas podrían ejercer este rol, quizás por
  votación de una comunidad.

Perillas del experimento: con qué frecuencia actúan, cuánto cambian cada vez, y qué
umbral de floración/estancamiento los dispara.

---

## Observadoras e historiadoras

Modelos que miran lo que ocurre, en dos funciones que conviene mantener separadas:

- **Detectora (filtro de atención).** Señala lo anómalo y lo describe. No decide
  sola qué es un fenómeno valioso —ese juicio sigue siendo humano—. Reduce miles de
  ticks a unos pocos candidatos para revisar. Debe validarse con controles (ver
  DESAFIOS).
- **Historiadora (cronista).** Narra la historia de los linajes: quién dominó, qué
  cambió cuando un dios quitó una regla, cómo derivó cada familia. Convierte datos
  en una saga legible. Es el puente entre el experimento y quien lo mira desde
  afuera.

A futuro, también historiadores humanos.

---

## Universos variables (idea conservada)

Antes de decantarse por "un mundo con dioses", se exploró la idea de mundos que
rotan (grid → otro → grid) con organismos que acumulan aprendizaje a través de los
cambios. La versión actual lo absorbe parcialmente: los dioses hacen variar el único
mundo. Pero la idea más fuerte —someter al organismo a presiones cualitativamente
distintas y premiar la adaptación general— queda registrada por si el proyecto
crece hacia ahí.

---

## Lo open y los linajes

- **Arena abierta:** que cualquiera introduzca organismos; un ecosistema plural y
  distribuido. Posterior a tener evidencia de que el fenómeno existe.
- **Linajes con historia:** la idea de que un organismo con procedencia trazable —que
  sobrevivió a tales reglas, mutó de tal forma— tenga valor en sí mismo, narrativo.
  Apareció en la concepción original. No es foco cercano.
- **Explorar organismos por conversación:** poder "hablar" con un organismo para ver
  qué sabe, en modo solo-lectura (responde, pero no recibe información que altere su
  estado, para no contaminar). Pieza delicada, posterior.
