import sys
import re

file_path = r'd:\College\Semester 8\TA\Software-Testing-Web-App\frontend-dev\src\components\custom\AddModuleForm.tsx'
content = open(file_path, 'r', encoding='utf-8').read()

# Filter out strings and comments to get a true brace count
def remove_comments_and_strings(text):
    text = re.sub(r'//.*', '', text)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    text = re.sub(r'".*?"', '""', text)
    text = re.sub(r"'.*?'", "''", text)
    text = re.sub(r'`.*?`', '``', text, flags=re.DOTALL)
    return text

clean_content = remove_comments_and_strings(content)

print(f"Braces {{: {clean_content.count('{')}, }}: {clean_content.count('}')}")
print(f"Parens (: {clean_content.count('(')}, ): {clean_content.count(')')}")
print(f"Angles <: {clean_content.count('<')}, >: {clean_content.count('>')}")

stack = []
for i, char in enumerate(clean_content):
    if char in '{[(':
        stack.append((char, i))
    elif char in '}])':
        if not stack:
            print(f"Unmatched {char} at index {i}")
        else:
            last_char, last_i = stack.pop()
            if (char == '}' and last_char != '{') or \
               (char == ']' and last_char != '[') or \
               (char == ')' and last_char != '('):
                print(f"Mismatched {char} at index {i}, expected match for {last_char} at index {last_i}")

if stack:
    print(f"Unclosed brackets: {stack}")
