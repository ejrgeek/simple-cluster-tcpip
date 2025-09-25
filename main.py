import socket
import threading
import time
import json
from queue import Queue
import random


class ClusterMain:
    def __init__(self, host="localhost", port=8888):
        self.host = host
        self.port = port
        self.worker_nodes = {}
        self.task_queue = Queue()
        self.results = {}
        self.node_id_counter = 1

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        print(f"Nó Principal iniciado em {self.host}:{self.port}")
        print("Aguardando conexões dos nós de computação/processamento...")

        accept_thread = threading.Thread(target=self.accept_connections)
        accept_thread.daemon = True
        accept_thread.start()

        task_thread = threading.Thread(target=self.distribute_tasks)
        task_thread.daemon = True
        task_thread.start()

        return self

    def accept_connections(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            node_id = self.node_id_counter
            self.node_id_counter += 1

            worker_thread = threading.Thread(
                target=self.handle_worker, args=(client_socket, addr, node_id)
            )
            worker_thread.daemon = True
            worker_thread.start()

            print(f"Nó {node_id} conectado de {addr}")

    def handle_worker(self, client_socket, addr, node_id):
        self.worker_nodes[node_id] = {
            "socket": client_socket,
            "addr": addr,
            "status": "available",
            "tasks_completed": 0,
        }

        try:
            while True:
                data = client_socket.recv(1024).decode("utf-8")
                if not data:
                    break

                message = json.loads(data)
                if message["type"] == "ready":
                    self.worker_nodes[node_id]["status"] = "available"
                elif message["type"] == "result":
                    task_id = message["task_id"]
                    self.results[task_id] = message["result"]
                    self.worker_nodes[node_id]["status"] = "available"
                    self.worker_nodes[node_id]["tasks_completed"] += 1
                    print(f"Resultado recebido do nó {node_id}: {message['result']}")

        except Exception as e:
            print(f"Erro no nó {node_id}: {e}")
        finally:
            if node_id in self.worker_nodes:
                del self.worker_nodes[node_id]
            client_socket.close()
            print(f"Nó {node_id} desconectado")

    def create_task(self, task_type, data):
        task_id = f"task_{int(time.time())}_{random.randint(1000,9999)}"
        task = {"task_id": task_id, "type": task_type, "data": data}
        self.task_queue.put(task)
        return task_id

    def distribute_tasks(self):
        while True:
            if not self.task_queue.empty():
                available_nodes = [
                    node_id
                    for node_id, info in self.worker_nodes.items()
                    if info["status"] == "available"
                ]

                if available_nodes:
                    task = self.task_queue.get()
                    node_id = available_nodes[0]

                    message = json.dumps(task)
                    self.worker_nodes[node_id]["socket"].send(message.encode("utf-8"))
                    self.worker_nodes[node_id]["status"] = "busy"

                    print(f"Tarefa {task['task_id']} enviada para nó {node_id}")

            time.sleep(0.1)

    def get_cluster_status(self):
        available_nodes = len(
            [n for n in self.worker_nodes.values() if n["status"] == "available"]
        )
        busy_nodes = len(
            [n for n in self.worker_nodes.values() if n["status"] == "busy"]
        )

        return {
            "total_nodes": len(self.worker_nodes),
            "available_nodes": available_nodes,
            "busy_nodes": busy_nodes,
            "total_tasks_completed": sum(
                n["tasks_completed"] for n in self.worker_nodes.values()
            ),
            "pending_tasks": self.task_queue.qsize(),
        }


if __name__ == "__main__":
    main = ClusterMain().start_server()

    while True:
        print("\n@@@@@ SISTEMA DE CLUSTER @@@@@")
        print("1. Criar tarefa de processamento")
        print("2. Status do cluster")
        print("3. Sair")

        choice = input("Escolha uma opção: ")

        if choice == "1":
            task_types = ["calculate_prime", "process_image", "analyze_data"]
            for i in range(3):
                task_id = main.create_task(
                    random.choice(task_types),
                    {
                        "number": random.randint(100, 1000),
                        "iterations": random.randint(1, 10),
                    },
                )
                print(f"Tarefa {task_id} criada!")

        elif choice == "2":
            status = main.get_cluster_status()
            print(f"\nStatus do Cluster:")
            print(f"\tNós conectados: {status['total_nodes']}")
            print(f"\tNós disponíveis: {status['available_nodes']}")
            print(f"\tNós ocupados: {status['busy_nodes']}")
            print(f"\tTarefas completadas: {status['total_tasks_completed']}")
            print(f"\tTarefas pendentes: {status['pending_tasks']}")

        elif choice == "3":
            break

        time.sleep(1)
