.PHONY: all generate validate contrast install check release clean

# Default: regenerate + validate
all: generate validate

# Regenerate all theme files from palette
generate:
	python3 scripts/generate.py

# Structural + freshness + drift validation
validate:
	python3 scripts/validate_theme.py

# Full WCAG contrast report
contrast:
	python3 scripts/contrast_matrix.py

# Install Pi theme to local system (safe: backup + integrity check)
install:
	bash scripts/install.sh

# Full check: generate, validate, contrast
check: generate validate contrast

# Build release artifacts into dist/
release:
	bash scripts/build_release.sh

# Remove dist/
clean:
	rm -rf dist/
