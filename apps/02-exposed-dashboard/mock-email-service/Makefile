IMAGE = atemate/webinar-k8sec_mock-email-service:v1.3

.PHONY: docker-build
docker-build:
	docker build . -t $(IMAGE)

.PHONY: docker-push
docker-push:
	docker push $(IMAGE)

.PHONY: docker-run
docker-run:
	docker run -p 8083:8080 $(IMAGE)
