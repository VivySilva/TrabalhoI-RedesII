#!/bin/bash

declare -A ip_para_container
hosts=()

# Leitura do docker-compose.yml
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

# Gera lista de IPs dos hosts
ips=()
for ip in "${!ip_para_container[@]}"; do
  container="${ip_para_container[$ip]}"
  if [[ " ${hosts[@]} " =~ " ${container} " ]]; then
    ips+=("$ip")
  fi
done

success=0
fail=0

echo "=========================================="
echo "Teste de conectividade ICMP entre os hosts:"
echo "=========================================="

# Loop de testes de ping
for origem in "${hosts[@]}"; do
  echo -e "\n### Pings a partir de $origem ###"
  for destino_ip in "${ips[@]}"; do
    destino="${ip_para_container[$destino_ip]}"
    [[ "$origem" == "$destino" ]] && continue
    printf "Pingando %-15s (%-8s)... " "$destino_ip" "$destino"
    if docker exec "$origem" ping -c 1 -W 1 "$destino_ip" &> /dev/null; then
      echo "✔️"
      ((success++))
    else
      echo "❌"
      ((fail++))
    fi
  done
done

# Resumo
total=$((success + fail))
echo -e "\nResumo (Hosts):"
echo "Total de testes: $total"
echo "Sucesso: $success"
echo "Falha: $fail"
[[ $total -gt 0 ]] && echo "Perda: $((100 * fail / total))%" || echo "Perda: N/A"
