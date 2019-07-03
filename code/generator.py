#! /usr/bin/env python

import os
import glob
import argparse
import subprocess
import shutil
import yaml
from jinja2 import Template
from nbconvert import TemplateExporter, HTMLExporter


def make_snakefile(notebook_templates_dir, snake_template, snakefile, notebooks_outdir):
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


def make_yaml_config(outdir, config_template):
    """ Create the YAML config used by papermill

    :param outdir: Path to the output directory of the workflow.
    """

    config_file = os.path.join(outdir, "config.yaml")

    with open(config_template) as f:
        template = Template(f.read())

    with open(config_file, "w") as out:
        out.write(template.render(OUTDIR=outdir))

    return os.path.abspath(config_file)


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
        type=directory_path_type,
    )
    parser.add_argument(
        "-s",
        "--snakefile_template",
        help="Path to the snakefile jinja template file",
        default=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "templates", "basic_snakefile"
        ),
    )
    parser.add_argument(
        "-y",
        "--yaml_config_template",
        help="Path to the YAML config file template",
        default=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "templates", "config.yaml"
        ),
    )
    parser.add_argument(
        "-e",
        "--conda_env_dir",
        help="Path to the directory with all the conda environment yaml files",
        type=directory_path_type,
    )

    return parser.parse_args()


def directory_path_type(string):

    # In case the argument is a proper directory, return the absolute path
    if os.path.isdir(string):
        return os.path.abspath(string)
    else:
        raise NotADirectoryError(string)


def main():

    args = parse_arguments()

    # Create ouput directory
    os.makedirs(args.outdir)

    if args.conda_env_dir:
        # Copy conda environment files
        env_dir = os.path.join(args.outdir, "envs")
        os.makedirs(env_dir)
        for env_yaml_file in glob.glob(os.path.join(args.conda_env_dir, "*.yml")):
            shutil.copy(env_yaml_file, env_dir)

    config_file = make_yaml_config(args.outdir, args.yaml_config_template)

    with open(config_file, "r") as yml:
        config = yaml.safe_load(yml)

    make_snakefile(
        args.notebook_templates_dir,
        args.snakefile_template,
        os.path.join(args.outdir, "Snakefile"),
        config["EXECUTED_NOTEBOOKS_DIR"],
    )

    os.chdir(args.outdir)
    subprocess.run(["snakemake", "--use-conda", "--use-singularity"])

    for notebook in glob.glob(
        os.path.join(config["EXECUTED_NOTEBOOKS_DIR"], "*.ipynb")
    ):
        export_notebook_to_html(notebook)


if __name__ == "__main__":
    main()
