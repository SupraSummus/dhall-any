SEMANTICS_RAW = dhall-lang/standard/semantics.md
SEMANTICS_PATCH = semantics.md.patch
SEMANTICS_RAW_PATCHED = build/semantics.md
SEMANTICS_PARSED = build/semantics.json

.PHONY: clean semantics_patch

all: $(SEMANTICS_PARSED)

# this is for regenerating the patch - use it manually and with caution as it's operating on generated files
semantics_patch:
	diff -u $(SEMANTICS_RAW) $(SEMANTICS_RAW_PATCHED) > $(SEMANTICS_PATCH); test $$? -le 1

$(SEMANTICS_RAW_PATCHED): $(SEMANTICS_RAW) $(SEMANTICS_PATCH)
	patch -o $(SEMANTICS_RAW_PATCHED) $(SEMANTICS_RAW) $(SEMANTICS_PATCH)

$(SEMANTICS_PARSED): semantics_parser.py $(SEMANTICS_RAW_PATCHED)
	cat $(SEMANTICS_RAW_PATCHED) | python semantics_parser.py > $(SEMANTICS_PARSED)

clean:
	rm -r build/*
