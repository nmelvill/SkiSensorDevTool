import click

@click.group()
@click.pass_context
def main(ctx: click.Context) -> None:
    click.echo(message="Hello")


#main.add_command(cmd=cli_commands.blconnect)