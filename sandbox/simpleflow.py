from pathlib import Path

import prefect
from prefect.run_configs import DockerRun
from prefect.storage import Docker, Local

from datafetch.s3.flows import post_processing


@prefect.task
def local_processing(fp: str):
    print(f"Do some post-processing on {fp} ... ")


with prefect.Flow(name="simpleflow") as flow:
    local_processing("/tmp/plop")
    post_processing("/tmp/plip")



def configure_docker():
    # Using Docker
    fp = Path(__file__)
    flow.storage = Docker(
        python_dependencies=["git+https://github.com/steph-ben/datafetch.git"],
        stored_as_script=True,
        path=f"/flow/{ fp.name }",
        files={fp.absolute(): f"/flow/{ fp.name }"},
        build_kwargs={'nocache': False}
    )
    flow.run_config = DockerRun()


def configure_local():
    # Using Local
    flow.storage = Local(stored_as_script=True, path="/home/steph/Code/steph-ben/fetch-with-prefect/config/laptop/simpleflow.py")
    #flow.run_config = DockerRun(image="stephben/fetch-with-prefect")


if __name__ == "__main__":
    configure_docker()
    flow.register(project_name="laptop-gfs-project", labels=["steph-laptop"])


