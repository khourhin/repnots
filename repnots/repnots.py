# -*- coding: utf-8 -*-

"""Main module."""

import os
import glob
import shutil

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


def copy_conda_envs(conda_env_dir, outdir):
    """ Copy the conda environment yaml file to the output directory
    """
    env_dir = os.path.join(outdir, "envs")
    os.makedirs(env_dir)
    for env_yaml_file in glob.glob(os.path.join(conda_env_dir, "*.yml")):
        shutil.copy(env_yaml_file, env_dir)
