---
clave: estructuras-suministro
slug: precio-fijado-entregas-futuras
volanta: Abastecimiento
titulo: Precio fijado, entregas futuras: ¿quién asume el riesgo en un programa de granel?
bajada: Acordar el precio del vino, comprometer el volumen anual y ordenar las retiradas son decisiones distintas. Cómo comparar estructuras de suministro cuando cambian las ventas, los plazos y las necesidades de capital.
orden: 3
fecha: 2026-11-06
---

Escena ilustrativa. Tres propuestas por el mismo vino, a 0,75 euros por litro, para 288.000 litros anuales. La primera exige recibir y pagar todo al inicio. La segunda permite cuatro recepciones a lo largo del año, con el volumen anual comprometido. La tercera permite comprar cada partida sin obligación sobre las siguientes.

En las dos primeras propuestas se fija el precio del volumen anual. En la tercera, 0,75 €/l es el precio de la primera partida; las siguientes quedan abiertas a las condiciones del mercado. Para aislar el efecto del calendario, el ejemplo supone inicialmente que todas se compran al mismo precio.

El precio por litro puede coincidir en las tres. La exposición de los meses siguientes, no.

> Si el precio por litro es el mismo, ¿qué estamos comparando cuando una oferta exige recibir todo y otra permite ordenar las retiradas durante el año?

En Corbeau adaptamos la programación de los embarques a las necesidades del cliente dentro de los volúmenes anuales acordados. La conversación cambia cuando ese compromiso anual no se cumple: ahí surge la renegociación.

Mover una retirada dentro del programa no es lo mismo que reducir el volumen anual.

## Tres estructuras, tres compromisos distintos

Las siguientes son estructuras hipotéticas para el mismo vino y la misma demanda. No describen modalidades ofrecidas por Corbeau ni condiciones estándar del mercado.

| Estructura | Qué se compromete | Cómo se recibe | Qué queda abierto |
| --- | --- | --- | --- |
| A · Compra anual, recepción inicial | 288.000 l y precio del vino | Todo al inicio | Ventas reales, costo de mantener existencias y costo de oportunidad si baja el mercado |
| B · Compromiso anual, retiradas escalonadas | 288.000 l y precio del vino | Cuatro recepciones de 72.000 l | Recursos reservados en origen, condiciones de pago y resultado si no se completa el volumen |
| C · Compras independientes | Solo la partida contratada | Cuatro compras previstas de 72.000 l | Precio y disponibilidad de las siguientes partidas, y nueva validación cuando corresponda |

Los contratos de largo plazo y las operaciones spot conviven como modalidades reales del negocio de granel. Ninguna domina en todos los escenarios, y la solución puede ser mixta: un volumen base comprometido y necesidades adicionales por confirmar.

FUENTE Ciatti, Want to Buy Bulk Wine

Conviene separar cuatro cosas que la conversación comercial mezcla con frecuencia: la previsión, el pedido firme, el volumen anual comprometido y la opción de compra. Una previsión no constituye por sí misma una reserva garantizada, y una tolerancia puede negociarse pero no debe asumirse incluida.

Hay además una definición que cambia bastante el resto: si se reserva un lote identificado o la capacidad de abastecer un perfil. Esa diferencia determina qué se inmoviliza y cómo se valida.

## Dónde queda el inventario y quién lo financia

La diferencia aparece al comparar inventario y costos de mantenimiento.

Todos los valores que siguen son supuestos ilustrativos. No son precios de Malbec, tasas bancarias ni tarifas de Corbeau. El objetivo es aislar el efecto del calendario, no calcular un costo puesto en destino.

Supuestos: demanda uniforme de 288.000 litros en doce meses, equivalente a 24.000 litros mensuales, con salidas continuas y uniformes; precio de 0,75 €/l; pago al recibir, sin anticipos ni crédito; financiación del inventario al 10% anual; almacenamiento a 0,006 €/l por mes. En B y C, recepciones al inicio de los meses 0, 3, 6 y 9. Se compara el mismo punto de recepción del comprador y se excluyen tránsito, stock de seguridad, impuestos, fletes, fraccionamiento, materiales, seguros y mermas.

