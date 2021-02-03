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
    'timesteps': [0, 1, 2, 3, 4, 5, 6],
    'max_concurrent_download': 5,
    'download_dir': "/tmp/laptop/s3/gfs",
    'post_flowrun': StartFlowRun(flow_name="gfs-post-processing", project_name=prefect_project_name)
}

# Create a prefect's flow object with some configuration
flow_nwp_00 = create_flow_download(run=00, **settings)
flow_nwp_12 = create_flow_download(run=12, **settings)

flow_list = [flow_nwp_00]


def main(cmd):
    # This part of the flow configuration is only needed when registering the flow

    # Configure how this code will be passed to the prefect agents
    # In this case, a docker image containing current file and associated libraries
    # will be created
    fp = Path(__file__)
    for flow in flow_list:
        # flow.storage = Docker(
        #     stored_as_script=True,
        #     files={fp.absolute(): f"/flow/{fp.name}"},  # Copy current file to container
        #     path=f"/flow/{fp.name}",  # Use this file for running the flow
        #     python_dependencies=["git+https://github.com/steph-ben/datafetch"],
        #     build_kwargs={'nocache': True}
        # )
        flow.storage = GitHub(
                repo="stephben/datafetch-config",  # name of repo
                path="laptop/s3_gfs_flow.py",  # location of flow file in repo
                secrets=["2451054577d8ff030a2267853876b3a7e9ef0b42"]  # name of personal access token secret
        )

    # This flow will run only in docker
    for flow in flow_list:
        flow.run_config = DockerRun(
            image="stephben/datafetch"
        )

    if cmd in ("register", "trigger"):
        # Ensure the flow is well registered in prefect server
        for flow in flow_list:
            r = flow.register(project_name=prefect_project_name, labels=["docker"])
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
