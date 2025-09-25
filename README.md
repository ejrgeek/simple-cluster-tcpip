# PROJETO EXEMPLO CLUSTER PYTHON - SISTEMAS DISTRIBUIDOS

### Instalação
1. Python 3.10.x

### Execução

Principal:
```bash
python main.py
```

Processadores/Nós:
```bash
python no.py IP_PRINCIPAL 8888
```

### O projeto já possui:
- Comunicação TCP/IP
- Pseudo Balanceamento de Carga Automático na distribuição de tarefas:
    - É possível montar uma lógica com estrategias da seguinte maneira:
    ```python
    self.load_balancing_strategy = 'least_connections' # definido no __init__
    # no momento da distribuição, antes do envio:
    if self.load_balancing_strategy == 'round_robin':
        node_id = self.round_robin_balancing(available_nodes)
    elif self.load_balancing_strategy == 'least_connections':
        node_id = self.least_connections_balancing(available_nodes)
    elif self.load_balancing_strategy == 'weighted':
        node_id = self.weighted_balancing(available_nodes)
    else:
        node_id = available_nodes[0]
    ```

A partir daí é implementar as estratégias, como, por exemplo:

**Round Robin**
```python
def round_robin_balancing(self, available_nodes):
    if not hasattr(self, 'rr_counter'):
        self.rr_counter = 0
    
    available_nodes.sort()
    node_id = available_nodes[self.rr_counter % len(available_nodes)]
    self.rr_counter += 1
    
    return node_id
```
**Least Connections**
```python
def least_connections_balancing(self, available_nodes):
    node_loads = []
    for node_id in available_nodes:
        tasks_completed = self.worker_nodes[node_id]['tasks_completed']
        node_loads.append((node_id, tasks_completed))
    
    node_loads.sort(key=lambda x: x[1])
    return node_loads[0][0]
```
**Weighted Balancing**
```python
def weighted_balancing(self, available_nodes):
    node_weights = []
    
    for node_id in available_nodes:
        node_info = self.worker_nodes[node_id]
        tasks_completed = node_info['tasks_completed']
        
        
        weight = max(1, 100 - tasks_completed)
        
        node_weights.append((node_id, weight))
    
    node_weights.sort(key=lambda x: x[1])
    return node_weights[0][0]
```

**Configuração da Estratégia**
```python
def set_load_balancing_strategy(self, strategy):
    valid_strategies = ['round_robin', 'least_connections', 'weighted', 'first_available']
    if strategy in valid_strategies:
        self.load_balancing_strategy = strategy
        print(f"Estratégia de balanceamento alterada para: {strategy}")
    else:
        print(f"Estratégia inválida. Use: {valid_strategies}")
```

**Exibir informação da estratégia**
```python
def get_load_balancing_info(self):
    available_nodes = self.get_available_nodes()
    
    node_info = []
    for node_id in available_nodes:
        info = self.worker_nodes[node_id]
        node_info.append({
            'node_id': node_id,
            'tasks_completed': info['tasks_completed'],
            'status': info['status'],
            'address': info['addr']
        })
    
    return {
        'strategy': self.load_balancing_strategy,
        'available_nodes': len(available_nodes),
        'node_details': node_info
    }
```

**Bloco de Iteração com Operador**
```python
if __name__ == "__main__":
    main = ImprovedClusterMain().start_server()
    
    print("CLUSTER COM BALANCEAMENTO DE CARGA AVANÇADO")
    print("Estratégias disponíveis:")
    print("1. round_robin - Distribuição igualitária")
    print("2. least_connections - Menor número de tarefas")
    print("3. weighted - Baseado em desempenho")
    print("4. first_available - Estratégia básica (padrão anterior)")
    
    while True:
        print("\n@@@@@ SISTEMA DE CLUSTER AVANÇADO @@@@@")
        print("1. Criar tarefas de teste")
        print("2. Status do cluster")
        print("3. Mudar estratégia de balanceamento")
        print("4. Informações detalhadas de balanceamento")
        print("5. Sair")
        
        choice = input("Escolha uma opção: ")
        
        if choice == '1':
            task_types = ['calculate_prime', 'process_image', 'analyze_data']
            num_tasks = int(input("Quantas tarefas criar? ") or "3")
            
            for i in range(num_tasks):
                task_id = main.create_task(
                    random.choice(task_types),
                    {'number': random.randint(100, 1000), 'iterations': random.randint(1, 5)}
                )
                print(f"Tarefa {task_id} criada!")
                
        elif choice == '2':
            status = main.get_cluster_status()
            lb_info = main.get_load_balancing_info()
            
            print(f"\nStatus do Cluster:")
            print(f"\tEstratégia: {lb_info['strategy']}")
            print(f"\tNós conectados: {status['total_nodes']}")
            print(f"\tNós disponíveis: {lb_info['available_nodes']}")
            print(f"\tTarefas completadas: {status['total_tasks_completed']}")
            print(f"\tTarefas pendentes: {status['pending_tasks']}")
            
        elif choice == '3':
            print("\nEstratégias de Balanceamento:")
            print("\tround_robin, least_connections, weighted, first_available")
            strategy = input("Digite a estratégia desejada: ")
            main.set_load_balancing_strategy(strategy)
            
        elif choice == '4':
            lb_info = main.get_load_balancing_info()
            print(f"\nInformações de Balanceamento:")
            print(f"\tEstratégia atual: {lb_info['strategy']}")
            print(f"\tNós disponíveis: {lb_info['available_nodes']}")
            
            for node in lb_info['node_details']:
                print(f"\tNó {node['node_id']}: {node['tasks_completed']} tarefas completadas")
                
        elif choice == '5':
            break
            
        time.sleep(1)
```