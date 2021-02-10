from pathlib import Path

import prefect
from prefect.engine.results import PrefectResult
from prefect.run_configs import DockerRun
from prefect.storage import GitHub, Docker


@prefect.task
def processing1(fp: str):
    logger = prefect.context.get("logger")
    logger.info(f"Doing some processing1 on {fp} ...")


@prefect.task
def processing2(fp: str):
    logger = prefect.context.get("logger")
    logger.info(f"Doing some processing2 on {fp} ...")


with prefect.Flow("gfs-post-processing", result=PrefectResult()) as flow:
    fp = prefect.Parameter("fp")

    p1 = processing1(fp)
    p2 = processing2(fp)
    p2.set_upstream(p1)


if __name__ == "__main__":
    fp = Path(__file__)
    flow.storage = GitHub(
        repo="steph-ben/datafetch-config",
        ref="master",
        path="mfi_datahub/processing.py",
        secrets=["GITHUB_ACCESS_TOKEN"]
    )
    flow.run_config = DockerRun()
    # flow.storage = Docker(
    #     stored_as_script=True,
    #     files={fp.absolute(): f"/flow/{fp.name}"},  # Copy current file to container
    #     path=f"/flow/{fp.name}",  # Use this file for running the flow
    #     build_kwargs={'nocache': False}
    # )
    r = flow.register(project_name="gfs", labels=["docker"])
