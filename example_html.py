#!/usr/bin/env python3

from templatemaker import HTMLTemplate

# Simple HTML example
html1 = "<p>Name: John, Age: 30</p>"
html2 = "<p>Name: Jane, Age: 25</p>"
html3 = "<p>Name: Bob, Age: 42</p>"

# Create HTML template
t = HTMLTemplate()
t.learn(html1)
t.learn(html2)
t.learn(html3)

# Display the template
print("===== HTML Template =====")
print(t.as_text("{{ HOLE }}"))

# Extract data from a new HTML
html3 = "<p>Name: Oliver, Age: 7</p>"

data = t.extract(html3)
print("\n===== Extracted Data =====")
for i, value in enumerate(data):
    print(f"Hole {i}: {value}")

# Use dictionary extraction
print("\n===== Dictionary Extraction =====")
fields = ("name", "age")
data_dict = t.extract_dict(html3, fields)
print(data_dict)
