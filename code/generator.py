#! /usr/bin/env python

import os
import glob
import argparse
import subprocess
from jinja2 import Template
from nbconvert import TemplateExporter, HTMLExporter


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


def generate_config(outdir, config_template):
    """ Create the YAML config used by papermill

    :param outdir: Path to the output directory of the workflow.
    """

    with open(config_template) as f:
        template = Template(f.read())

    with open(os.path.join(outdir, "config.yaml"), "w") as out:
        out.write(template.render(OUTDIR=outdir))


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


def parse_arguments():
    parser = argparse.ArgumentParser(description="Jupyter notebooks based workflow")

    parser.add_argument(
        "-o", "--outdir", required=True, help="Path to output directory"
    )
    parser.add_argument(
        "-t",
        "--notebook_templates_dir",
        help="Path to directory with jupyter notebooks to use as templates",
        default=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "notebook_templates"
        ),
    )
    parser.add_argument(
        "-s",
        "--snakefile_template",
        help="Path to the snakefile jinja template file",
        default=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "templates", "basic_snakefile"
        ),
    )

    return parser.parse_args()


def main():

    args = parse_arguments()

    notebooks_outdir = "executed_notebooks"

    os.makedirs(args.outdir)

    generate_config(args.outdir, "templates/config.yaml")

    generate_snakefile(
        args.notebook_templates_dir,
        args.snakefile_template,
        os.path.join(args.outdir, "Snakefile"),
        "executed_notebooks",
    )
    os.chdir(args.outdir)
    subprocess.run("snakemake")

    for notebook in glob.glob(os.path.join(notebooks_outdir, "*.ipynb")):
        export_notebook_to_html(notebook)


if __name__ == "__main__":
    main()
