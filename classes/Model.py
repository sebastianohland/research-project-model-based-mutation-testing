import random
import json


class Model:
    """FSM of the system under test in form of dictionary"""
    def __init__(self, model):
        self.model = model
        self.vertices = model['models'][0]['vertices']
        self.edges = model['models'][0]['edges']
        self.name = model['models'][0]['name']

    def print_edges(self):
        for i in self.edges:
            print(i)

    def print_vertices(self):
        for i in self.vertices:
            print(i)

    def convert_to_json(self):
        # Returns model in json format
        return json.dumps(self.model)

    def remove_edge(self, index):
        # Removes edge with index
        del self.edges[index]

    def remove_vertex(self, index):
        # Removes vertex with index
        del self.vertices[index]

    def reverse_edge(self, index):
        # Reverses edge (changes direction of source and target vertex) with index
        temp = self.edges[index]['sourceVertexId']
        self.edges[index]['sourceVertexId'] = self.edges[index]['targetVertexId']
        self.edges[index]['targetVertexId'] = temp

    def change_source(self, index):
        # Changes source of edge with index to another random source
        random_vertex_id = self.vertices[random.randint(0, len(self.vertices) - 1)]['id']
        self.edges[index]['sourceVertexId'] = random_vertex_id

    def change_sink(self, index):
        # Changes sink of edge with index to another random source
        random_vertex_id = self.vertices[random.randint(0, len(self.vertices) - 1)]['id']
        self.edges[index]['targetVertexId'] = random_vertex_id

    def remove_action(self, index):
        # Removes action from edge
        try:
            del self.edges[index]['actions']
        except KeyError:
            print("No action to remove from edge.")

    def replace_action(self, index):
        # Replaces action with another action from random edge
        try:
            # Makes sure the replaced action is not the same as the original action
            while True:
                random_edge = self.edges[random.randint(0, len(self.edges) - 1)]
                if "actions" in random_edge and self.edges[index]['actions'][0] != random_edge['actions'][0]:
                    break
            self.edges[index]['actions'][0] = random_edge['actions'][0]   # Replaces first action on edge
        except KeyError:
            print("No action to replace from edge.")
