##pip install pyyaml graphviz
## sudo apt update && sudo apt install graphviz
## sudo apt update && sudo apt install xdg-utils

import yaml                # YAML parser to load pipeline configuration
from graphviz import Digraph  # Graphviz for DAG visualization

# 🧠 Load YAML config from a file and return as Python dict
def load_pipeline_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

# 🎯 Build a directed graph (DAG) from pipeline definition
def build_dag_graph(pipeline):
    # Extract pipeline metadata from root level
    dot = Digraph(comment=pipeline["pipeline"]["name"])  # Set DAG title
    dot.attr(rankdir="LR", size="8,5")  # Set layout to left-to-right

    stages = pipeline["pipeline"].get("stages", [])  # Get all pipeline stages
    step_registry = {}  # Used to map step names to their full paths for dependency resolution

    for stage in stages:
        stage_name = stage["name"]

        # 🔷 Add stage node
        dot.node(stage_name, shape="box", style="filled", fillcolor="lightblue")

        # ➡️ Add dependencies between stages
        for dep in stage.get("depends_on", []):
            dot.edge(dep, stage_name)

        # 🔸 Handle groups inside the stage (if any)
        groups = stage.get("groups", [])
        for group in groups:
            group_name = f"{stage_name}.{group['name']}"  # Unique group ID
            dot.node(group_name, shape="box", style="filled", fillcolor="lightyellow")  # Group node
            dot.edge(stage_name, group_name)  # Link stage → group

            # ➡️ Add group dependencies (e.g., wait for other groups)
            for group_dep in group.get("depends_on", []):
                dot.edge(f"{stage_name}.{group_dep}", group_name)

            # ⚪ Add each step in the group
            for step in group.get("steps", []):
                step_name = f"{stage_name}.{step['name']}"
                step_registry[step['name']] = step_name  # Register step for dependency lookups

                # Add the step node
                dot.node(step_name, shape="ellipse", style="filled", fillcolor="white")

                # Link group → step
                dot.edge(group_name, step_name)

                # ➡️ Add step-level dependencies
                for step_dep in step.get("depends_on", []):
                    dep_full = step_registry.get(step_dep)
                    if dep_full:
                        dot.edge(dep_full, step_name)  # internal step
                    else:
                        dot.edge(step_dep, step_name)  # external step (possibly cross-stage)

        # 🔄 Handle stages without groups (direct steps under the stage)
        for step in stage.get("steps", []):
            step_name = f"{stage_name}.{step['name']}"
            step_registry[step['name']] = step_name

            # Add the step node
            dot.node(step_name, shape="ellipse", style="filled", fillcolor="white")

            # Link stage → step directly
            dot.edge(stage_name, step_name)

            # ➡️ Add step dependencies
            for step_dep in step.get("depends_on", []):
                dep_full = step_registry.get(step_dep)
                if dep_full:
                    dot.edge(dep_full, step_name)
                else:
                    dot.edge(step_dep, step_name)

    return dot  # Return the final graph object

# 🚀 Script entry point
if __name__ == "__main__":
    import sys
    import os

    yaml_file = "./pipelines/flows/new_version.yaml"  # 📄 Path to your pipeline YAML
    output_file = "./pipelines/flows/diagrams/etl_pipeline_dag"  # 🖼 Output file name (no extension)

    pipeline = load_pipeline_yaml(yaml_file)       # Load the YAML pipeline config
    dag_graph = build_dag_graph(pipeline)          # Build the DAG graph

    # 📤 Render DAG to PDF and PNG formats
    dag_graph.render(output_file, format="pdf", view=True)   # Opens PDF if system supports it
    dag_graph.render(output_file, format="png", view=False)  # Renders PNG silently

    print(f"✅ DAG generated: {output_file}.pdf and {output_file}.png")  # 🎉 Success!

