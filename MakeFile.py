# -*- coding: utf-8 -*-
"""A pythonic like make file """

import click
import subprocess
import glob


@click.command()
@click.option("--test", is_flag=True, help="test if the environement is nicely set up")
@click.option("--coverage", is_flag=True, help="Generate coverage")
@click.option("--apk", is_flag=True, help="Build an android apk with buildozer")
@click.option("--deploy", is_flag=True, help="Deploy the app to your android device")
@click.option("--po", is_flag=True, help="Create i18n message files")
@click.option("--mo", is_flag=True, help="Create i18n message locales")
def cli(test, coverage, apk, deploy, po, mo):
    if test:
        subprocess.run("pytest", shell=True, check=True)

    if coverage:
        subprocess.run("coverage run -m pytest", shell=True, check=True)
        subprocess.run("coverage html", shell=True, check=True)
        subprocess.run("xdg-open htmlcov/index.html", shell=True, check=True)

    if po:
        po_files = glob.glob("po/*.po")
        subprocess.run(
            "xgettext -Lpython --output=messages.pot src/waclient/*.py src/waclient/*/*.py src/waclient/*.kv",
            shell=True,
            check=True,
        )

        for i in po_files:
            command = "msgmerge --update --no-fuzzy-matching --backup=off "
            command = command + i + " messages.pot"
            subprocess.run(command, shell=True, check=True)

    if mo:
        po_files = glob.glob("po/*.po")
        for i in po_files:
            command1 = "mkdir -p data/locales/" + i[3:-3] + "/LC_MESSAGES"
            command2 = "msgfmt -c -o data/locales/" + i[3:-3]
            command2 = command2 + "/LC_MESSAGES/witness-angel-client.mo " + i
            subprocess.run(command1, shell=True, check=True)
            subprocess.run(command2, shell=True, check=True)

    if apk:
        subprocess.run("buildozer -v android debug", shell=True, check=True)

    if deploy:
        subprocess.run("buildozer android deploy logcat", shell=True, check=True)


if __name__ == "__main__":
    cli()


# @click.option('--po',help='Generate po files')
# @click.option('--mo',help='Generate mo files')
