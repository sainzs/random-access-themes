# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in Random Access Themes, please report it responsibly.

### How to Report

**Do not open a public GitHub issue for security vulnerabilities.**

Instead, please email: **sainzs@users.noreply.github.com**

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### What to Expect

- **Acknowledgment**: We will acknowledge receipt within 48 hours
- **Assessment**: We will assess the vulnerability within 7 days
- **Resolution**: We will work to resolve critical vulnerabilities within 30 days
- **Disclosure**: We will coordinate disclosure with you after a fix is available

### Security Considerations

This repository contains **theme files** (color palettes) for terminals and editors. Security considerations include:

1. **Generated Files**: Theme files are generated from YAML palettes using Python scripts. The scripts do not execute arbitrary code or make network requests.

2. **Installation**: The `install.sh` script copies theme files to local configuration directories. It does not modify system files or execute remote code.

3. **Dependencies**: The only dependency is `pyyaml` for parsing palette files. No runtime dependencies are installed.

4. **File System Access**: Scripts only read/write files within the repository and user configuration directories (e.g., `~/.config/ghostty`).

### Security Best Practices

When using this theme:

- Review `install.sh` before running it
- Use `--dry-run` flag to preview installation
- Do not run installation scripts from untrusted sources
- Keep your terminal/editor updated to benefit from security patches

## Security Updates

Security updates will be released as patch versions (e.g., 0.1.1 → 0.1.2) and announced via GitHub Security Advisories.

## Responsible Disclosure

We appreciate responsible disclosure. If you report a valid security vulnerability, we will:

- Credit you in the security advisory (unless you prefer to remain anonymous)
- Mention your contribution in the CHANGELOG
- Work with you to understand and resolve the issue

Thank you for helping keep this project secure.
