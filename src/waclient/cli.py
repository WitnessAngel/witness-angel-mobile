#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
os.environ["KIVY_NO_ARGS"] = "1"

import click

from waclient.waclient_app import WitnessAngelClientApp


@click.command()
@click.option(
    '-l', '--language', help='Default language of the App', default='en',
    type=click.Choice(['en', 'es', 'de', 'fr'])
)
def main(language):
    """Run WitnessAngelClientApp with the given language setting.
    """
    WitnessAngelClientApp(language).run()


if __name__ == "__main__":
    main()
