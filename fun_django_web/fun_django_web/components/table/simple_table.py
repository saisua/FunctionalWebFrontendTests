def simple_table(
    page,
    rows: int,
    columns: int,
    *,
    headers: bool = True,
    **kwargs
):
    # Configuración de clases CSS
    table_class = kwargs.get('table_class', 'table')
    header_class = kwargs.get('header_class', 'table-header')
    row_class = kwargs.get('row_class', 'table-row')
    cell_class = kwargs.get('cell_class', 'table-cell')
    striped = kwargs.get('striped', False)
    style = kwargs.get('style')

    table_kwargs = dict(
        klass=table_class,
    )

    if style:
        table_kwargs['style'] = style

    # Construir la tabla vacía primero
    with page.tag("table", **table_kwargs) as table:
        # Encabezados
        if headers:
            with page.tag("thead"):
                with page.tag("tr", klass=row_class) as header_row:
                    for col_idx in range(columns):
                        page.tag(
                            "th",
                            f"Col {col_idx + 1}",
                            klass=f"{header_class} {cell_class}",
                        )
                        setattr(header_row, f"header_{col_idx}", None)
                        setattr(table, f"header_{col_idx}", None)

        # Cuerpo de la tabla con estructura definida
        with page.tag("tbody") as tbody:
            for row_idx in range(rows):
                row_class_name = row_class
                if striped and row_idx % 2 == 1:
                    row_class_name = f"{row_class} alt"

                with page.tag("tr", klass=row_class_name) as row:
                    setattr(tbody, f"row_{row_idx}", row)

                    # Crear celdas vacías primero
                    for col_idx in range(columns):
                        cell = page.tag("td", "", klass=cell_class)
                        setattr(row, f"cell_{col_idx}", cell)
                        setattr(table, f"cell_{col_idx}_{row_idx}", cell)

    return table
