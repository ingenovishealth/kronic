from flask import Flask, request, render_template

from kron import getCronJobs, getNamespaces, getJobs, getCronJob, getPods, getPodLogs, toggleCronJob

app = Flask(__name__,
            static_url_path='',
            static_folder='static')

@app.route("/")
def index():
    cronjobs = getCronJobs()
    namespaces = {}
    for cronjob in cronjobs:
        namespaces[cronjob["namespace"]] = namespaces.get(cronjob["namespace"], 0) + 1

    return render_template("index.html", namespaces=namespaces)

@app.route("/namespaces/<name>")
def namespaces(name):
    cronjob_names = getCronJobs(name)
    cronjobs = [getCronJob(namespace=name, cronjob_name=cronjob["name"]) for cronjob in cronjob_names]
    for cron in cronjobs:
        jobs = getJobs(namespace=name, cronjob_name=cron["metadata"]["name"])
        cron["jobs"] = jobs
        for job in cron["jobs"]:
            job["pods"] = getPods(cron["metadata"]["namespace"], job["metadata"]["name"])

    return render_template("namespaceJobs.html", cronjobs=cronjobs, namespace=name)

@app.route("/api/")
def allCronJobs():
    jobs = getCronJobs()
    return jobs

@app.route("/api/namespaces/")
def apiNamespaces():
    namespaces = getNamespaces()
    return namespaces

@app.route("/api/namespaces/<name>/cronjobs")
@app.route("/api/namespaces/<name>")
def namespace(name):
    jobs = getCronJobs(name)
    return jobs

@app.route("/api/namespaces/<namespace>/cronjobs/<cronjob_name>")
def showCronJob(namespace, cronjob_name):
    cronjob = getCronJob(namespace, cronjob_name)
    return cronjob

@app.route("/api/namespaces/<namespace>/cronjobs/<cronjob_name>/suspend", methods = ['GET', 'POST'])
def getSetSuspended(namespace, cronjob_name):
    if request.method == 'GET':
        """Return the suspended status of the <cronjob_name>"""
        cronjob = getCronJob(namespace, cronjob_name)
        return cronjob
    if request.method == 'POST':
        """Toggle the suspended status of <cronjob_name>"""
        cronjob = toggleCronJob(namespace, cronjob_name)
        return cronjob


@app.route('/api/namespaces/<namespace>/jobs', defaults={'cronjob_name': None})
@app.route('/api/namespaces/<namespace>/jobs/<cronjob_name>')
def showJobs(namespace, cronjob_name):
    jobs = getJobs(namespace, cronjob_name)
    return jobs

@app.route('/api/namespaces/<namespace>/pods')
def showPods(namespace):
    pods = getPods(namespace)
    return pods

@app.route('/api/namespaces/<namespace>/pods/<pod_name>/logs')
def showPodLogs(namespace, pod_name):
    logs = getPodLogs(namespace, pod_name)
    return logs
