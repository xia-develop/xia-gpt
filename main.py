import os
import yaml
import logging
import asyncio
from xia_composer import Template
from xia_gpt.models import GptGroup, GptActor, GptTarget, GptKnowledge, GptCampaign


class GptPrompts(Template):
    """"""


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


def init_actors():
    with open('config/actors.yaml', 'r') as fp:
        actors_profile = yaml.safe_load(fp)
    for actor_profile in actors_profile:
        actor = GptActor.load(name=actor_profile["name"])
        if not actor:
            GptActor.from_display(**actor_profile).save()


def init_jobs():
    with open('config/jobs.yaml', 'r') as fp:
        jobs_profile = yaml.safe_load(fp)
    if not jobs_profile:
        return  # Empty file, nothing to do
    for job_profile in jobs_profile:
        target = GptTarget.load(name=job_profile["project_name"])
        if not target:
            group = GptGroup.load(name=job_profile["organization_unit"])
            if not group:
                raise ValueError(f"Organization Unit {job_profile['organization_unit']} doesn't exist")
            GptTarget(name=job_profile["project_name"], group_name=job_profile["organization_unit"],
                      visibility=group.visibility).save()

        # Case 1: It is a campaign
        if "campaign_type" in job_profile:
            campaign = GptCampaign.load(target=job_profile["project_name"], name=job_profile["job_name"])
            if not campaign:
                GptCampaign(target=job_profile["project_name"], name=job_profile["job_name"],
                            owner=job_profile["owner_name"], campaign_type=job_profile["campaign_type"],
                            description=job_profile["job_name"]).save()
            owner = GptActor.load(name=job_profile["owner_name"])
            if not owner:
                raise ValueError(f"Actor {job_profile['owner_name']} is not found")
            owner.add_job(target=job_profile["project_name"], object_name=job_profile["job_name"],
                          role="campaign_owner")
        # Save the context to the mission
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
    for actor_profile in actors_profile:
        actor = GptActor.load(name=actor_profile["name"])
        if actor:
            team_members.append(actor)
    task_list = []
    for actor in team_members:
        task_list.append(asyncio.create_task(actor.live()))
    for task in task_list:
        await task


if __name__ == '__main__':
    assert os.environ.get("GITLAB_TOKEN")
    init_company_config()
    init_actors()
    init_jobs()
    for _ in range(15):
        asyncio.run(team_working())
        pass
