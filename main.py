import argparse
import yaml
import logging
import asyncio
from xia_composer import Template
from xia_actor import JobTemplate, Actor
from xia_pattern import PatternTemplate
from xia_gpt.models import GptGroup, GptTarget, GptKnowledge, GptCampaign, GptMission, GptJob, XiaActor
from xia_gpt.patterns import GptPythonPattern


class GptPrompts(JobTemplate, PatternTemplate):
    """Register ./templates"""


def create_ou(ou_name: str, parent_name: str, sub_org: dict, visibility: str):
    ou = GptGroup.load(name=ou_name)
    if not ou:
        GptGroup(name=ou_name, parent_name=parent_name, visibility=visibility).save()
        logging.info(f"Organization Unit {ou_name} under {parent_name} created.")
    for sub_ou in sub_org:
        create_ou(sub_ou, ou_name, sub_org[sub_ou], visibility)


def init_company_config():
    """Create company organization units if not exists

    """
    with open('config/company.yaml', 'r') as fp:
        company_config = yaml.safe_load(fp)
    company = GptGroup.load(name=company_config["name"])
    if not company:
        raise ValueError(f"Please create the top-level group {company_config['name']} in gitlab.com as your company."
                         f"You could also change the company name by modifying 'config/company.yaml' file")
    for ou_name in company_config["organization"]:
        create_ou(ou_name, company_config["name"], company_config["organization"][ou_name],
                  company_config["visibility"])


def init_actors(recreate: bool = False):
    with open('config/actors.yaml', 'r') as fp:
        actors_profile = yaml.safe_load(fp)
    # Create team project if not exists
    team = GptTarget.load(name=actors_profile["team_name"])
    if team and recreate:
        team.delete()
    if not team or recreate:
        GptTarget(name=actors_profile["team_name"], group_name="").save()
    # Create actors if not exists
    for actor_profile in actors_profile["actors"]:
        actor = XiaActor.load(name=actor_profile["name"])
        if not actor:
            new_actor = XiaActor.from_display(**actor_profile)
            new_actor.save()


def init_jobs(recreate_target: bool = False):
    with open('config/jobs.yaml', 'r') as fp:
        jobs_profile = yaml.safe_load(fp)
    if not jobs_profile:
        return  # Empty file, nothing to do
    for job_profile in jobs_profile:
        target = GptTarget.load(name=job_profile["project_name"])
        if target and recreate_target:
            target.delete()
        if not target or recreate_target:
            group = GptGroup.load(name=job_profile["organization_unit"])
            if not group:
                raise ValueError(f"Organization Unit {job_profile['organization_unit']} doesn't exist")
            GptTarget(name=job_profile["project_name"], group_name=job_profile["organization_unit"],
                      visibility=group.visibility).save()

        # Case 1: It is a campaign
        if "campaign_type" in job_profile:
            campaign = GptCampaign.load(target=job_profile["project_name"], name=job_profile["job_name"])
            if not campaign:  # Case 1.1: New Campaign
                GptCampaign(target=job_profile["project_name"], name=job_profile["job_name"],
                            owner=job_profile["owner_name"], campaign_type=job_profile["campaign_type"],
                            campaign_contexts=job_profile.get("campaign_contexts", []),
                            runtime_variables=job_profile.get("runtime_variables", {}),
                            description=job_profile["job_name"]).save()
                owner = XiaActor.load(name=job_profile["owner_name"])
                if not owner:
                    raise ValueError(f"Actor {job_profile['owner_name']} is not found")
                owner.add_job(target=job_profile["project_name"], object_name=job_profile["job_name"],
                              role="campaign_owner")
            else:  # Case 1.2: Try replay all current missions
                for mission in GptMission.objects(target=job_profile["project_name"], campaign=campaign.name,
                                                  status="opened"):
                    campaign.step_status = [step for step in campaign.step_status if step.mission_name != mission.name]
                    for job in GptJob.objects(target=job_profile["project_name"], object_name=mission.name):
                        job.delete()
                    mission.delete()
                campaign.save()

        # Case 2: It is a mission
        elif "mission_type" in job_profile:
            mission = GptMission.load(target=job_profile["project_name"], name=job_profile["job_name"])
            if mission:
                for job in GptJob.objects(target=job_profile["project_name"], object_name=job_profile["job_name"]):
                    job.delete()
                mission.delete()
            GptMission(target=job_profile["project_name"], name=job_profile["job_name"],
                       owner=job_profile["owner_name"], mission_type=job_profile["mission_type"],
                       skip_validation=job_profile.get("skip_validation", False),
                       max_task_per_round=job_profile.get("max_task_per_round", None),
                       runtime_variables=job_profile.get("runtime_variables", {}),
                       template_contexts=job_profile.get("template_contexts", [])).save()
            owner = XiaActor.load(name=job_profile["owner_name"])
            if not owner:
                raise ValueError(f"Actor {job_profile['owner_name']} is not found")
            owner.add_job(target=job_profile["project_name"], object_name=job_profile["job_name"],
                          role="mission_owner")

        # Review Settings
        for review_type, reviewers in job_profile.get("reviewers", {}).items():
            for reviewer_name in reviewers:
                reviewer = XiaActor.load(name=reviewer_name)
                if not reviewer:
                    raise ValueError(f"Actor {reviewer} is not found")
                reviewer.add_job(target=job_profile["project_name"], object_name=review_type,
                                 role="target_reviewer")

        # Initial Contents
        for context_key, context_data in job_profile.get("input_contexts", {}).items():
            knowledge_node = GptKnowledge.load(target=job_profile["project_name"], key=context_key,
                                               version=job_profile["job_name"])
            if not knowledge_node:
                GptKnowledge(target=job_profile["project_name"], key=context_key, version=job_profile["job_name"],
                             value=context_data).save()


async def team_working():
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
    for _ in range(args.round):
        asyncio.run(team_working())
        pass
