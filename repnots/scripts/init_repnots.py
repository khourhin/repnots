#! /usr/bin/env python

import os
import glob
import argparse
import subprocess
import yaml

import repnots.repnots as rn


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
    os.makedirs(args.outdir, exist_ok=True)

    if args.conda_env_dir:
        rn.copy_conda_envs(args.conda_env_dir, args.outdir)

    config_file = rn.make_yaml_config(args.outdir, args.yaml_config_template)

    with open(config_file, "r") as yml:
        config = yaml.safe_load(yml)

    rn.make_snakefile(
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
        rn.export_notebook_to_html(notebook)


if __name__ == "__main__":
    main()
