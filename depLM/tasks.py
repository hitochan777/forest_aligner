from invoke import run, task

@task
def test():
    run("python tests/TestNgramLM.py")

@task
def clean():
    run("rm *.pyc *_pb2.py")

@task
def proto():
    run("protoc -I=. --python_out=. depLM.proto")
