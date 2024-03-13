from rte import BatchClient, RemoteServer


if __name__ == "__main__":
    server = RemoteServer("localhost:50051")

    client = BatchClient(server, refresh_time=0.5)
    results = client.solve([b"task_1", b"task_2", b"task_3"])
    print(results)
    assert results == [b"TASK_1", b"TASK_2", b"TASK_3"]
