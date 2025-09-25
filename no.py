import socket
import json
import time
import random
import math


class ComputeNode:
    def __init__(self, main_host="localhost", main_port=8888):
        self.main_host = main_host
        self.main_port = main_port
        self.socket = None

    def connect_to_main(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.main_host, self.main_port))
            print(f"Conectado ao nó principal em {self.main_host}:{self.main_port}")
            return True
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            return False

    def send_ready_signal(self):
        message = {"type": "ready"}
        self.socket.send(json.dumps(message).encode("utf-8"))

    def process_task(self, task):
        task_type = task["type"]
        data = task["data"]

        print(f"Processando tarefa {task['task_id']}: {task_type}")

        if task_type == "calculate_prime":
            result = self.calculate_prime(data["number"])
        elif task_type == "process_image":
            result = self.process_image_simulation(data["iterations"])
        elif task_type == "analyze_data":
            result = self.analyze_data_simulation(data["iterations"])
        else:
            result = {"error": "Tipo de tarefa desconhecido"}

        return result

    def calculate_prime(self, n):
        time.sleep(1)
        if n < 2:
            return {"number": n, "is_prime": False}

        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return {"number": n, "is_prime": False}

        return {"number": n, "is_prime": True}

    def process_image_simulation(self, iterations):
        for i in range(iterations):
            time.sleep(0.5)
            progress = (i + 1) / iterations * 100
            print(f"\tProcessando imagem... {progress:.1f}%")

        return {
            "processed": True,
            "iterations": iterations,
            "result": "image_processed_successfully",
        }

    def analyze_data_simulation(self, iterations):
        total = 0
        for i in range(iterations):
            time.sleep(0.3)
            total += random.random()
            print(f"\tAnalisando dados... {i+1}/{iterations}")

        return {
            "analysis_complete": True,
            "average": total / iterations,
            "iterations": iterations,
        }

    def start_working(self):
        if not self.connect_to_main():
            return

        try:
            while True:
                self.send_ready_signal()

                data = self.socket.recv(1024).decode("utf-8")
                if not data:
                    break

                task = json.loads(data)
                print(f"Nova tarefa recebida: {task['task_id']}")

                result = self.process_task(task)

                response = {
                    "type": "result",
                    "task_id": task["task_id"],
                    "result": result,
                }
                self.socket.send(json.dumps(response).encode("utf-8"))
                print(f"Resultado enviado para o principal")

        except Exception as e:
            print(f"Erro durante execução: {e}")
        finally:
            self.socket.close()


if __name__ == "__main__":
    import sys

    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8888

    print(f"Iniciando nó de computação...")
    print(f"\tConectando em: {host}:{port}")

    worker = ComputeNode(host, port)
    worker.start_working()