| Métrica del comprador | A · Todo al inicio | B · Anual escalonado | C · Spot escalonado |
| --- | --- | --- | --- |
| Primer pago de vino | 216.000 € | 54.000 € | 54.000 € |
| Inventario medio | 144.000 l | 36.000 l | 36.000 l |
| Valor medio del inventario | 108.000 € | 27.000 € | 27.000 € |
| Financiación anual | 10.800 € | 2.700 € | 2.700 € |
| Almacenamiento anual | 10.368 € | 2.592 € | 2.592 € |
| Tenencia anual | 21.168 € | 5.292 € | 5.292 € |
| Precio de compras futuras | Fijado | Fijado | Sin fijar |

Los valores monetarios de C solo coinciden si cada compra posterior también se ejecuta a 0,75 €/l: es un escenario de precio constante, no una previsión. Si se incluye un cargo de reserva en B, o cambian los pagos, el flete o el seguro, hay que recalcular. B reduce el inventario medio del comprador un 75% y sus costos de tenencia en 15.876 euros al año, aproximadamente 5,51 céntimos por litro sobre el volumen anual. No es un ahorro neto del programa completo: faltan los costos y compromisos de la estructura en origen.

Conviene acotar qué mide ese costo. La financiación se calcula sobre el valor medio de las existencias, y no representa el capital de trabajo total ni un presupuesto de caja: no se modelan los cobros a clientes ni otros saldos operativos.

El paso siguiente es mirar el inventario de toda la cadena.

Si en B todo el vino ya está preparado y reservado al comienzo, las existencias en origen después de cada recepción serían 216.000, 144.000, 72.000 y cero litros durante cada trimestre: un promedio de 108.000 litros.

| Inventario medio del ejemplo | En origen | En destino | Total |
| --- | --- | --- | --- |
| Recepción anual completa | 0l | 144.000 l | 144.000 l |
| Entregas escalonadas | 108.000 l | 36.000 l | 144.000 l |

Supone que todo el vino está terminado y reservado desde el inicio.

> El inventario puede desplazarse entre las partes sin desaparecer. Lo que cambia es quién lo financia, dónde se conserva y qué condiciones comerciales hacen viable esa distribución.

Eso no significa que el costo total sea idéntico. Las tasas, las instalaciones, los costos de conservación y las necesidades de financiación de cada parte pueden ser muy distintos. Y tampoco significa que todo programa escalonado inmovilice el vino terminado desde el primer día: si se produce o se ensambla progresivamente, la comparación cambia.

## Cuando las ventas no siguen el plan

La comparación se vuelve interesante cuando el año deja de parecerse a la previsión. El caso más instructivo es el de ventas por debajo de lo esperado.

Con ventas un 25% menores —216.000 litros en lugar de 288.000— la diferencia es de 72.000 litros, con un valor de referencia de 54.000 euros al precio base. En A, si todo fue recibido, quedan 72.000 litros sin consumir al cierre. No son una pérdida de 54.000 euros: el vino sigue siendo un activo, sujeto a su valor recuperable y a los costos futuros de mantenerlo. Conviene no confundir esa cifra con un gasto reconocido ni con efectivo recuperable.

En B, la demanda menor no elimina el compromiso anual, y el saldo puede estar en origen o en destino según las retiradas efectivas. Es exactamente acá donde aparece la renegociación, y no en el ajuste ordinario de fechas dentro del volumen anual.

En C, si la reducción se conoce antes de emitir la cuarta compra y no existe obligación sobre ella, puede no contratarse. Esa flexibilidad no está disponible después de firmar un pedido ni con todos los proveedores, y su contrapartida es no haber asegurado precio ni disponibilidad.

El escenario inverso también importa. Con ventas un 25% mayores —360.000 litros— tanto A como B cubrían 288.000: faltan 72.000 litros, y un compromiso anual fijo no garantiza volumen extra. C también tiene que encontrar producto adicional. Lo útil es identificar con antelación el tramo de demanda base y el de crecimiento, y pactar cómo se consultarán cantidades adicionales.

## Lo que un precio fijo no fija

Un precio acordado deja varias cosas sin resolver, y conviene nombrarlas.

→ El calendario real de llegada. Sea-Intelligence reportó en octubre de 2026 una fiabilidad global de itinerarios del 50,6% y una demora media de 6,65 días entre las llegadas tardías, con datos hasta septiembre.

→ El precio de las compras futuras. En C, las tres últimas partidas suman 216.000 litros. Si pasan de 0,75 a 0,825 €/l, la compra de vino aumenta 16.200 euros; si bajan a 0,675, disminuye lo mismo.

