import argparse
import yaml
import logging
import asyncio
from xia_composer import Template
from xia_actor import JobTemplate, Actor
from xia_pattern import PatternTemplate
from xia_gpt.prepare import create_ou, init_actors, init_jobs, init_company_config
from xia_gpt.models import XiaActor
from xia_gpt.patterns import GptPythonPattern


class GptPrompts(JobTemplate, PatternTemplate):
    """Register ./templates"""


def team_loading():
    with open('config/actors.yaml', 'r') as fp:
        actors_profile = yaml.safe_load(fp)
    team_members = []
    for actor_profile in actors_profile["actors"]:
        actor = XiaActor.load(name=actor_profile["name"])
        if actor:
            team_members.append(actor)
    return team_members


async def team_working(team_members: list):
    with open('config/actors.yaml', 'r') as fp:
        actors_profile = yaml.safe_load(fp)
    team_members = []
    for actor_profile in actors_profile["actors"]:
        actor = XiaActor.load(name=actor_profile["name"])
        if actor:
            team_members.append(actor)
    task_list = []
    for actor in team_members:
        task_list.append(asyncio.create_task(actor.live()))
    for task in task_list:
        await task


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description='Processing job configurations')
    parser.add_argument('-n', '--round', type=int, default=1, help='Round of range')
    parser.add_argument('--skip-sync-company', action='store_true', help='Synchronize Company Structure')
    parser.add_argument('--recreate-actors', action='store_true', help='Skip all initialization')
    parser.add_argument('--recreate-projects', action='store_true', help='Recreate Projects')
    parser.add_argument('--work-only', action='store_true', help='Recreate Projects')
    args = parser.parse_args()

    if not args.work_only:
        if not args.skip_sync_company:
            init_company_config()
        init_actors(recreate=args.recreate_actors)
        init_jobs(recreate_target=args.recreate_projects)
    team_member = team_loading()
    for _ in range(args.round):
        asyncio.run(team_working(team_member))
