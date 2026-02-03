"""
Gera avatares placeholder em SVG
Execute: python generate_placeholders.py
"""

avatars = {
    "shadow_avatar": {
        "color": "#1a1a2e",
        "bg": "#2d2d44"
    },
    "freud_style": {
        "color": "#4a3728",
        "bg": "#6b5344"
    },
    "skinner_style": {
        "color": "#2d4a5e",
        "bg": "#4a6b7f"
    },
    "perls_style": {
        "color": "#3d5a3d",
        "bg": "#5a7a5a"
    }
}

svg_template = '''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <rect width="512" height="512" fill="{bg}"/>
  <circle cx="256" cy="180" r="100" fill="{color}"/>
  <ellipse cx="256" cy="420" rx="140" ry="120" fill="{color}"/>
  <text x="256" y="500" text-anchor="middle" fill="white" font-size="24">{name}</text>
</svg>'''

for name, colors in avatars.items():
    svg = svg_template.format(
        bg=colors["bg"],
        color=colors["color"],
        name=name.replace("_", " ").title()
    )
    with open(f"{name}.svg", "w") as f:
        f.write(svg)
    print(f"Criado: {name}.svg")

print("\nConverta SVG para PNG usando:")
print("  - Inkscape: inkscape file.svg -o file.png")
print("  - ImageMagick: convert file.svg file.png")