→ La moneda de los pagos pendientes. En B, tras la primera recepción quedan 162.000 euros de compras previstas. Si el comprador presupuesta en otra moneda y no fijó el tipo de cambio, su costo puede variar aunque el precio en euros sea fijo.

FUENTE Sea-Intelligence, Global Liner Performance, edición 182, 28 de octubre de 2026

Sobre el dato marítimo conviene ser preciso. Son indicadores globales de arribos de buques, no de entregas de vino al almacén, y los 6,65 días corresponden a las llegadas tardías, no al conjunto de los viajes. No sirven para derivar un stock de seguridad: para eso hacen falta la distribución de demoras, la variabilidad de la demanda y el nivel de servicio buscado. Un ejemplo acota la magnitud. Si una recepción llega treinta días más tarde de lo previsto, con el consumo supuesto hay que cubrir 24.000 litros durante ese intervalo, y solo habría ruptura si las existencias y las otras recepciones no alcanzan. Mantener esos 24.000 litros adicionales durante todo el año costaría 3.528 euros de financiación y almacenamiento bajo las tasas del caso. Es una sensibilidad de costo, no una recomendación de stock.

Hay además una confusión frecuente que conviene deshacer. La Cámara de Comercio Internacional distingue obligaciones operativas, reparto de costos y punto de transmisión del riesgo de pérdida o daño. Sus reglas no establecen por sí mismas la propiedad, el calendario o la moneda de pago, el precio ni los remedios por incumplimiento. Y en el grupo C, el destino hasta el que se paga el transporte no coincide necesariamente con el punto donde se transmite el riesgo.

FUENTE ICC, Incoterms and Commercial Contracts

> El Incoterm acordado determina el punto de transmisión del riesgo de pérdida o daño. Las consecuencias de una demanda menor dependen del compromiso de compra y de las demás condiciones del acuerdo.

Y mover una recepción tiene consecuencias más allá de la bodega. Las condiciones de los transportistas distinguen demurrage, detention y almacenamiento, con cargos aplicables después del tiempo libre correspondiente. Reprogramar un embarque antes de la carga no es lo mismo que retrasar la retirada de un contenedor de la terminal, su vaciado o la devolución del equipo: la flexibilidad comercial con la bodega no elimina las obligaciones con transportista, terminal o fraccionador.

FUENTE Maersk, Terms for Detention and Demurrage

## La flexibilidad que sí puede acordarse

Una prórroga de almacenamiento tampoco es solo contar meses. La guía de la OIV para transporte a granel contempla oxidación, contaminación y conservación de muestras representativas, y conviene evaluar el estado y la preparación del vino antes de extender un plazo. No hay un período universal de conservación para cualquier Malbec. Con todo eso en la mesa, estas son las preguntas que conviene dejar resueltas antes de comparar dos propuestas.

FUENTE OIV, Good Practices Guide for Bulk Wine Transportation

| Pregunta de negociación | Decisión que puede cambiar |
| --- | --- |
| ¿Qué parte de la previsión es compromiso firme, y para qué período? | Cantidad realmente reservada y saldo anual por resolver |
| ¿Se reserva un lote o un perfil abastecido progresivamente? | Inventario en origen, validación y capacidad comprometida |
| ¿Qué precio está fijado y qué componentes quedan variables? | Vino, preparación, flete, seguro, almacenamiento o revisiones |
| ¿Se paga al reservar, al cargar, al recibir o con crédito? | Necesidad financiera, que no se deduce del Incoterm |
| ¿Qué ajustes de retirada admite el programa, y con qué aviso? | Flexibilidad operativa real y coordinación logística |
| ¿Qué ocurre si se completa menos volumen al final del período? | Momento y alcance de la renegociación |
| ¿Cuándo pasa el riesgo físico y cuándo la propiedad? | Responsabilidad por daño frente a titularidad |
| ¿Quién detecta el desvío y cuándo se revisa la previsión? | Capacidad de reaccionar antes de que se cierre una ventana |

Preguntas recomendadas para ordenar la negociación. La frecuencia de revisión, los plazos de aviso y las tolerancias se acuerdan en cada proyecto.

Las condiciones de pago, reserva y almacenamiento deben quedar acordadas en cada proyecto.

Un programa sólido no necesita acertar cada retirada con un año de anticipación. Necesita distinguir qué volumen sostiene el acuerdo, qué movimientos admite el calendario y cómo actuar cuando la demanda cambia. Ahí un precio se convierte en una relación de abastecimiento.
