"""Background task scheduler, shared by future features that need periodic
or delayed jobs (e.g. reminders, alarms).

Empty of jobs until the first feature registers one — this module only
provides the scheduler instance; its start/stop is wired into the FastAPI
app's lifespan in app/main.py.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
