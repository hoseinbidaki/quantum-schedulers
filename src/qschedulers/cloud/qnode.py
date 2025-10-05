# from external.qsimpy.qsimpy import QNode
import simpy as sp

class QuantumNode(sp.Resource):
    """
    Wraps a quantum backend as a qsimpy Resource (with a queue).
    """
    def __init__(self, env: sp.Environment, backend, name=None):
        super().__init__(env, capacity=1)
        self.backend = backend
