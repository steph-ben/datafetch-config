from pathlib import Path

import prefect
from prefect.storage import Docker


@prefect.task
def processing1(fp: str):
    print(f"Doing some processing1 on {fp} ...")


@prefect.task
def processing2(fp: str):
    print(f"Doing some processing2 on {fp} ...")


with prefect.Flow("gfs-post-processing") as flow:
    fp = prefect.Parameter("fp")

    output = processing1(fp)
    processing2(output)


if __name__ == "__main__":
    fp = Path(__file__)
    flow.storage = Docker(
        stored_as_script=True,
        files={fp.absolute(): f"/flow/{fp.name}"},  # Copy current file to container
        path=f"/flow/{fp.name}",  # Use this file for running the flow
        build_kwargs={'nocache': False}
    )
    r = flow.register(project_name="laptop-gfs-project", labels=["docker"])
