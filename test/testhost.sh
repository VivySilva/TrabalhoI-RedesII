#!/bin/bash

declare -A ip_para_container
declare -A origem_tempos
declare -A origem_sucessos
declare -A origem_total

hosts=()
success=0
fail=0
total_time=0
total_success=0

# Lê o docker-compose.yml
container=""
while read -r line; do
  if [[ $line == *"container_name:"* ]]; then
    container=$(echo "$line" | awk '{print $2}')
  elif [[ $line == *"ipv4_address:"* ]]; then
    ip=$(echo "$line" | awk '{print $2}')
    ip_para_container["$ip"]="$container"
    if [[ "$container" =~ ^h[1-5][ab]$ ]]; then
      hosts+=("$container")
    fi
  fi
done < docker-compose.yml

ips=()
for ip in "${!ip_para_container[@]}"; do
  container="${ip_para_container[$ip]}"
  if [[ " ${hosts[*]} " =~ " $container " ]]; then
    ips+=("$ip")
  fi
done

# CSV
echo "origem,destino,destino_ip,duracao,status" > resultados_hosts.csv

echo "====================================="
echo "Teste de conectividade entre os hosts"
echo "====================================="

for origem in "${hosts[@]}"; do
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
      ((total_success++))
    else
      end=$(date +%s.%N)
      duracao=$(awk "BEGIN {print $end - $start}")
      status="0"
      ((fail++))
    fi

    total_time=$(awk "BEGIN {print $total_time + $duracao}")
    echo "-> $destino (${destino_ip}): ${duracao}s [$status]"

    origem_tempos[$origem]=$(awk "BEGIN {print ${origem_tempos[$origem]:-0} + $duracao}")
    origem_sucessos[$origem]=$(( ${origem_sucessos[$origem]:-0} + 1 ))
    origem_total[$origem]=$(( ${origem_total[$origem]:-0} + 1 ))
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
