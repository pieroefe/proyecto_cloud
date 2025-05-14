#!/bin/bash

# Fecha y hora actual
FECHA=$(date '+%Y-%m-%d %H:%M:%S')

# Usuario que inició sesión
USUARIO=$PAM_USER

# Dirección IP o terminal
ORIGEN=$PAM_RHOST
[ -z "$ORIGEN" ] && ORIGEN="local"

# Registrar en archivo de log personalizado
echo "$FECHA - Usuario: $USUARIO - Origen: $ORIGEN" >> /var/log/inicios_sesion_silkroad.log