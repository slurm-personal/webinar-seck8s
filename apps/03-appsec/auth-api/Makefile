IMAGE = atemate/webinar-k8sec_auth-api:v1.6

.PHONY: docker-build
docker-build:
	docker build . -t $(IMAGE)

.PHONY: docker-push
docker-push:
	docker push $(IMAGE)
