"""
GFS flow for test running on my laptop
"""
import os
import sys
from pathlib import Path

from prefect.run_configs import DockerRun
from prefect.tasks.prefect import StartFlowRun
from prefect.storage import GitHub, Docker

from datafetch.s3.flows import create_flow_download
from datafetch.utils import trigger_prefect_flow


prefect_project_name = "laptop-gfs-project"

settings = {
    'flow_name': "fetch-gfs",
    'timesteps': [0, 1],
    'max_concurrent_download': 5,
    'download_dir': "/tmp/laptop/s3/gfs",
    'post_flowrun': StartFlowRun(flow_name="gfs-post-processing", project_name=prefect_project_name)
}

# Create a prefect's flow object with some configuration
flow_nwp_12 = create_flow_download(run=12, **settings)
flow_nwp_00 = create_flow_download(run=00, **settings)

flow_list = [flow_nwp_00, flow_nwp_12]
use_github = False
if use_github:
    for f in flow_list:
        # Configure how this code will be passed to the prefect agents
        # In this case, prefect will get this file from github
        f.storage = GitHub(
            repo="steph-ben/datafetch-config",  # name of repo
            ref="laptop",
            # FIXME : add flow_name argument to prefect code
            path="laptop/s3_gfs_flow.py",  # location of flow file in repo
            secrets=["GITHUB_ACCESS_TOKEN"]  # name of personal access token secret
        )

        # Configure how this code will be executed
        # In this case, prefect will run this inside a docker container
        f.run_config = DockerRun(
            image="stephben/datafetch"
        )


def main(cmd):
    if cmd in ("register", "trigger"):
        # Ensure the flow is well registered in prefect server
        for f in flow_list:
            labels = []
            if use_github:
                labels = ["docker"]
            r = f.register(
                project_name=prefect_project_name,
                labels=labels
            )
            print(r)

    if cmd == "trigger":
        # Trigger the flow manually
        for flow in flow_list:
            trigger_prefect_flow(
                flow_name=flow.name,
                run_name=f"{flow.name}-manually_triggered",
            )

    if cmd == "run":
        # Run a download from current process
        flow_nwp_00.schedule = None
        flow_nwp_00.run()


if __name__ == "__main__":
    cmd = "register"
    if len(sys.argv) > 1:
        cmd = sys.argv[1]

    main(cmd)
