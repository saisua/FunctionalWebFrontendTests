import pydot
import copy


def join_sm_graphs(
	g1: pydot.Dot,
	g2: pydot.Dot,
	source_node: str,
	target_node: str = None,
	g1_label: str = None,
	g2_label: str = None,
) -> pydot.Dot:
	g = copy.deepcopy(g1)

	g_nodes = {n.get_name().strip('"') for n in g.get_nodes()}
	if source_node not in g_nodes:
		raise ValueError(f"Source node '{source_node}' not found in g1")

	if g1_label is None:
		g1_label = g1.get_label()

	for edge in g.get_edges():
		edge.set_label(f"{g1_label}_{edge.get_label()}")

	for node in g2.get_nodes():
		node.set_fillcolor("white")

		g.add_node(node)

	if target_node is None:
		g2_edges = g2.get_edges()
		if not g2_edges:
			raise ValueError("g2 has no edges to determine default target_node")

		g2_first_edge = g2_edges[0]

		target_node = g2_first_edge.get_destination().strip('"')

	if g2_label is None:
		g2_label = g2.get_label()

	for edge in g2.get_edges():
		edge.set_label(f"{g2_label}_{edge.get_label()}")

		g.add_edge(edge)

	for subgraph in g2.get_subgraphs():
		g.add_subgraph(subgraph)

	g.add_edge(pydot.Edge(source_node, target_node))

	g.set_label("Joined Graph")

	return g
