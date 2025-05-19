#!/bin/bash

declare -A ip_para_container
declare -A roteadores_map
roteadores=()

success=0
fail=0
total_time=0

# Leitura do docker-compose para mapear roteadores
container=""
while read -r line; do
  if [[ $line == *"container_name:"* ]]; then
    container=$(echo $line | awk '{print $2}')
  elif [[ $line == *"ipv4_address:"* ]]; then
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
  echo -e "\n---- Pings a partir de $origem ----"
  for destino_ip in "${ips[@]}"; do
    destino="${ip_para_container[$destino_ip]}"
    [[ "$origem" == "$destino" ]] && continue

    start=$(date +%s.%N)
    if docker exec "$origem" ping -c 1 -W 1 "$destino_ip" &> /dev/null; then
      end=$(date +%s.%N)
      duracao=$(awk "BEGIN {print $end - $start}")
      status="1"
      ((success++))
    else
      end=$(date +%s.%N)
      duracao=$(awk "BEGIN {print $end - $start}")
      status="0"
      ((fail++))
    fi

    total_time=$(awk "BEGIN {print $total_time + $duracao}")
    echo "-> $destino (${destino_ip}): ${duracao}s [$status]"
  done
done

# Resumo
total=$((success + fail))
taxa_sucesso=$(awk "BEGIN {printf \"%.2f\", ($success / $total) * 100}")
taxa_falha=$(awk "BEGIN {printf \"%.2f\", ($fail / $total) * 100}")
media_global=$(awk "BEGIN {printf \"%.4f\", $total_time / $total}")

echo -e "\n---- Resumo Geral ----"
echo "Total de testes: $total"
echo "Sucesso: $success | Percentual: $taxa_sucesso%"
echo "Falha: $fail | Percentual: $taxa_falha%"
echo "Média global de tempo: ${media_global}s"
