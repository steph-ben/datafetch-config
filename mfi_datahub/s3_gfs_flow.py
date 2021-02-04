"""
GFS flow for downloading on MFI datahub
"""
import sys

from prefect.run_configs import DockerRun
from prefect.storage import GitHub, Docker

from datafetch.s3.flows import create_flow_download
from datafetch.utils import trigger_prefect_flow


prefect_project_name = "gfs"

settings = {
    'flow_name': "fetch-gfs",
    'timesteps': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 18, 21, 24],
    'max_concurrent_download': 5,
    'download_dir': "/data/hub/in/NOAA_GFS_FULL"
}

# Create a prefect's flow object with some configuration
flow_nwp_00 = create_flow_download(run=00, **settings)
flow_nwp_12 = create_flow_download(run=12, **settings)

flow_list = flow_nwp_00, flow_nwp_12
for flow in flow_list:
    # Configure how this code will be passed to the prefect agents
    # In this case, prefect will get this file from github
    flow.storage = GitHub(
        repo="steph-ben/datafetch-config",  # name of repo
        ref="laptop",
        path="mfi_datahub/s3_gfs_flow.py",  # location of flow file in repo
        secrets=["GITHUB_ACCESS_TOKEN"]  # name of personal access token secret
    )

    # Configure how this code will be executed
    # In this case, prefect will run this inside a docker container
    flow.run_config = DockerRun(
        image="stephben/datafetch"
    )


def main(cmd):
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
