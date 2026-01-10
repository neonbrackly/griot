# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Custom targets
.PHONY: livehtml clean-all apidoc

# Live reload server for development
livehtml:
	sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)

# Clean all build artifacts
clean-all:
	rm -rf $(BUILDDIR)
	rm -rf api-reference/generated

# Generate API documentation stubs
apidoc:
	sphinx-apidoc -f -o api-reference/generated ../griot/griot-core/src/griot_core
	sphinx-apidoc -f -o api-reference/generated ../griot/griot-cli/src/griot_cli
	sphinx-apidoc -f -o api-reference/generated ../griot/griot-enforce/src/griot_enforce
	sphinx-apidoc -f -o api-reference/generated ../griot/griot-registry/src/griot_registry
