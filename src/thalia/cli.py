"""
Copyright (C) 2025 Narendra S

This file is a part of the Thalia project

Thalia is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Thalia is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Thalia.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import sqlite3

import click
from click_default_group import DefaultGroup
from platformdirs import user_cache_path, user_config_path
from rich import print

from . import config as conf

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(
    cls=DefaultGroup,
    default="tui",
    default_if_no_args=True,
    invoke_without_command=True,
    context_settings=CONTEXT_SETTINGS,
)
@click.version_option(
    "0.0.1",
    "--version",
    "-v",
)
@click.option(
    "-c",
    "--config",
    help=f"Path to the configuration file (defaults to {user_config_path('thalia') / 'config.toml'})",
)
@click.option("--cache-dir", help="Path to the cache directory to use")
@click.pass_context
def cli(ctx, config, cache_dir):
    """Thalia CLI"""
    ctx.ensure_object(dict)

    if config is not None:
        # If a config file is mentioned set the config file environment variable to override the default config
        os.environ["THALIA_CONFIG_FILE"] = str(config)
    ctx.obj["settings"] = conf.Settings()
    ctx.obj["config_path"] = config or user_config_path("thalia") / "config.toml"

    if cache_dir is None:
        cache_dir = ctx.obj["cache_dir"] = user_cache_path("thalia")

    if not cache_dir.exists():
        cache_dir.mkdir(parents=True)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def tui(ctx):
    # Load the app class and run it with the given settings
    from .tui import app

    db_path = ctx.obj["cache_dir"] / "cache.db"
    try:
        db = sqlite3.connect(db_path, timeout=3)
    except sqlite3.OperationalError:
        print("[red]Unable to open cache database. Exiting.[/red]")
        exit(1)

    thalia = ctx.obj["app"] = app.Thalia(ctx.obj["settings"], db, ctx.obj["cache_dir"])
    thalia.run()


@click.pass_context
def get_settings(ctx) -> conf.Settings:
    """Get the settings object from the context."""
    return ctx.obj["settings"]
