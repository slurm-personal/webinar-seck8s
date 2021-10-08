IMAGE = atemate/webinar-k8sec_auth-api:v1.3

.PHONY: docker-build
docker-build:
	docker build . -t $(IMAGE)

.PHONY: docker-push
docker-push:
	docker push $(IMAGE)

.PHONY: docker-run
docker-run:
	docker run -p 8081:8080 \
		-e REDIRECT_HOST=http://0.0.0.0:8082 \
		-e SECRET_KEY=secret123 \
		$(IMAGE)
