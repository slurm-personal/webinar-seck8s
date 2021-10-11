IMAGE = atemate/webinar-k8sec_mock-email-service:v1.4

.PHONY: docker-build
docker-build:
	docker build . -t $(IMAGE)

.PHONY: docker-push
docker-push:
	docker push $(IMAGE)

.PHONY: docker-run
docker-run:
	docker run -p 8083:8080 $(IMAGE)
	# $ curl http://0.0.0.0:8083/register -XPOST -d to_email=test@test.com -d subject="Test email"
