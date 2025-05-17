#!/bin/bash

# Obtém o IP da interface principal
IP=$(ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')

# Define o gateway baseado na subrede
GATEWAY=$(echo "$IP" | awk -F. '{print $1"."$2"."$3".2"}')

# Substitui o gateway padrão
ip route del default 2>/dev/null
ip route add default via "$GATEWAY"

echo "[START] Gateway padrão configurado para $GATEWAY"

# Mantém o container vivo
while true; do sleep 1000; done
