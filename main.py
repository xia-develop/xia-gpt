import os
import yaml
import logging
from xia_gpt.models import GptGroup, GptActor


def create_ou(ou_name: str, parent_name: str, sub_org: dict, visibility: str):
    ou = GptGroup.load(name=ou_name)
    if not ou:
        GptGroup(name=ou_name, parent_name=parent_name, visibility=visibility).save()
        logging.info(f"Organization Unit {ou_name} under {parent_name} created.")
        for sub_ou in sub_org:
            create_ou(sub_ou, ou_name, sub_org[sub_ou], visibility)


def sync_company_config():
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


def sync_actors():
    with open('config/actors.yaml', 'r') as fp:
        actors_profile = yaml.safe_load(fp)
    for actor_profile in actors_profile:
        actor = GptActor.load(name=actor_profile["name"])
        if not actor:
            GptActor.from_display(**actor_profile).save()


if __name__ == '__main__':
    assert os.environ.get("GITLAB_TOKEN")
    # sync_company_config()
    # sync_actors()