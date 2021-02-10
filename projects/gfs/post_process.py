import os

import prefect
from prefect.engine.results import PrefectResult
from prefect.run_configs import DockerRun
from prefect.storage import GitHub


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


repo_ref = os.getenv("DATAFETCH__STORAGE__REPO__REF", default="master")
print(f"Registering Using GitHub repo ref {repo_ref}")
flow.storage = GitHub(
    repo="steph-ben/datafetch-config",
    ref=repo_ref,
    path="projects/gfs/post_process.py",
    secrets=["GITHUB_ACCESS_TOKEN"]
)
flow.run_config = DockerRun()


if __name__ == "__main__":
    from datafetch.utils import show_prefect_cli_helper
    show_prefect_cli_helper(flow_list=[flow])
