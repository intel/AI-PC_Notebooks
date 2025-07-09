def extract_elements(node, source_code):
    elements = []
    if node.type == 'function_definition':
        elements.append({
            'type': 'function_definition',
            'text': source_code[node.start_byte:node.end_byte].decode('utf8')
        })
    for child in node.children:
        elements.extend(extract_elements(child, source_code))
    return elements


def write_code_comments_to_file(file_path: str, original_code: str, modified_code: str):
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
        start_pos = file_content.find(original_code)
        
        if start_pos != -1:
            end_pos = start_pos + len(original_code)
            indentation = file_content[:start_pos].split("\n")[-1]
            
            modeified_lines = modified_code.split("\n")
            first_line = modeified_lines.pop(0)
            
            indented_modified_lines = [indentation + line for line in modeified_lines]
            indented_modified_code = (first_line + "\n" + "\n".join(indented_modified_lines))
            
            modified_content = (file_content[:start_pos] + indented_modified_code + file_content[end_pos:])
            
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(modified_content)