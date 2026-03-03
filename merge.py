#!/usr/bin/env python
# -*- coding: utf-8 -*-

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

with open('sections.html', 'r', encoding='utf-8') as f:
    sections = f.read()

insert_pos = content.find('  <main>')
if insert_pos != -1:
    new_content = content[:insert_pos] + sections + '\n\n' + content[insert_pos:]
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Sections inserted successfully!")
else:
    print("Could not find <main> tag")
