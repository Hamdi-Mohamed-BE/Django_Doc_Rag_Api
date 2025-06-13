COMPOSE_NAME ?= backend
PROJECT_NAME ?=backend

IMAGE_NAME ?= backend
IMAGE_TAG := $(shell git describe --exact-match --tags 2>/dev/null || git rev-parse --short HEAD)

ECR ?= europe-west2-docker.pkg.dev/${PROJECT_NAME}-cloud
ECR_REPO_API ?= ${PROJECT_NAME}-api/api
ECR_REPO_CELERY ?= ${PROJECT_NAME}-api/celery
ECR_REPO_PUBSUB ?= ${PROJECT_NAME}-api/pubsub

DOCKER_TAG_API = ${ECR}/${ECR_REPO_API}:${IMAGE_TAG}
DOCKER_TAG_CELERY = ${ECR}/${ECR_REPO_CELERY}:${IMAGE_TAG}
DOCKER_TAG_PUBSUB = ${ECR}/${ECR_REPO_PUBSUB}:${IMAGE_TAG}

DOCKER_TAG_API_LTS = ${ECR}/${ECR_REPO_API}:latest
DOCKER_TAG_CELERY_LTS = ${ECR}/${ECR_REPO_CELERY}:latest
DOCKER_TAG_PUBSUB_LTS = ${ECR}/${ECR_REPO_PUBSUB}:latest

COMPOSE_COMMON = COMPOSE_NAME=${COMPOSE_NAME} docker compose -p ${PROJECT_NAME} -f infra/compose-common.yml
COMPOSE_API_PROD = COMPOSE_NAME=${COMPOSE_NAME} docker compose -p ${PROJECT_NAME} -f infra/compose-api.yml


PRODUCTION_TAG_REGEX = ^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$$
IS_PROD_TAG = $(shell [[ $(IMAGE_TAG) =~ $(PRODUCTION_TAG_REGEX) ]] && echo matched)

docker-gc-login:
	cat keys/google-docker-login.json | docker login -u _json_key_base64 --password-stdin https://europe-west2-docker.pkg.dev

show-image-tag:
	@echo ${IMAGE_TAG}

docker-build: show-image-tag
	docker pull ${DOCKER_TAG_API} || true & docker pull ${DOCKER_TAG_CELERY} || true & docker pull ${DOCKER_TAG_CELERY} || true

	docker build -f Dockerfile \
        --cache-from ${DOCKER_TAG_API} \
        --tag ${DOCKER_TAG_API} --quiet . & \

	docker build -f celery.dockerfile \
        --cache-from ${DOCKER_TAG_CELERY} \
        --tag ${DOCKER_TAG_CELERY}  --quiet . & \

	docker build -f Dockerfile.pubsub \
        --cache-from ${DOCKER_TAG_PUBSUB} \
        --tag ${DOCKER_TAG_PUBSUB}  --quiet .

docker-push-manual: docker-gc-login docker-build
	docker push ${DOCKER_TAG_API} & docker push ${DOCKER_TAG_CELERY} & docker push ${DOCKER_TAG_PUBSUB}
ifeq ($(strip $(IS_PROD_TAG)), matched)
	 docker tag ${DOCKER_TAG_API} ${DOCKER_TAG_API_LTS}
	 docker push ${DOCKER_TAG_API_LTS}

	 docker tag ${DOCKER_TAG_CELERY} ${DOCKER_TAG_CELERY_LTS}
	 docker push ${DOCKER_TAG_CELERY_LTS}

	 docker tag ${DOCKER_TAG_PUBSUB} ${DOCKER_TAG_PUBSUB_LTS}
	 docker push ${DOCKER_TAG_PUBSUB_LTS}
else
	 docker tag ${DOCKER_TAG_API} ${ECR}/${ECR_REPO_API}:dev
	 docker push ${ECR}/${ECR_REPO_API}:dev

	 docker tag ${DOCKER_TAG_CELERY} ${ECR}/${ECR_REPO_CELERY}:dev
	 docker push ${ECR}/${ECR_REPO_CELERY}:dev

	 docker tag ${DOCKER_TAG_PUBSUB} ${ECR}/${ECR_REPO_PUBSUB}:dev
	 docker push ${ECR}/${ECR_REPO_PUBSUB}:dev
endif

docker-push: docker-build
	docker push ${DOCKER_TAG_API} & docker push ${DOCKER_TAG_CELERY} & docker push ${DOCKER_TAG_PUBSUB}
ifeq ($(strip $(IS_PROD_TAG)), matched)
	 docker tag ${DOCKER_TAG_API} ${DOCKER_TAG_API_LTS}
	 docker push ${DOCKER_TAG_API_LTS}

	 docker tag ${DOCKER_TAG_CELERY} ${DOCKER_TAG_CELERY_LTS}
	 docker push ${DOCKER_TAG_CELERY_LTS}

	 docker tag ${DOCKER_TAG_PUBSUB} ${DOCKER_TAG_PUBSUB_LTS}
	 docker push ${DOCKER_TAG_PUBSUB_LTS}
else
	 docker tag ${DOCKER_TAG_API} ${ECR}/${ECR_REPO_API}:dev
	 docker push ${ECR}/${ECR_REPO_API}:dev

	 docker tag ${DOCKER_TAG_CELERY} ${ECR}/${ECR_REPO_CELERY}:dev
	 docker push ${ECR}/${ECR_REPO_CELERY}:dev

	 docker tag ${DOCKER_TAG_PUBSUB} ${ECR}/${ECR_REPO_PUBSUB}:dev
	 docker push ${ECR}/${ECR_REPO_PUBSUB}:dev
endif

