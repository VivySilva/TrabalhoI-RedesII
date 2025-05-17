#!/bin/bash

# Cria um vetor associativo ip -> container
declare -A ip_para_container
declare -A roteadores_map
roteadores=()

success=0
fail=0

# Leitura do docker-compose para identificar os roteadores
while read -r line; do
  if [[ $line == *"container_name:"* ]]; then
    container=$(echo $line | awk '{print $2}')
  fi
  if [[ $line == *"ipv4_address:"* ]]; then
    ip=$(echo $line | awk '{print $2}')
    ip_para_container[$ip]=$container

    if [[ "$container" =~ ^r[0-9]+$ ]] && [[ -z "${roteadores_map[$container]}" ]]; then
      roteadores+=("$container")
      roteadores_map[$container]=1
    fi
  fi
done < docker-compose.yml

ips=("${!ip_para_container[@]}")

echo "======================================="
echo "Teste de conectividade entre roteadores"
echo "======================================="

for origem in "${roteadores[@]}"; do
  echo -e "\n### Pings a partir do $origem ###"
  for destino_ip in "${ips[@]}"; do
    destino_nome="${ip_para_container[$destino_ip]}"
    [[ "$origem" == "$destino_nome" ]] && continue
    printf "Pingando %-15s (%-8s)... " "$destino_ip" "$destino_nome"
    if docker exec "$origem" ping -c 1 -W 1 "$destino_ip" &> /dev/null; then
      echo "1"
      ((success++))
    else
      echo "0"
      ((fail++))
    fi
  done
done

total=$((success + fail))
echo -e "\nResumo:"
echo "Total: $total | Sucesso: $success | Falha: $fail"
[[ $total -gt 0 ]] && echo "Perda: $((100 * fail / total))%" || echo "Perda: N/A"
