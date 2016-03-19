from invoke import run, task


@task
def clean():
    run("rm -rf *.pyc")


@task
def pep8():
    run("autopep8 --in-place --max-line-length 10000 --aggressive --aggressive *.py")
