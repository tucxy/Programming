import os
import pygame
import networkx as nx
import math

# Constants
NEW_LEFT_TAB_WIDTH = 350
DEFAULT_WIDTH, DEFAULT_HEIGHT = 1200, 800
RIGHT_TAB_WIDTH = 200
MARGIN = 20
DARK_GREEN = (0, 128, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)

#Function to find the longest path in an undirected tree
def find_longest_path(tree):
    def bfs_farthest_node(tree, start):
        visited = {start}
        queue = [(start, 0)]
        farthest_node, max_distance = start, 0

        while queue:
            current_node, distance = queue.pop(0)
            for neighbor in tree.neighbors(current_node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, distance + 1))
                    if distance + 1 > max_distance:
                        farthest_node, max_distance = neighbor, distance + 1

        return farthest_node, max_distance

    #First BFS to find one endpoint of the longest path
    start_node = next(iter(tree.nodes()))
    farthest_node, _ = bfs_farthest_node(tree, start_node)

    #Second BFS to find the longest path from the farthest node
    farthest_node, _ = bfs_farthest_node(tree, farthest_node)

    #Get the actual path
    visited = {farthest_node}
    path = [farthest_node]
    queue = [(farthest_node, path)]

    while queue:
        current_node, current_path = queue.pop(0)
        if len(current_path) > len(path):
            path = current_path

        for neighbor in tree.neighbors(current_node):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, current_path + [neighbor]))

    return path

#Function to arrange nodes along the longest path and branch out leaves
def arrange_tree(tree, pos, start_x, start_y, x_spacing=50, y_spacing=50):
    longest_path = find_longest_path(tree)
    x = start_x
    y = start_y

    #Arrange nodes along the longest path
    for node in longest_path:
        pos[node] = (x, y)
        x += x_spacing

    #Arrange other nodes branching out from the longest path
    for node in longest_path:
        leaf_y = y + y_spacing
        for neighbor in tree.neighbors(node):
            if neighbor not in pos:
                pos[neighbor] = (pos[node][0], leaf_y)
                leaf_y += y_spacing

    #Arrange any remaining nodes that might not be connected
    remaining_nodes = set(tree.nodes()) - set(pos.keys())
    for node in remaining_nodes:
        pos[node] = (x, y)
        y += y_spacing

    return pos

#Function to draw a grid
def draw_grid(screen, width, height, spacing_x, spacing_y):
    for x in range(0, width, spacing_x):
        pygame.draw.line(screen, GRAY, (x, 0), (x, height))
    for y in range(0, height, spacing_y):
        pygame.draw.line(screen, GRAY, (0, y), (width, y))

#Function to draw buttons
def draw_button(screen, label, state, position):
    color = DARK_GREEN if state else RED
    pygame.draw.rect(screen, color, (*position, 140, 50))
    font = pygame.font.SysFont('Arial', 18)
    text = font.render(label, True, (0, 0, 0))
    text_rect = text.get_rect(center=(position[0] + 70, position[1] + 25))
    screen.blit(text, text_rect)


