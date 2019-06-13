import os
import glob
import subprocess
from jinja2 import Template
from nbconvert import TemplateExporter, HTMLExporter

OUTDIR = "outdir"
NOTEBOOK_TEMPLATES = os.path.abspath("notebook_templates")
NOTEBOOKS_OUTDIR = "executed_notebooks"
SNAKEFILE_TEMPLATE = "templates/basic_snakefile"
SNAKEFILE_RENDERED = os.path.join(OUTDIR, "Snakefile")


def generate_snakefile(
    notebook_templates_dir, snake_template, snakefile, notebooks_outdir
):
    """ Generate a snakefile to execute a series of jupyter notebooks using papermill

    :param notebook_templates_dir: a directory where to find the jupyter notebook templates 
    :param snake_template: the name of the file to use as snakefile template.
    """

    notebooks = os.listdir(notebook_templates_dir)

    with open(snake_template) as f:
        template = Template(f.read())

    with open(snakefile, "w") as out:
        out.write(
            template.render(
                notebooks=notebooks,
                notebooks_outdir=notebooks_outdir,
                notebook_templates_dir=notebook_templates_dir,
            )
        )


def generate_config(output_dir, config_template):
    """ Create the YAML config used by papermill

    :param output_dir: Path to the output directory of the workflow.
    """

    with open(config_template) as f:
        template = Template(f.read())

    with open(os.path.join(output_dir, "config.yaml"), "w") as out:
        out.write(template.render(OUTDIR=output_dir))


def export_notebook_to_html(notebook):
    # Config for simple output
    TemplateExporter.exclude_input_prompt = True
    TemplateExporter.exclude_output_prompt = True
    TemplateExporter.exclude_input = True

    exporter = HTMLExporter(template_file="full.tpl")

    # Make html report
    output, resources = exporter.from_filename(notebook)
    with open(f"{os.path.splitext(notebook)[0]}.html", "w") as f:
        f.write(output)


def main():

    os.makedirs(OUTDIR)
    generate_config(OUTDIR, "templates/config.yaml")
    generate_snakefile(
        NOTEBOOK_TEMPLATES, SNAKEFILE_TEMPLATE, SNAKEFILE_RENDERED, NOTEBOOKS_OUTDIR
    )
    os.chdir(OUTDIR)
    subprocess.run("snakemake")

    for notebook in glob.glob(os.path.join(NOTEBOOKS_OUTDIR, "*.ipynb")):
        export_notebook_to_html(notebook)


main()
