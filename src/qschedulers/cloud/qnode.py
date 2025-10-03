import qsimpy.core as sp


class QuantumNode(sp.Resource):
    def __init__(self, env, backend, name=None):
        super().__init__(env, capacity=1, name=name or backend.name)
        self.backend = backend
        self.queue = []

    def __str__(self):
        return f"QuantumNode({self.name}, backend={self.backend.name})"
