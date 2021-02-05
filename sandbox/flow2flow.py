import prefect

################################
from prefect.tasks.prefect import StartFlowRun

@prefect.task
def process(fp):
    print(f"Processing file {fp} ...")


with prefect.Flow("process") as flow_process:
    fp = prefect.Parameter("fp")
    process(fp)

################################
@prefect.task
def check_file(fp):
    print(f"Checking file {fp} ...")
    return fp


@prefect.task
def download_file(fp):
    print(f"Downloading file {fp} ...")
    return {'fp': fp}

#################################
@prefect.task
def process(fp):
    print(f"Processing file {fp} ...")


with prefect.Flow("process") as flow_process:
    fp = prefect.Parameter("fp")
    process(fp)


flow_run = StartFlowRun(flow_name="process", project_name="sandbox")


with prefect.Flow("download") as flow_download:
    fp = "plip"
    check = check_file(fp)
    download = download_file(check)
    run = flow_run(run_name=f"process_{fp}", parameters={'fp': download}, idempotency_key=fp)
    run.set_upstream(download)

    fp = "plop"
    check = check_file(fp)
    download = download_file(check)
    run = flow_run(run_name=f"process_{fp}", parameters={'fp': download}, idempotency_key=fp)
    run.set_upstream(download)



def main(cmd):
    if cmd in ("register", "trigger"):
        # Ensure the flow is well registered in prefect server
        for flow in flow_download, flow_process:
            r = flow.register(project_name="sandbox", labels=["steph-laptop"])
            print(r)

    if cmd in ("run",):
        flow_download.run()


if __name__ == "__main__":
    import sys
    cmd = "register"
    if len(sys.argv) > 1:
        cmd = sys.argv[1]

    main(cmd)
