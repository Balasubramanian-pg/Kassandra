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
