.PHONY: all generate visuals validate contrast tokens install check release clean

# Use project venv if present, otherwise system python3
PYTHON := $(shell test -x .venv/bin/python3 && echo .venv/bin/python3 || echo python3)

# Default: regenerate + validate
all: generate validate

# Regenerate all theme files from palette
generate:
	$(PYTHON) scripts/generate.py

# Regenerate the phosphor-family screenshots (themes/pi/reckoner-*.json)
# Needs Pillow, which the project .venv does not carry; the system interpreter
# does. Nothing else in the pipeline draws raster images.
phosphor:
	python3 scripts/render_phosphor_screenshots.py

# Regenerate README visuals from palette
visuals:
	$(PYTHON) scripts/render_repo_visuals.py

# Structural + freshness + drift validation
validate:
	$(PYTHON) scripts/validate_theme.py

# Full WCAG contrast report
contrast:
	$(PYTHON) scripts/contrast_matrix.py

# Export design tokens for web/CSS/Tailwind consumers
tokens:
	$(PYTHON) scripts/export_tokens.py

# Install Pi theme to local system (safe: backup + integrity check)
install:
	bash scripts/install.sh

# Full check: generate, validate, contrast, tokens
check: generate validate contrast tokens

# Build release artifacts into dist/
release:
	bash scripts/build_release.sh

# Remove dist/
clean:
	rm -rf dist/
