.DEFAULT_GOAL := help

PROJECT_ID ?= anim-482714
REGION ?= us-central1
SERVICE_NAME ?= animai-api
IMAGE_NAME ?= animai
REPO_NAME ?= animai-repo
IMAGE_URL := $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(REPO_NAME)/$(IMAGE_NAME)
CONTAINER_NAME ?= $(SERVICE_NAME)

.PHONY: install dev test integration_tests test-local test-local-run test-run benchmark \
	lint format docker-build docker-run docker-stop docker-logs docker-shell docker-clean \
	tf-init tf-plan tf-apply tf-destroy gcp-auth push update deploy deploy-full logs \
	logs-follow describe url clean help

## LOCAL DEV
install: ## Install Python dependencies
	pip install -r requirements.txt

dev: ## Run the API locally with reload
	PYTHONPATH=src uvicorn src.api.main:app --reload --port 8000

## TESTING
test: ## Run unit tests
	pytest unit

integration_tests: ## Run integration tests
	pytest integration

test-local: ## Test local health endpoint
	curl -s http://localhost:8000/health

test-local-run: ## Test local /run endpoint
	curl -s -X POST http://localhost:8000/run \
		-H "Content-Type: application/json" \
		-d '{"prompt":"Explain projectile motion","language":"en"}'

test-run: ## Test deployed /run endpoint
	curl -s -X POST "$$(gcloud run services describe $(SERVICE_NAME) --region $(REGION) --format='value(status.url)')/run" \
		-H "Content-Type: application/json" \
		-d '{"prompt":"Explain projectile motion","language":"en"}'

benchmark: ## Run a quick load test against the local health endpoint
	hey -n 50 -c 5 http://localhost:8000/health

## LINTING
lint: ## Run linting and type checks
	ruff check .
	ruff format --check .
	mypy src

format: ## Format the codebase
	ruff format .
	isort .

## DOCKER
docker-build: ## Build and tag the API container image
	docker build -t $(IMAGE_NAME):latest -t $(IMAGE_URL):latest .

docker-run: ## Run the API container locally
	docker run --env-file .env -p 8000:8000 --name $(CONTAINER_NAME) -d $(IMAGE_NAME):latest

docker-stop: ## Stop the local API container
	-docker rm -f $(CONTAINER_NAME)

docker-logs: ## Show local API container logs
	docker logs $(CONTAINER_NAME)

docker-shell: ## Open a shell in the local API container
	docker exec -it $(CONTAINER_NAME) /bin/sh

docker-clean: ## Remove the local API container and image tags
	-docker rm -f $(CONTAINER_NAME)
	-docker rmi $(IMAGE_NAME):latest
	-docker rmi $(IMAGE_URL):latest

## TERRAFORM
tf-init: ## Initialize Terraform
	cd terraform && terraform init

tf-plan: ## Preview Terraform changes
	cd terraform && terraform plan

tf-apply: ## Apply Terraform changes
	cd terraform && terraform apply -lock=false

tf-destroy: ## Destroy Terraform-managed infrastructure
	cd terraform && terraform destroy

## GCP
gcp-auth: ## Authenticate to GCP and Artifact Registry
	gcloud auth login
	gcloud config set project $(PROJECT_ID)
	gcloud auth configure-docker $(REGION)-docker.pkg.dev

push: ## Push the latest API image to Artifact Registry
	docker push $(IMAGE_URL):latest

update: ## Update the deployed Cloud Run API service
	gcloud run services update $(SERVICE_NAME) --region $(REGION) --image $(IMAGE_URL):latest

## DEPLOY
deploy: docker-build push update ## Build, push, and update the API service

deploy-full: docker-build push tf-apply update ## Apply infra and deploy the API service

## MONITORING
logs: ## Read recent Cloud Run logs
	gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$(SERVICE_NAME)" --limit 50

logs-follow: ## Follow Cloud Run logs
	gcloud beta run services logs tail $(SERVICE_NAME) --region $(REGION)

describe: ## Describe the deployed Cloud Run service
	gcloud run services describe $(SERVICE_NAME) --region $(REGION)

url: ## Print the deployed service URL
	gcloud run services describe $(SERVICE_NAME) --region $(REGION) --format='value(status.url)'

## CLEANUP
clean: ## Remove Python cache artifacts
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -prune -exec rm -rf {} +

## HELP
help: ## Print all available commands
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
