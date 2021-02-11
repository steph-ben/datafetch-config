import os

import prefect
from prefect.engine.results import PrefectResult
from prefect.run_configs import DockerRun
from prefect.storage import GitHub
from prefect.tasks.shell import ShellTask
from prefect.tasks.templates import StringFormatter

task = ShellTask(log_stdout=True, log_stderr=True)
formatter = StringFormatter()

with prefect.Flow(
        name="subset_for_ww3",
        result=PrefectResult(),
        run_config=DockerRun(image="dockhub.mfi.local:5000/stephben/grib-subset:latest")
        ) as flow:
    fp = prefect.Parameter("fp", default="plop")
    command = formatter(template="fetch_s-atl_wind10m.sh {fp}", fp=fp)
    subset = task(command=command)

repo_ref = os.getenv("DATAFETCH__STORAGE__REPO__REF", default="master")
print(f"Registering Using GitHub repo ref {repo_ref}")
flow.storage = GitHub(
    repo="steph-ben/datafetch-config",
    ref=repo_ref,
    path="projects/gfs/subset_for_ww3.py",
    secrets=["GITHUB_ACCESS_TOKEN"]
)


if __name__ == "__main__":
    from datafetch.utils import show_prefect_cli_helper
    show_prefect_cli_helper(flow_list=[flow])
