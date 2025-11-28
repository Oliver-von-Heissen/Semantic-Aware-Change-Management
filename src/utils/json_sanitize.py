def sanitize(elements):
    """Remove empty fields from the input."""
    filtered_elements = []
    
    for element in elements:
        filtered_element = {k: v for k, v in element.items() if v not in [None, "", [], {}, ()]}
        filtered_elements.append(filtered_element)

    return filtered_elements
