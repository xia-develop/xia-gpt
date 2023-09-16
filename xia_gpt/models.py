from xia_composer import Group, Target, Campaign, Mission, Dialog, Review, Turn, KnowledgeNode, Validation
from xia_engine_gitlab import GitlabMilestoneEngine, GitlabMilestoneIssueEngine
from xia_engine_gitlab import GitlabProjectEngine, GitlabCodeEngine, GitlabSnippetEngine
from xia_engine_gitlab import GitlabIssueDiscussionEngine, GitlabIssueDiscussionNoteEngine
from xia_engine_gitlab import GitlabGroupEngine, GitlabMrDiscussionEngine, GitlabMergeRequestEngine
from xia_actor_openai import OpenaiActor


GitlabProjectEngine.field_mapping = {"blue_labels": "mission_status"}


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


class GptActor(OpenaiActor):
    _engine = GitlabSnippetEngine
    _address = {
        "gitlab_snippet": {
            "api_host": "gitlab.com",
            "api_token": b"GITLAB_TOKEN"
        }
    }
