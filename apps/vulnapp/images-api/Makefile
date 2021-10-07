IMAGE = atemate/webinar-k8sec_images-api:v1.3

.PHONY: docker-build
docker-build:
	docker build . -t $(IMAGE)

.PHONY: docker-push
docker-push:
	docker push $(IMAGE)

.PHONY: docker-run
docker-run:
	docker run -p 8082:8080 -e SECRET_KEY=secret123 $(IMAGE)
