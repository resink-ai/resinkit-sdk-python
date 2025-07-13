.PHONY: generate-api-client
generate-api-client:
	uvx openapi-python-client generate --url http://127.0.0.1:8603/openapi.json --overwrite --output-path /tmp/resinkit_api
	cp -r /tmp/resinkit_api/resinkit_api_client .