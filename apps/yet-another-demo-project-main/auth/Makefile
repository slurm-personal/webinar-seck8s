
IMAGE = atemate/webinar-k8sec_auth-api:v1.0

.PHONY: build-image
build-image:
	docker build . -t $(IMAGE)

.PHONY: push-image
push-image:
	docker push $(IMAGE)
