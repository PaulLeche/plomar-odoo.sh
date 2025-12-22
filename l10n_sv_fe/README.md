## Info sobre Retención de IVA del 1%

- El módulo espera que se agregue en cada línea de factura el impuesto con el nombre exacto: **IVA Retenido**. Esto asegura que se reste el monto adecuado automáticamente en Odoo y solo se envíen esos valores en el JSON, sin necesidad de recalcular información por detrás.
- Para informarle al certificador (INFILE) que el CCF o Factura lleva retención se agrega el campo "retener_iva": "true" dentro de "documento". INFILE se encarga de validar los montos por su parte y agregar en el PDF el monto correspondiente al IVA Retenido.
- El impuesto de **IVA Retenido** debe configurarse como tipo Venta y en negativo (-1.00%) y que no se afecte por impuestos previos debido a que se debe calcular del monto de la factura o ccf antes de IVA.