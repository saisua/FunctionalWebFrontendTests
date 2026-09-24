from typing import List, Any
from math import ceil, sqrt


def simple_grid(page, items: List[Any] | int | None = None, **kwargs):
	# TODO: CSS and test

	if items is None:
		n_items = 1
	elif isinstance(items, int):
		n_items = items
	else:
		n_items = len(items)

	columns = kwargs.get('columns', ceil(sqrt(n_items)))
	rows = kwargs.get('rows', ceil(n_items / columns))
	class_name = kwargs.get('class_name', 'grid')
	row_class = kwargs.get('row_class', 'grid-row')
	column_class = kwargs.get('column_class', 'grid-column')

	with page.tag("div", klass=class_name) as grid:
		for row_idx in range(rows):
			with page.tag("div", klass=row_class) as row:
				setattr(grid, f"row_{row_idx}", row)
				for column_idx in range(columns):
					column = page.tag("div", klass=column_class)
					setattr(row, f"column_{column_idx}", column)
					setattr(grid, f"item_{column_idx}_{row_idx}", column)

	return grid
