#! groovy

def workerNode = "devel10"

pipeline {
	agent { label workerNode }
	environment {
		ARTIFACTORY_LOGIN = credentials("artifactory_login")
		DOCKER_TAG = "${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
		GITLAB_PRIVATE_TOKEN = credentials("ai-gitlab-api-token")
	}
    triggers {
	    upstream(upstreamProjects: 'Docker-base-python3,Docker-base-python3-bump-trigger', threshold: hudson.model.Result.SUCCESS)
        pollSCM("H/06 * * * *")
    }
    stages {
		stage("test") {
			agent {
				docker {
					label workerNode
					image "docker.dbc.dk/build-env"
					alwaysPull true
				}
			}
			steps {
				sh """#!/usr/bin/env bash
					set -xe
					rm -rf env
					python3 -m venv env
					source env/bin/activate
					pip install -U pip wheel pytest-cov
					pip install .
					make-build-info
				"""
				stash includes: "src/series_poc/_build_info.py,docs", name: "build-stash"
			}
		}
		stage("upload wheel package") {
			agent {
				docker {
					label workerNode
					image "docker.dbc.dk/build-env"
					alwaysPull true
				}
			}
			when {
				branch "master"
			}
			steps {
				unstash "build-stash"
				sh """#!/usr/bin/env bash
					set -xe
					rm -rf dist
					make-build-info
					python3 setup.py egg_info --tag-build=${env.BUILD_NUMBER} bdist_wheel
					twine upload -u $ARTIFACTORY_LOGIN_USR -p $ARTIFACTORY_LOGIN_PSW --repository-url https://artifactory.dbc.dk/artifactory/api/pypi/pypi-dbc dist/*
				"""
			}
		}
	stage('build'){
	    steps {
				unstash "build-stash"
		script {
		    def tag = 'dbc-series-poc'
		    app = docker.build("$tag:${DOCKER_TAG}", "--pull --no-cache --build-arg BRANCH_NAME=${BRANCH_NAME} .")
		}
	    }
	}
	stage('push') {
	    steps {
		script {
		    docker.withRegistry('https://docker.dbc.dk', 'docker') {
			app.push()
			app.push('latest')
		            }
		        }
	        }
        }
	// stage("update staging version number for staging") {
	// 	agent {
	// 		docker {
	// 			label workerNode
	// 			image "docker.dbc.dk/build-env"
	// 			alwaysPull true
	// 		}
	// 	}
	// 	when {
	// 		branch "master"
	// 	}
	// 	steps {
	// 		dir("deploy") {
	// 			sh "set-new-version series-poc-1-0.yml ${env.GITLAB_PRIVATE_TOKEN} ai/series-poc-secrets ${env.DOCKER_TAG} -b staging"
	// 		}
	// 		build job: "ai/series-poc-deploy/staging", wait: true
	// 	}
	// }
	// 	stage("validate staging") {
	// 		agent {
	// 			docker {
	// 				label workerNode
	// 				image "docker.dbc.dk/build-env"
	// 				alwaysPull true
	// 			}
	// 		}
	// 		when {
	// 			branch "master"
	// 		}
	// 		steps {
	// 			sh "webservice_validation.py http://series-poc-1-0.mi-staging.svc.cloud.dbc.dk deploy/validation.yml"
	// 		}
	// 	}
	// stage("update staging version number for prod") {
	// 	agent {
	// 		docker {
	// 			label workerNode
	// 			image "docker.dbc.dk/build-env"
	// 			alwaysPull true
	// 		}
	// 	}
	// 	when {
	// 		branch "master"
	// 	}
	// 	steps {
	// 		dir("deploy") {
	// 			sh "set-new-version series-poc-1-0.yml ${env.GITLAB_PRIVATE_TOKEN} ai/series-poc-secrets ${env.DOCKER_TAG} -b prod"
	// 		}
	// 		build job: "ai/series-poc-deploy/prod", wait: true
	// 	}
	// }
	// 	stage("validate prod") {
	// 		agent {
	// 			docker {
	// 				label workerNode
	// 				image "docker.dbc.dk/build-env"
	// 				alwaysPull true
	// 			}
	// 		}
	// 		when {
	// 			branch "master"
	// 		}
	// 		steps {
	// 			sh "webservice_validation.py http://series-poc-1-0.mi-prod.svc.cloud.dbc.dk deploy/validation.yml"
	// 		}
	// 	}
    }
}
