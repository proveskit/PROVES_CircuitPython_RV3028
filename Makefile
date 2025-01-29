.PHONY: all
all: venv pre-commit-install help

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development

.venv: ## Create a virtual environment
	@echo "Creating virtual environment..."
	@$(MAKE) uv
	@$(UV) venv
	@$(UV) pip install --requirement pyproject.toml

.PHONY: pre-commit-install
pre-commit-install: uv
	@echo "Installing pre-commit hooks..."
	@$(UVX) pre-commit install > /dev/null

.PHONY: fmt
fmt: pre-commit-install ## Lint and format files
	$(UVX) pre-commit run --all-files

.PHONY: test
test: .venv ## Run tests
	$(UV) run coverage run --rcfile=pyproject.toml -m pytest tests/
	@$(UV) run coverage html --rcfile=pyproject.toml > /dev/null
	@$(UV) run coverage xml --rcfile=pyproject.toml > /dev/null

.PHONY: clean
clean: ## Remove all gitignored files such as downloaded libraries and artifacts
	git clean -dfX

##@ Build Tools
TOOLS_DIR ?= tools
$(TOOLS_DIR):
	mkdir -p $(TOOLS_DIR)

### Tool Versions
UV_VERSION ?= 0.5.24

UV_DIR ?= $(TOOLS_DIR)/uv-$(UV_VERSION)
UV ?= $(UV_DIR)/uv
UVX ?= $(UV_DIR)/uvx
.PHONY: uv
uv: $(UV) ## Download uv
$(UV): $(TOOLS_DIR)
	@test -s $(UV) || { mkdir -p $(UV_DIR); curl -LsSf https://astral.sh/uv/$(UV_VERSION)/install.sh | UV_INSTALL_DIR=$(UV_DIR) sh > /dev/null; }
