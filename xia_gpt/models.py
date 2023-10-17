import yaml
from xia_composer import Group, Target, Campaign, Mission, Dialog, Review, Turn, KnowledgeNode, Validation
from xia_engine_gitlab import GitlabMilestoneEngine, GitlabMilestoneIssueEngine
from xia_engine_gitlab import GitlabProjectEngine, GitlabCodeEngine
from xia_engine_gitlab import GitlabIssueDiscussionEngine, GitlabIssueDiscussionNoteEngine
from xia_engine_gitlab import GitlabGroupEngine, GitlabMrDiscussionEngine, GitlabMergeRequestEngine
from xia_engine_gitlab_project import GitlabProjectMilestoneEngine
from xia_engine_gitlab_project import GitlabProjectIssueNoteEngine, GitlabProjectMilestoneIssueEngine
from xia_actor import JobLog, Job, Actor
from xia_actor.jobs import *
from xia_actor_openai import GptActor, PollinationActor


with open('config/actors.yaml', 'r') as fp:
    actors_profile = yaml.safe_load(fp)


class GptGroup(Group):
    _engine = GitlabGroupEngine
    _address = {
        "gitlab_group": {
            "api_host": "gitlab.com",
            "api_token": b"GITLAB_TOKEN"
        }
    }


class GptTarget(Target):
    _engine = GitlabProjectEngine
    _address = {
        "gitlab_project": {
            "api_host": "gitlab.com",
            "api_token": b"GITLAB_TOKEN"
        }
    }


class GptDialog(Dialog):
    _engine = GitlabIssueDiscussionEngine
    _address = {
        "gitlab_issue_discussion": {
            "api_host": "gitlab.com",
            "api_token": b"GITLAB_TOKEN",
        }
    }


class GptReview(Review):
    _engine = GitlabMrDiscussionEngine
    _address = {
        "gitlab_mr_discussion": {
            "api_host": "gitlab.com",
            "api_token": b"GITLAB_TOKEN",
        }
    }


class GptTurn(Turn):
    _engine = GitlabIssueDiscussionNoteEngine
    _address = {
        "gitlab_issue_discussion_note": {
            "api_host": "gitlab.com",
            "api_token": b"GITLAB_TOKEN"
        }
    }


class GptKnowledge(KnowledgeNode):
    _engine = GitlabCodeEngine
    _search_engine = GitlabCodeEngine
    _address = {
        "gitlab_code": {
            "api_host": "gitlab.com",
            "api_token": b"GITLAB_TOKEN"
        }
    }


class GptValidation(Validation):
    _engine = GitlabMergeRequestEngine
    _address = {
        "gitlab_merge_request": {
            "api_host": "gitlab.com",
            "api_token": b"GITLAB_TOKEN"
        }
    }


class GptMission(Mission):
    _engine = GitlabMilestoneIssueEngine
    _address = {
        "gitlab_milestone_issue": {
            "api_host": "gitlab.com",
            "api_token": b"GITLAB_TOKEN"
        }
    }

    _knowledge_class = GptKnowledge
    _dialog_class = GptDialog
    _turn_class = GptTurn
    _review_class = GptReview
    _validation_class = GptValidation


class GptCampaign(Campaign):
    _engine = GitlabMilestoneEngine
    _address = {
        "gitlab_milestone": {
            "api_host": "gitlab.com",
            "api_token": b"GITLAB_TOKEN"
        }
    }

    _knowledge_class = GptKnowledge
    _mission_class = GptMission
    _validation_class = GptValidation


class GptJobLog(JobLog):
    _engine = GitlabProjectIssueNoteEngine
    _address = {
        "gitlab_project_issue_note": {
            "api_host": "gitlab.com",
            "api_token": b"GITLAB_TOKEN",
            "default_target": actors_profile["team_name"]
        }
    }


class GptJob(Job):
    _type_base = Job
    _job_log_class = GptJobLog

    _engine = GitlabProjectMilestoneIssueEngine
    _address = {
        "gitlab_project_milestone_issue": {
            "api_host": "gitlab.com",
            "api_token": b"GITLAB_TOKEN",
            "default_target": actors_profile["team_name"]
        }
    }


class XiaActor(Actor):
    _type_base = Actor
    _job_class = GptJob

    _engine = GitlabProjectMilestoneEngine
    _address = {
        "gitlab_project_milestone": {
            "api_host": "gitlab.com",
            "api_token": b"GITLAB_TOKEN",
            "default_target": actors_profile["team_name"]
        }
    }
