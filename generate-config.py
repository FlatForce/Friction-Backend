#!/usr/bin/env python3

import os
from yaml import dump


function_list = [ f.name for f in os.scandir("functions") if f.is_dir() ]

def write_pipelines():
    config = base_config()
    # print(config)
    
    config["jobs"].update((add_plan("test")))
    # print(config)
    for function in function_list:
        config["jobs"].update((add_plan(function)))
        config["jobs"].update((add_apply(function)))
        config["workflows"].update((add_workflow(function)))
        
    # config = collections.OrderedDict(config))
    print(dump(config))

def add_plan(name):
    return {
        f"plan-{name}": {
            "machine": {
                "image": "ubuntu-2204:2022.04.2"
            },
            "steps": [
                "aws-cli/install",
                "checkout",
                {
                    "aws-oidc-setup": {
                        "aws-role-arn": "arn:aws:iam::908315850849:role/friction-pipeline-role"
                    }
                },
                "terraform/install",
                {
                    "run": {
                        "name": "Plan",
                        "command": f"cd functions/{name}/arch\nterraform init -input=false\nterraform plan -input=false -out=tfplan\nls\n"
                    }
                },
                {
                    "persist_to_workspace": {
                        "root": ".",
                        "paths": [
                            "."
                        ]
                    }
                }
            ]
        },
    }
    
def add_apply(name):    
    return {
        f"apply-{name}": {
            "machine": {
                "image": "ubuntu-2204:2022.04.2"
            },
            "steps": [
                {
                    "attach_workspace": {
                        "at": "."
                    }
                },
                "aws-cli/install",
                {
                    "aws-oidc-setup": {
                        "aws-role-arn": "arn:aws:iam::908315850849:role/friction-pipeline-role"
                    }
                },
                "terraform/install",
                {
                    "run": {
                        "name": "Apply",
                        "command": f"cd functions/{name}/arch\nterraform apply -auto-approve tfplan\n"
                    }
                },
                {
                    "persist_to_workspace": {
                        "root": ".",
                        "paths": [
                            "."
                        ]
                    }
                }
            ]
        }
    }
    
def add_workflow(name):
    return {
        f"{name}": {
            "jobs": [
                {
                    f"plan-{name}": {
                        "context": "FlatForce Context"
                    }
                },
                {
                    f"apply-{name}": {
                        "context": "FlatForce Context",
                        "requires": [
                            f"plan-{name}"
                        ]
                    }
                }
            ]   
        }
    }
    
def base_config():
    return {
        "version": 2.1,
        "setup": "true",
        "orbs": {
            "aws-cli": "circleci/aws-cli@3.0.0",
            "terraform": "circleci/terraform@3.1.0"
        },
        "jobs": {},
        "commands": {
            "aws-oidc-setup": {
                "description": "Setup AWS auth using OIDC token",
                "parameters": {
                    "aws-role-arn": {
                        "type": "string"
                    }
                },
                "steps": [
                    {
                        "run": {
                            "name": "Get short-term credentials",
                            "command": "STS=($(aws sts assume-role-with-web-identity --role-arn << parameters.aws-role-arn >> --role-session-name \"${CIRCLE_BRANCH}-${CIRCLE_BUILD_NUM}\" --web-identity-token \"${CIRCLE_OIDC_TOKEN}\" --duration-seconds 900 --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' --output text))\necho \"export AWS_ACCESS_KEY_ID=${STS[0]}\" >> $BASH_ENV\necho \"export AWS_SECRET_ACCESS_KEY=${STS[1]}\" >> $BASH_ENV\necho \"export AWS_SESSION_TOKEN=${STS[2]}\" >> $BASH_ENV\n"
                        }
                    },
                    {
                        "run": {
                            "name": "Verify AWS credentials",
                            "command": "aws sts get-caller-identity"
                        }
                    }
                ]
            }
        },
        "workflows": {}
    }
    
if __name__ == '__main__':
    write_pipelines()