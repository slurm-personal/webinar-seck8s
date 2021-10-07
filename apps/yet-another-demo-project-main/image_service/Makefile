IMAGE = atemate/webinar-k8sec_image-api:v1.0

.PHONY: docker-build
docker-build:
	docker build . -t $(IMAGE)

.PHONY: docker-push
docker-push:
	docker push $(IMAGE)

.PHONY: docker-run
docker-run:
	docker run -p 8082:8080 $(IMAGE)
