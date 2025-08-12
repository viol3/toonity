import numpy as np
import sys


def load_obj(filename):
    vertices = []
    faces = []
    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('v '):
                parts = line.strip().split()
                vertices.append(np.array([float(parts[1]), float(parts[2]), float(parts[3])]))
            elif line.startswith('f '):
                parts = line.strip().split()
                # .obj dosyasında yüzler 1-based index ile belirtilir
                face = [int(p.split('/')[0]) - 1 for p in parts[1:]]
                faces.append(face)
    return np.array(vertices), faces

def build_adjacency(vertices, faces):
    adjacency = {i: set() for i in range(len(vertices))}
    for face in faces:
        for i in range(len(face)):
            v1 = face[i]
            v2 = face[(i + 1) % len(face)]
            adjacency[v1].add(v2)
            adjacency[v2].add(v1)
    return adjacency

def laplacian_smooth(vertices, adjacency, lambd=0.5, iterations=1):
    new_vertices = np.copy(vertices)
    for _ in range(iterations):
        temp_vertices = np.copy(new_vertices)
        for i, neighbors in adjacency.items():
            if not neighbors:
                continue
            neighbor_mean = np.mean([temp_vertices[j] for j in neighbors], axis=0)
            new_vertices[i] = new_vertices[i] + lambd * (neighbor_mean - new_vertices[i])
    return new_vertices

def write_obj(filename, vertices, faces):
    with open(filename, 'w') as f:
        for v in vertices:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for face in faces:
            face_str = ' '.join([str(idx + 1) for idx in face])
            f.write(f"f {face_str}\n")
filename = sys.argv[1]
vertices, faces = load_obj(filename)
adjacency = build_adjacency(vertices, faces)
smoothed_vertices = laplacian_smooth(vertices, adjacency, lambd=0.25, iterations=4)
write_obj(filename + "_smoothed.obj", smoothed_vertices, faces)