def draw_graph(mod, screen, G, pos, edge_length_func, edge_sublabel_func, vertex_sublabel_func, 
               show_vertex_labels, show_edge_labels, show_vertex_sublabels, show_edge_sublabels, vertex_scale, custom_colors):
    for edge in G.edges():
        edge_color = custom_colors.get((G, "edge", edge), (200, 200, 200))  # Default to gray
        pygame.draw.line(screen, edge_color, pos[edge[0]], pos[edge[1]], int(2 * vertex_scale))
        
        #Compute edge label and sublabel
        if edge_length_func:
            try:
                edge_label = edge_length_func(edge[0], edge[1])
            except Exception:
                edge_label = " "
        elif isinstance(edge[0], int) and isinstance(edge[1], int):
            if mod is not None:
                edge_label = min(abs(edge[0] - edge[1]), mod - abs(edge[0] - edge[1]))
            else:
                edge_label = abs(edge[0] - edge[1])
        else:
            edge_label = " "

        if edge_sublabel_func:
            try:
                edge_sublabel = edge_sublabel_func(edge[0], edge[1]) if show_edge_sublabels else None
            except Exception:
                edge_sublabel = " "
        else:
            edge_sublabel = None

        #Store labels in the graph attributes
        G.edges[edge]["label"] = str(edge_label) if show_edge_labels else ""
        G.edges[edge]["sublabel"] = str(edge_sublabel) if show_edge_sublabels else ""

        #Positioning for drawing
        mid_x = (pos[edge[0]][0] + pos[edge[1]][0]) / 2
        mid_y = (pos[edge[0]][1] + pos[edge[1]][1]) / 2
        angle = math.atan2(pos[edge[1]][1] - pos[edge[0]][1], pos[edge[0]][0] - pos[edge[1]][0])
        angle_deg = math.degrees(angle)
        if angle_deg < -90 or angle_deg > 90:
            angle_deg += 180
            angle_deg %= 360

        font = pygame.font.SysFont('Arial', int(12 * vertex_scale))
        sub_font = pygame.font.SysFont('Arial', int(10 * vertex_scale))

        #Draw edge labels
        if show_edge_labels:
            edge_label_color = custom_colors.get((G, "edge_label", edge), DARK_GREEN)  # Default to DARK_GREEN
            text = font.render(str(edge_label), True, edge_label_color)
            text = pygame.transform.rotate(text, -angle_deg)
            text_rect = text.get_rect(center=(mid_x, mid_y))
            screen.blit(text, text_rect.topleft)

        #Draw edge subscript labels
        if show_edge_sublabels and edge_sublabel is not None:
            sub_label_color = custom_colors.get((G, "edge_sublabel", edge), (255, 0, 0))  #Default to red
            sub_text = sub_font.render(str(edge_sublabel), True, sub_label_color)
            sub_text = pygame.transform.rotate(sub_text, -angle_deg)
            sub_text_rect = sub_text.get_rect(center=(mid_x, mid_y))
            if show_edge_labels:
                screen.blit(sub_text, (text_rect.right - 5, text_rect.bottom - 5))
            else:
                screen.blit(sub_text, sub_text_rect.topleft)

    for node in G.nodes():
        node_color = custom_colors.get((G, "node", node), (0, 0, 255))  #Default to blue
        pygame.draw.circle(screen, node_color, (int(pos[node][0]), int(pos[node][1])), int(5 * vertex_scale))
        
        if isinstance(node, str):
            node_label = node
            vertex_sublabel = None
        else:
            node_label = str(node) if mod is None else str(node % mod)
            if vertex_sublabel_func:
                try:
                    vertex_sublabel = vertex_sublabel_func(node) if show_vertex_sublabels else None
                except Exception:
                    vertex_sublabel = " "
            else:
                vertex_sublabel = None

        G.nodes[node]["sublabel"] = str(vertex_sublabel) if show_vertex_sublabels else ""

        font = pygame.font.SysFont('Arial', int(12 * vertex_scale))
        sub_font = pygame.font.SysFont('Arial', int(10 * vertex_scale))

        #Draw vertex labels
        if show_vertex_labels:
            node_label_color = custom_colors.get((G, "node_label", node), (0, 0, 0))  #Default to black
            text = font.render(node_label, True, node_label_color)
            text_rect = text.get_rect()
            screen.blit(text, (pos[node][0] + 8, pos[node][1] - 5))

        #Draw vertex subscript labels
        if show_vertex_sublabels and vertex_sublabel is not None:
            vertex_sublabel_color = custom_colors.get((G, "vertex_sublabel", node), (255, 0, 0))  #Default to red
            sub_text = sub_font.render(str(vertex_sublabel), True, vertex_sublabel_color)
            if show_vertex_labels:
                screen.blit(sub_text, (pos[node][0] + 8 + text_rect.width - 2, pos[node][1] - 5 + text_rect.height - 2))
            else:
                screen.blit(sub_text, (pos[node][0] + 8, pos[node][1] - 5))


def get_tikz_color(rgb):
    """Convert RGB values to TikZ default colors."""
    color_map = {
        (0, 0, 0): "black",
        (255, 255, 255): "white",
        (0, 255, 255): "cyan",
        (255, 192, 203): "pink",
        (255, 0, 0): "red",
        (0, 255, 0): "green",
        (0, 0, 255): "blue",
        (255, 255, 0): "yellow",
        (255, 165, 0): "orange",
        (128, 0, 128): "purple",
    }
    return color_map.get(tuple(rgb), "black")  #Default to black if color is not found

