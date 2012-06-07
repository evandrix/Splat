graph = {'A': ['B', 'C'],
             'B': ['C', 'D'],
             'C': ['D'],
             'D': ['C'],
             'E': ['F'],
             'F': ['C']}

# returns first path found, via backtracking
def find_path(graph, start, end, path=[]):
       path = path + [start]
       if start == end:
           return path
       if not graph.has_key(start):
           return None
       for node in graph[start]:
           if node not in path:
               newpath = find_path(graph, node, end, path)
               if newpath: return newpath
       return None

# list of all paths (without cycles)
def find_all_paths(graph, start, end, path=[]):
       path = path + [start]
       if start == end:
           return [path]
       if not graph.has_key(start):
           return []
       paths = []
       for node in graph[start]:
           if node not in path:
               newpaths = find_all_paths(graph, node, end, path)
               for newpath in newpaths:
                   paths.append(newpath)
       return paths

def find_shortest_path(graph, start, end, path=[]):
       path = path + [start]
       if start == end:
           return path
       if not graph.has_key(start):
           return None
       shortest = None
       for node in graph[start]:
           if node not in path:
               newpath = find_shortest_path(graph, node, end, path)
               if newpath:
                   if not shortest or len(newpath) < len(shortest):
                       shortest = newpath
       return shortest

if __name__ == "__main__":
    """
        A -> B
        A -> C
        B -> C
        B -> D
        C -> D
        D -> C
        E -> F
        F -> C
    """

    assert find_path(graph, 'A', 'D') == ['A', 'B', 'C', 'D']
    assert find_all_paths(graph, 'A', 'D') == [['A', 'B', 'C', 'D'], ['A', 'B', 'D'], ['A', 'C', 'D']]
    assert find_shortest_path(graph, 'A', 'D') == ['A', 'B', 'D']
