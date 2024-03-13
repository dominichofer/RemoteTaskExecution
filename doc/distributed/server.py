from rte import Server, GrpcServer


if __name__ == "__main__":
    server = Server(task_timeout=1)
    rpc_server = GrpcServer(server, port=50051)
    rpc_server.start()
    rpc_server.wait_for_termination()
