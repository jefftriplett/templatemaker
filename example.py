#!/usr/bin/env python3

from templatemaker import Template

# Create a template
t = Template()
t.learn("<b>this and that</b>")
t.learn("<b>alex and sue</b>")

# Display the template
print(f"Template: {t.as_text('!')}")

# Extract data
data = t.extract("<b>larry and curly</b>")
print(f"Extracted: {data}")
