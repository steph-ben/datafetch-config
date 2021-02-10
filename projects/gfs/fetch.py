"""
GFS flow for downloading on MFI datahub
"""
import os
import logging

from prefect.engine.results import PrefectResult
from prefect.run_configs import DockerRun
from prefect.storage import GitHub
from prefect.tasks.prefect import StartFlowRun

from datafetch.s3.flows import create_flow_download
from datafetch.utils import show_prefect_cli_helper

logger = logging.getLogger(__name__)


prefect_project_name = "gfs"

settings = {
    'flow_name': "fetch-gfs",
    'timesteps': list(range(0, 12)) + list(range(12, 96, 3)),
    'max_concurrent_download': 5,
    'download_dir': "/data/hub/in/NOAA_GFS_FULL",
    'post_flowrun': StartFlowRun(
        flow_name="gfs-post-processing",
        project_name=prefect_project_name
    )
}

# Create a prefect's flow object with some configuration
flow_nwp_00 = create_flow_download(run=00, **settings)
flow_nwp_12 = create_flow_download(run=12, **settings)

flow_list = [flow_nwp_00, flow_nwp_12]
for flow in flow_list:
    # Configure how this code will be passed to the prefect agents
    # In this case, prefect will get this file from github
    repo_ref = os.getenv("DATAFETCH__STORAGE__REPO__REF", default="master")
    print(f"Registering Using GitHub repo ref {repo_ref}")
    flow.storage = GitHub(
        repo="steph-ben/datafetch-config",  # name of repo
        ref=repo_ref,
        path="projects/gfs/fetch.py",  # location of flow file in repo
        secrets=["GITHUB_ACCESS_TOKEN"]  # name of personal access token secret
    )

    # Configure how this code will be executed
    # In this case, prefect will run this inside a docker container
    flow.run_config = DockerRun(
        image="stephben/datafetch"
    )

    # Configure where tasks status will be stored
    # See :
    #   - https://docs.prefect.io/core/concepts/results.html
    #   - https://docs.prefect.io/core/advanced_tutorials/using-results.html
    flow.result = PrefectResult()


if __name__ == "__main__":
    show_prefect_cli_helper(flow_list=flow_list)
