def calculate_cyclomatic_complexity(nodes, edges):
    """
    Menghitung Cyclomatic Complexity menggunakan rumus: CC = E - N + 2
    """
    if not nodes:
        return 0
    
    # E = Jumlah Edges
    E = len(edges)
    
    # N = Jumlah Nodes
    N = len(nodes)
    
    # P = Connected Components (selalu 1 untuk satu method)
    P = 1 
    
    cc = E - N + (2 * P)
    return cc