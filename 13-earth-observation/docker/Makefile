BUILD_IMAGE ?= johan/openeo
PUSH_IMAGE ?= johan/openeo	

build:
	docker build -t $(BUILD_IMAGE) . 
push:
	docker tag $(BUILD_IMAGE) $(PUSH_IMAGE) 
	docker push $(PUSH_IMAGE)
