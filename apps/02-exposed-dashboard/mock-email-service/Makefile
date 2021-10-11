IMAGE = atemate/webinar-k8sec_mock-email-service:v1.4

.PHONY: docker-build
docker-build:
	docker build . -t $(IMAGE)

.PHONY: docker-push
docker-push:
	docker push $(IMAGE)