def save_as_latex(graphs, pos_list, save_info, colored_elements,
                  show_vertex_labels, show_edge_labels, show_vertex_sublabels, show_edge_sublabels):
    if not save_info or len(save_info) != 2:
        print("Save info must be a list [name, path]")
        return

    name, path = save_info
    os.makedirs(os.path.join(path, name), exist_ok=True)
    file_path = os.path.join(path, name, f"{name}.tex")

    with open(file_path, "w") as f:
        f.write("\\documentclass{standalone}\n")
        f.write("\\usepackage{amsmath}\n")
        f.write("\\usepackage{tikz}\n")
        f.write("\\begin{document}\n")
        f.write("\\begin{tikzpicture}\n")

        for i, (G, pos) in enumerate(zip(graphs, pos_list), start=1):
            graph_name = f"G{i}"  #Name of graph

            # Nodes
            for node, (x, y) in pos.items():
                y = -y  #Reflect the y-coordinate for TikZ
                color = get_tikz_color(colored_elements.get((G, "node", node), (0, 0, 0)))
                label_color = get_tikz_color(colored_elements.get((G, "node_label", node), (0, 0, 0)))

                #Handle labels and subscripts
                vertex_label = f"{node}" if show_vertex_labels else ""
                vertex_sublabel = G.nodes[node].get("sublabel", "") if show_vertex_sublabels else ""
                label_with_subscript = f"{vertex_label}_{{{vertex_sublabel}}}" if vertex_sublabel else vertex_label

                #Wrap in math mode
                math_label = f"\\textcolor{{{label_color}}}{{${label_with_subscript}$}}"

                #Node naming convention: GiNj
                f.write(f"\\node[fill={color}, circle, inner sep=2pt, label=above:{{{math_label}}}] "
                        f"({graph_name}N{node}) at ({x / 100},{y / 100}) {{}};\n")

            # Edges
            for edge in G.edges():
                edge_color = get_tikz_color(colored_elements.get((G, "edge", edge), (0, 0, 0)))
                edge_label_color = get_tikz_color(colored_elements.get((G, "edge_label", edge), (0, 0, 0)))
                edge_label = G.edges[edge].get("label", "") if show_edge_labels else ""
                edge_sublabel = G.edges[edge].get("sublabel", "") if show_edge_sublabels else ""

                #Handle labels and subscripts
                edge_label_with_subscript = f"{edge_label}_{{{edge_sublabel}}}" if edge_sublabel else edge_label

                #Wrap in math mode
                math_edge_label = f"\\textcolor{{{edge_label_color}}}{{${edge_label_with_subscript}$}}"

                #Define the edge using node names
                f.write(f"\\draw[draw={edge_color}, shorten >=0pt, shorten <=0pt] "
                        f"({graph_name}N{edge[0]}) -- ({graph_name}N{edge[1]})")

                #Add labels if they exist
                if edge_label or edge_sublabel:
                    f.write(f" node[midway, above] {{{math_edge_label}}};\n")
                else:
                    f.write(";\n")

        f.write("\\end{tikzpicture}\n")
        f.write("\\end{document}\n")

    print(f"Graph saved to {file_path}")





