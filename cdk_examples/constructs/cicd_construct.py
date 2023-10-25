from aws_cdk import (
    aws_codecommit as codecommit,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_events as events,
    aws_iam as iam,
    aws_events_targets as targets,

    Stack
)
from constructs import Construct


class CodePipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, project_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a CodeCommit repository
        code_repo = codecommit.Repository(
            self,
            f"{project_name}Repo",
            repository_name=project_name
        )

        # Create a CodeBuild project for installing requirements and running cdk deploy
        build_project = codebuild.PipelineProject(
            self,
            f"{project_name}Project",
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "commands": ["pip install -r requirements.txt", "npm install -g aws-cdk"]
                    },
                    "build": {
                        "commands": ["cdk deploy"]
                    }
                }
            }),
        )

        # Define a CodePipeline
        pipeline = codepipeline.Pipeline(
            self,
            f"{project_name}Pipeline",
        )

        # Add stages to the CodePipeline
        source_output = codepipeline.Artifact()
        source_action = codepipeline_actions.CodeCommitSourceAction(
            action_name="Source",
            repository=code_repo,
            output=source_output,
            branch="main",
        )

        pipeline.add_stage(
            stage_name="Source",
            actions=[source_action],
        )

        build_output = codepipeline.Artifact()
        build_action = codepipeline_actions.CodeBuildAction(
            action_name="Build",
            project=build_project,
            input=source_output,
            outputs=[build_output],
        )

        pipeline.add_stage(
            stage_name="Build",
            actions=[build_action],
        )

        # Create an IAM role for assuming in the "deployToProd" stage
        assume_role = iam.Role(
            self,
            "CrossAccountDeploymentRole",
            assumed_by=iam.AccountPrincipal("652380775390"),
        )

        # Add a new "deployToProd" stage with the assumed role
        deploy_action = codepipeline_actions.CodeBuildAction(
            action_name="DeployToProd",
            project=build_project,
            input=source_output,
            # outputs=[build_output],
            role=assume_role,
        )

        pipeline.add_stage(
            stage_name="DeployToProd",
            actions=[deploy_action],
        )

        codecommit_rule = events.Rule(
            self,
            "CodeCommitRule",
            event_pattern={
                "source": ["aws.codecommit"],
                "detail": {
                    "event": ["referenceCreated"],
                    "referenceName": ["refs/heads/main"]
                },
            },
        )

        codecommit_rule.add_target(
            targets.CodePipeline(pipeline),
        )