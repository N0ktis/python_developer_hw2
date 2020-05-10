import click
from patient import Patient, PatientCollection, DEFAULT_PARAMS, Patient_DB


@click.group()
def cli():
    pass


@click.command()
@click.argument('first_name', type=str)
@click.argument('last_name', type=str)
@click.option('--birth-date', '-b', default=None, type=str)
@click.option('--phone', '-p', default=None, type=str)
@click.option('--document-type', '-t', nargs=2, default=str)
@click.option('--document-number', '-n', nargs=3, default=str)
def create(first_name, last_name, birth_date, phone, document_type, document_number):
    if None in (first_name, last_name, birth_date, phone, document_type, document_number):
        raise Exception
    Patient.create(first_name, last_name, birth_date, phone, ' '.join(document_type), ' '.join(document_number)).save()
    click.echo('Patient added')


@click.command()
@click.argument('limit_val', default=10, type=int)
def show(limit_val):
    if limit_val >= 0:
        p = PatientCollection(*DEFAULT_PARAMS).limit(limit_val)
        for i in p:
            click.echo(i)


@click.command()
def count():
    click.echo(PatientCollection(*DEFAULT_PARAMS).session.query(Patient_DB).count())


cli.add_command(create)
cli.add_command(show)
cli.add_command(count)

if __name__ == '__main__':
    cli()
