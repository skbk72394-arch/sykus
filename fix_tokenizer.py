import sys
with open('tokenizer.py', 'r') as f:
    content = f.read()

content = content.replace('[" ", "\t", "\n", "\r"]', '[" ", "\\t", "\\n", "\\r"]')
content = content.replace('== "\\n"', '== "\\n"')
content = content.replace('!= "\\n"', '!= "\\n"')

# Just rewrite the skip methods explicitly if they have actual newlines:
with open('tokenizer.py', 'w') as f:
    f.write(content)
