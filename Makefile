.PHONY: build parse-host parse-sample clean
build:
	docker build -t homelab-01-parser:latest .
parse-host: build
	docker compose run --rm parser-host
	@echo "CSV → evidence/auth_failures.csv"
parse-sample: build
	docker compose run --rm parser-sample
	@echo "CSV → evidence/auth_failures.csv"
clean:
	docker image rm homelab-01-parser:latest 2>/dev/null || true