#viz
def viz(graphs, mod=None, edge_length_func=None, edge_sublabel_func=None, vertex_sublabel_func=None, save_info=None):
    pygame.init()
    WIDTH, HEIGHT = DEFAULT_WIDTH, DEFAULT_HEIGHT
    screen = pygame.display.set_mode((WIDTH + RIGHT_TAB_WIDTH, HEIGHT))
    pygame.display.set_caption("Tikzgrapher")

    pos_list = []
    for G in graphs:
        pos = {}
        start_x = NEW_LEFT_TAB_WIDTH + MARGIN
        start_y = MARGIN
        arrange_tree(G, pos, start_x, start_y)
        pos_list.append(pos)

    running = True
    show_vertex_labels = True
    show_edge_labels = True
    show_vertex_sublabels = vertex_sublabel_func is not None
    show_edge_sublabels = edge_sublabel_func is not None
    show_grid = False
    selected_node = None
    initial_graph_position = None
    graph_dragging = False
    graph_being_dragged = None
    right_tab_visible = True
    paintbrush_color = None

    #Full palette with all 10 basic TikZ colors
    palette_colors = [
        (0, 0, 0),  #Black
        (255, 255, 255),  #White
        (0, 255, 255),  #Cyan
        (255, 192, 203),  #Pink
        (0, 0, 255),  #Blue
        (255, 255, 0),  #Yellow
        (255, 165, 0),  #Orange
        (128, 0, 128),  #Violet
        (255, 0, 0),  #Red
        (0, 255, 0),  #Green
    ]
    colored_elements = {}

    button_positions = [
        ("Save", lambda: True, (WIDTH + 20, 20)),
        ("Vertex Labels", lambda: show_vertex_labels, (WIDTH + 20, 90)),
        ("Edge Labels", lambda: show_edge_labels, (WIDTH + 20, 160)),
        ("Vertex Sublabels", lambda: show_vertex_sublabels, (WIDTH + 20, 230)),
        ("Edge Sublabels", lambda: show_edge_sublabels, (WIDTH + 20, 300)),
        ("Grid", lambda: show_grid, (WIDTH + 20, 370)),
    ]

    palette_positions = [(WIDTH + 20 + (i % 5) * 30, 440 + (i // 5) * 30) for i in range(len(palette_colors))]
    mouse_icon_position = (WIDTH + 20, 510)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  #Left click
                    for G, pos in zip(graphs, pos_list):
                        for node, (x, y) in pos.items():
                            if (event.pos[0] - x) ** 2 + (event.pos[1] - y) ** 2 < 100:
                                if paintbrush_color:  #Color the node
                                    colored_elements[(G, "node", node)] = paintbrush_color
                                else:
                                    selected_node = (G, node)
                                break
                        for edge in G.edges():
                            mid_x = (pos[edge[0]][0] + pos[edge[1]][0]) / 2
                            mid_y = (pos[edge[0]][1] + pos[edge[1]][1]) / 2
                            if (event.pos[0] - mid_x) ** 2 + (event.pos[1] - mid_y) ** 2 < 100:
                                if paintbrush_color:  #Color the edge
                                    colored_elements[(G, "edge", edge)] = paintbrush_color
                                break
                        for edge in G.edges():
                            mid_x = (pos[edge[0]][0] + pos[edge[1]][0]) / 2
                            mid_y = (pos[edge[0]][1] + pos[edge[1]][1]) / 2
                            if (event.pos[0] - mid_x) ** 2 + (event.pos[1] - mid_y) ** 2 < 100:
                                if paintbrush_color:  #Color the edge label
                                    colored_elements[(G, "edge_label", edge)] = paintbrush_color
                                break
                        for node, (x, y) in pos.items():
                            if (event.pos[0] - (x + 8)) ** 2 + (event.pos[1] - (y - 5)) ** 2 < 100:
                                if paintbrush_color:  #Color the vertex label
                                    colored_elements[(G, "node_label", node)] = paintbrush_color
                                break
                    #Button and palette interaction
                    for label, state_getter, position in button_positions:
                        rect = pygame.Rect(*position, 140, 50)
                        if rect.collidepoint(event.pos):
                            if label == "Save" and save_info:
                                save_as_latex(
                                    graphs,
                                    pos_list,
                                    save_info,
                                    colored_elements,
                                    show_vertex_labels,
                                    show_edge_labels,
                                    show_vertex_sublabels,
                                    show_edge_sublabels,
                                )
                            elif label == "Vertex Labels":
                                show_vertex_labels = not show_vertex_labels
                            elif label == "Edge Labels":
                                show_edge_labels = not show_edge_labels
                            elif label == "Vertex Sublabels":
                                show_vertex_sublabels = not show_vertex_sublabels
                            elif label == "Edge Sublabels":
                                show_edge_sublabels = not show_edge_sublabels
                            elif label == "Grid":
                                show_grid = not show_grid
                            break
                    for i, (x, y) in enumerate(palette_positions):
                        if x <= event.pos[0] <= x + 20 and y <= event.pos[1] <= y + 20:
                            paintbrush_color = palette_colors[i]
                            break
                    if mouse_icon_position[0] <= event.pos[0] <= mouse_icon_position[0] + 40 and mouse_icon_position[1] <= event.pos[1] <= mouse_icon_position[1] + 40:
                        paintbrush_color = None
                        break
                elif event.button == 3:  #Right click
                    if not paintbrush_color:
                        for i, (G, pos) in enumerate(zip(graphs, pos_list)):
                            for node, (x, y) in pos.items():
                                if (event.pos[0] - x) ** 2 + (event.pos[1] - y) ** 2 < 100:
                                    graph_being_dragged = i  #Set the graph being dragged
                                    initial_graph_position = event.pos
                                    graph_dragging = True
                                    break
                            if graph_being_dragged is not None:
                                break

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  #Left click
                    selected_node = None
                elif event.button == 3:  #Right click
                    graph_dragging = False
                    graph_being_dragged = None

            elif event.type == pygame.MOUSEMOTION:
                if not paintbrush_color:
                    if selected_node:
                        G, node = selected_node
                        for g_pos, g in zip(pos_list, graphs):
                            if g == G:
                                g_pos[node] = event.pos
                    elif graph_dragging and graph_being_dragged is not None:
                        dx = event.pos[0] - initial_graph_position[0]
                        dy = event.pos[1] - initial_graph_position[1]
                        pos = pos_list[graph_being_dragged]
                        for node in pos:
                            pos[node] = (pos[node][0] + dx, pos[node][1] + dy)
                        initial_graph_position = event.pos

        screen.fill((255, 255, 255))
        if show_grid:
            draw_grid(screen, WIDTH, HEIGHT, 50, 50)

        if right_tab_visible:
            pygame.draw.rect(screen, GRAY, (WIDTH, 0, RIGHT_TAB_WIDTH, HEIGHT))
            for label, state_getter, position in button_positions:
                draw_button(screen, label, state_getter(), position)
            for i, (x, y) in enumerate(palette_positions):
                pygame.draw.rect(screen, palette_colors[i], (x, y, 20, 20))
            pygame.draw.rect(screen, (200, 200, 200), (*mouse_icon_position, 40, 40))
            pygame.draw.polygon(screen, (0, 0, 0), [
                (mouse_icon_position[0] + 10, mouse_icon_position[1] + 5),
                (mouse_icon_position[0] + 30, mouse_icon_position[1] + 15),
                (mouse_icon_position[0] + 15, mouse_icon_position[1] + 30)
            ])
            pygame.draw.rect(screen, (150, 150, 150), (WIDTH - 20, HEIGHT // 2 - 20, 20, 40))
            tab_text = pygame.font.SysFont('Arial', 14).render(">", True, (0, 0, 0))
            screen.blit(tab_text, (WIDTH - 10 - tab_text.get_width() // 2, HEIGHT // 2 - 10 - tab_text.get_height() // 2))
        else:
            pygame.draw.rect(screen, (150, 150, 150), (WIDTH + RIGHT_TAB_WIDTH - 20, HEIGHT // 2 - 20, 20, 40))
            tab_text = pygame.font.SysFont('Arial', 14).render("<", True, (0, 0, 0))
            screen.blit(tab_text, (WIDTH + RIGHT_TAB_WIDTH - 10 - tab_text.get_width() // 2, HEIGHT // 2 - 10 - tab_text.get_height() // 2))

        for G, pos in zip(graphs, pos_list):
            draw_graph(
                mod, screen, G, pos, edge_length_func, edge_sublabel_func, vertex_sublabel_func,
                show_vertex_labels, show_edge_labels, show_vertex_sublabels, show_edge_sublabels,
                vertex_scale=1.0, custom_colors=colored_elements
            )

        if paintbrush_color:
            pygame.draw.circle(screen, paintbrush_color, pygame.mouse.get_pos(), 5)

        pygame.display.flip()

    pygame.quit()







# Example usage
if __name__ == "__main__":
    #Define a custom edge length function
    def custom_edge_length(node1, node2):
        if isinstance(node1, str) or isinstance(node2, str):
            return ":)"
        return abs(node1 - node2)

    #Define a custom edge sublabel function
    def custom_edge_sublabel(node1, node2):
        if isinstance(node1, str) or isinstance(node2, str):
            return None
        return (node1 + node2) % 5

    #Define a custom vertex sublabel function
    def custom_vertex_sublabel(node):
        if isinstance(node, str):
            return None
        return node % 7
    
    #using standard Networkx methods for example. Graphs are induced by edges here.
    G1 = nx.Graph()
    G1.add_edges_from([(0, 1), (1, "node"), (2, 3)]) # each pair is an edge
    
    G2 = nx.Graph()
    G2.add_edges_from([("A", "beta"), ("B", "C"), ("C", "D")]) #
    
    #Pass custom functions or leave as None for default behavior
        #opt. means optional and #req means required

    viz(
        [G1, G2], #must pass a list, [G1] or [G1,G2] ... 
        mod=7, #opt.
        edge_length_func=custom_edge_length, #opt.
        edge_sublabel_func=custom_edge_sublabel, #opt.
        vertex_sublabel_func=custom_vertex_sublabel, #opt.
        save_info=['graph test', 'C:\\Users\\baneg\\OneDrive\\Desktop\\Git\\research\\pygtikz test files'] #opt.
    )

