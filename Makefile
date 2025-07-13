.PHONY: generate-api-client lab

generate-api-client:
	@if [ ! -f resinkit_api_client/py.typed ]; then \
		echo "resinkit_api_client/ does not exist, are you in the correct folder?"; \
		exit 1; \
	fi
	uvx openapi-python-client generate --url http://127.0.0.1:8603/openapi.json --overwrite --output-path /tmp/resinkit_api
	cp -r /tmp/resinkit_api/resinkit_api_client .

lab:
	uv run jupyter lab --notebook-dir=sample_notebooks
