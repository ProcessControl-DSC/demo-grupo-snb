# PC Stock Last Purchase Price

Actualiza el coste estándar de los productos con el precio unitario de la última compra recibida, configurable por categoría de producto.

## Funcionamiento

1. En `Inventario → Configuración → Categorías de productos`, cada categoría incorpora la casilla **Usar precio de la última compra**.
2. Cuando una recepción se valida (`stock.move._action_done` con `picking_type.code = 'incoming'`), el módulo recorre los productos cuya categoría tiene la casilla marcada y actualiza `standard_price = price_unit` del movimiento.
3. Opera por encima del método de coste estándar (`Precio estándar`, `FIFO`, `AVCO`), de modo que se mantiene la traza contable nativa mientras el campo de coste refleja el último precio pagado.

## Origen

Solicitado en preventa MDTEL (v19) — alternativa al módulo OCA `stock_cost_method_last` que no está portado a la rama 19.0 y al módulo de pago de App Store `Last Purchase Price as Cost Price`. Implementación propia Process Control, LGPL-3.

## Versión

`19.0.1.0.0` · Process Control · 2026.
