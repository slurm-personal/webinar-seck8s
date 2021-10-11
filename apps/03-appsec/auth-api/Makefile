IMAGE = atemate/webinar-k8sec_auth-api:v1.5

.PHONY: docker-build
docker-build:
	docker build . -t $(IMAGE)

.PHONY: docker-push
docker-push:
	docker push $(IMAGE)

.PHONY: docker-run
docker-run:
	docker run -p 8081:8080 \
		-e SQL_HOST=0.0.0.0 \
		-e SQL_PORT=33060 \
		-e SQL_DB=userdata \
		-e SQL_USERNAME=username \
		-e SQL_PASSWORD=password \
		-e REDIRECT_HOST=http://0.0.0.0:8082 \
		-e SECRET_KEY=secret123 \
		$(IMAGE)
