import re

file_path = r'd:\College\Semester 8\TA\Software-Testing-Web-App\frontend-dev\src\components\custom\AddModuleForm.tsx'
content = open(file_path, 'r', encoding='utf-8').read()

# Find all opening, closing and self closing tags
# Regex to match <Tag>, </Tag>, <Tag />
tags = re.finditer(r'<(/)?([a-zA-Z0-9_]+)([^>]*)>', content)

stack = []
for match in tags:
    is_closing = match.group(1) == '/'
    tag_name = match.group(2)
    attrs = match.group(3)
    is_self_closing = attrs.strip().endswith('/')
    
    if tag_name.lower() in ['input', 'img', 'br', 'hr', 'path', 'circle', 'line', 'textarea']:
        continue
    if is_self_closing:
        continue
        
    if not is_closing:
        stack.append((tag_name, match.start()))
    else:
        if not stack:
            print(f"Unmatched closing tag </{tag_name}> at index {match.start()}")
        else:
            last_tag, pos = stack.pop()
            if last_tag != tag_name:
                print(f"Mismatched tag: expected </{last_tag}> but got </{tag_name}> at index {match.start()}. Opened at {pos}")

if stack:
    print(f"Unclosed tags remaining: {stack}")
