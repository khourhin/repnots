import os
from jinja2 import Template
import subprocess


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


def main():

    outdir = "outdir"
    os.makedirs(outdir)
    generate_config(outdir, "templates/config.yaml")
    generate_snakefile(
        os.path.abspath("notebook_templates"),
        "templates/basic_snakefile",
        os.path.join(outdir, "Snakefile"),
        "executed_notebooks",
    )
    os.chdir(outdir)
    subprocess.run("snakemake")


main()
