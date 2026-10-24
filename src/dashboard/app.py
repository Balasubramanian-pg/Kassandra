import os
import glob
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import yaml
from src.vault.parser import parse_markdown_file

app = FastAPI(title="Antigravity Job Engine Dashboard")

VAULT_PATH = "vault"

def get_all_jobs():
    jobs = []
    # Find all .md files in vault/01 - Jobs recursively
    pattern = os.path.join(VAULT_PATH, "01 - Jobs", "**", "*.md")
    for filepath in glob.glob(pattern, recursive=True):
        fm, body = parse_markdown_file(filepath)
        if fm and fm.get("type") == "job":
            fm["filepath"] = filepath
            fm["filename"] = os.path.basename(filepath)
            jobs.append(fm)
    return jobs

def get_funnel_stats(jobs):
    stats = {
        "discovered": 0,
        "qualified": 0,
        "shortlisted": 0,
        "cv_generated": 0,
        "ready_to_apply": 0,
        "applied": 0,
        "rejected": 0,
    }
    for job in jobs:
        status = job.get("status", "discovered")
        if status in stats:
            stats[status] += 1
        app_status = job.get("application_status", "not_applied")
        if app_status == "applied":
            stats["applied"] += 1
    return stats

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Antigravity Job Application Engine</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-gray-100 font-sans min-h-screen">
    <!-- Navbar -->
    <nav class="border-b border-gray-800 bg-gray-950 p-4">
        <div class="container mx-auto flex justify-between items-center">
            <h1 class="text-xl font-bold tracking-wider text-green-400">🪐 ANTIGRAVITY JOB APPLICATION ENGINE</h1>
            <span class="text-sm text-gray-400">Vault: {{ vault_path }}</span>
        </div>
    </nav>

    <!-- Main Container -->
    <div class="container mx-auto p-6">
        
        <!-- Metrics Funnel -->
        <div class="grid grid-cols-2 md:grid-cols-7 gap-4 mb-8">
            <div class="bg-gray-800 p-4 rounded-lg border border-gray-700 text-center">
                <div class="text-gray-400 text-xs uppercase font-semibold">Discovered</div>
                <div class="text-2xl font-bold mt-1 text-blue-400">{{ stats.discovered }}</div>
            </div>
            <div class="bg-gray-800 p-4 rounded-lg border border-gray-700 text-center">
                <div class="text-gray-400 text-xs uppercase font-semibold">Qualified</div>
                <div class="text-2xl font-bold mt-1 text-purple-400">{{ stats.qualified }}</div>
            </div>
            <div class="bg-gray-800 p-4 rounded-lg border border-gray-700 text-center">
                <div class="text-gray-400 text-xs uppercase font-semibold">Shortlisted</div>
                <div class="text-2xl font-bold mt-1 text-yellow-400">{{ stats.shortlisted }}</div>
            </div>
            <div class="bg-gray-800 p-4 rounded-lg border border-gray-700 text-center">
                <div class="text-gray-400 text-xs uppercase font-semibold">CV Tailored</div>
                <div class="text-2xl font-bold mt-1 text-indigo-400">{{ stats.cv_generated }}</div>
            </div>
            <div class="bg-gray-800 p-4 rounded-lg border border-gray-700 text-center">
                <div class="text-gray-400 text-xs uppercase font-semibold">Ready</div>
                <div class="text-2xl font-bold mt-1 text-green-400">{{ stats.ready_to_apply }}</div>
            </div>
            <div class="bg-gray-800 p-4 rounded-lg border border-gray-700 text-center">
                <div class="text-gray-400 text-xs uppercase font-semibold">Applied</div>
                <div class="text-2xl font-bold mt-1 text-teal-400">{{ stats.applied }}</div>
            </div>
            <div class="bg-gray-800 p-4 rounded-lg border border-gray-700 text-center">
                <div class="text-gray-400 text-xs uppercase font-semibold">Rejected</div>
                <div class="text-2xl font-bold mt-1 text-red-400">{{ stats.rejected }}</div>
            </div>
        </div>

        <!-- Top Jobs Queue -->
        <div class="bg-gray-800 rounded-lg border border-gray-700 p-6">
            <h2 class="text-lg font-bold mb-4 text-green-400 border-b border-gray-700 pb-2">Active Opportunities</h2>
            <div class="overflow-x-auto">
                <table class="w-full text-left text-sm text-gray-300">
                    <thead class="bg-gray-900 text-gray-400 uppercase text-xs">
                        <tr>
                            <th class="p-3">Job ID</th>
                            <th class="p-3">Company</th>
                            <th class="p-3">Title</th>
                            <th class="p-3">Location</th>
                            <th class="p-3">Fit Score</th>
                            <th class="p-3">Status</th>
                            <th class="p-3">Action</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-700">
                        {% for job in jobs %}
                        <tr class="hover:bg-gray-750">
                            <td class="p-3 font-semibold text-gray-100">{{ job.job_id }}</td>
                            <td class="p-3">{{ job.company }}</td>
                            <td class="p-3 font-medium text-green-300">{{ job.title }}</td>
                            <td class="p-3 text-gray-400">{{ job.location|join(', ') }}</td>
                            <td class="p-3">
                                {% if job.fit_score %}
                                <span class="px-2 py-1 rounded text-xs font-bold {% if job.fit_score >= 85 %}bg-green-900 text-green-300{% elif job.fit_score >= 70 %}bg-yellow-900 text-yellow-300{% else %}bg-red-900 text-red-300{% endif %}">
                                    {{ job.fit_score }}%
                                </span>
                                {% else %}
                                <span class="text-gray-500">-</span>
                                {% endif %}
                            </td>
                            <td class="p-3">
                                <span class="px-2 py-1 rounded text-xs bg-gray-700 text-gray-300 uppercase font-semibold">
                                    {{ job.status }}
                                </span>
                            </td>
                            <td class="p-3">
                                <a href="/job/{{ job.job_id }}" class="text-green-400 hover:underline">Details &rarr;</a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

    </div>
</body>
</html>
"""

JOB_DETAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ job.title }} - Details</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-gray-100 font-sans min-h-screen">
    <!-- Navbar -->
    <nav class="border-b border-gray-800 bg-gray-950 p-4">
        <div class="container mx-auto flex justify-between items-center">
            <a href="/" class="text-sm text-green-400 hover:underline">&larr; Back to Dashboard</a>
            <h1 class="text-lg font-bold">{{ job.company }} - {{ job.title }}</h1>
            <span class="text-xs text-gray-400">ID: {{ job.job_id }}</span>
        </div>
    </nav>

    <!-- Content -->
    <div class="container mx-auto p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- Left Pane: Metadata & Status -->
        <div class="space-y-6 lg:col-span-1">
            <div class="bg-gray-800 rounded-lg border border-gray-700 p-6">
                <h3 class="font-bold text-green-400 mb-4 uppercase text-sm border-b border-gray-700 pb-2">Overview</h3>
                <div class="space-y-3 text-sm">
                    <div><span class="text-gray-400">Company:</span> {{ job.company }}</div>
                    <div><span class="text-gray-400">Location:</span> {{ job.location|join(', ') }}</div>
                    <div><span class="text-gray-400">Experience Min/Max:</span> {{ job.experience_min }} - {{ job.experience_max }} Yrs</div>
                    <div><span class="text-gray-400">Remote Type:</span> {{ job.remote_type }}</div>
                    <div><span class="text-gray-400">Domain:</span> {{ job.domain }}</div>
                    <div><span class="text-gray-400">Source:</span> <a href="{{ job.source_url }}" target="_blank" class="text-blue-400 hover:underline">Original Link &nearr;</a></div>
                </div>
            </div>

            <div class="bg-gray-800 rounded-lg border border-gray-700 p-6">
                <h3 class="font-bold text-green-400 mb-4 uppercase text-sm border-b border-gray-700 pb-2">Fit & Application Status</h3>
                <div class="space-y-3 text-sm">
                    <div><span class="text-gray-400">Fit Score:</span> <strong class="text-yellow-300">{{ job.fit_score or 'Not scored' }}%</strong></div>
                    <div><span class="text-gray-400">Job Status:</span> <span class="bg-gray-700 px-2 py-0.5 rounded text-xs">{{ job.status }}</span></div>
                    <div><span class="text-gray-400">Resume Status:</span> <span class="bg-indigo-900 text-indigo-300 px-2 py-0.5 rounded text-xs">{{ job.resume_status }}</span></div>
                    <div><span class="text-gray-400">Application Status:</span> <span class="bg-teal-900 text-teal-300 px-2 py-0.5 rounded text-xs">{{ job.application_status }}</span></div>
                </div>
            </div>
        </div>

        <!-- Right Pane: JD & Analysis Body -->
        <div class="lg:col-span-2 space-y-6">
            <div class="bg-gray-800 rounded-lg border border-gray-700 p-6">
                <h3 class="font-bold text-green-400 mb-4 uppercase text-sm border-b border-gray-700 pb-2">Analysis & JD Content</h3>
                <div class="prose prose-invert max-w-none text-sm text-gray-300 whitespace-pre-wrap">
                    {{ body }}
                </div>
            </div>
        </div>

    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    jobs = get_all_jobs()
    stats = get_funnel_stats(jobs)
    # Import jinja2 render directly
    from jinja2 import Template
    t = Template(HTML_TEMPLATE)
    return t.render(jobs=jobs, stats=stats, vault_path=os.path.abspath(VAULT_PATH))

@app.get("/job/{job_id}", response_class=HTMLResponse)
async def job_detail(job_id: str):
    jobs = get_all_jobs()
    target_job = None
    for j in jobs:
        if j.get("job_id") == job_id:
            target_job = j
            break
            
    if not target_job:
        return HTMLResponse("Job not found", status_code=404)
        
    _, body = parse_markdown_file(target_job["filepath"])
    from jinja2 import Template
    t = Template(JOB_DETAIL_TEMPLATE)
    return t.render(job=target_job, body=body)
