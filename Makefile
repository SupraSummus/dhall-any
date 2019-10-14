SEMANTICS_CHUNKS := \
    README \
    alpha-normalization \
    beta-normalization \
    shift \
    substitution \
    type-inference \

SEMANTICS_RAW_DIR = dhall-lang/standard/
SEMANTICS_PATCH_DIR = semantics_patches/
SEMANTICS_RAW_PATCHED_DIR = build/semantics_raw/
SEMANTICS_PARSED_DIR = build/semantics_parsed/

.PHONY: clean semantics_patch
.PRECIOUS: $(SEMANTICS_RAW_PATCHED_DIR)%.md

all: $(addprefix $(SEMANTICS_PARSED_DIR),$(addsuffix .json,$(SEMANTICS_CHUNKS)))

# this is for regenerating the patch - use it manually and with caution as it's operating on generated files
semantics_patch:
	$(foreach CHUNK,$(SEMANTICS_CHUNKS), \
		diff -u $(SEMANTICS_RAW_DIR)$(CHUNK).md $(SEMANTICS_RAW_PATCHED_DIR)$(CHUNK).md \
		> $(SEMANTICS_PATCH_DIR)$(CHUNK).md.patch; \
		test $$? -le 1; \
	)

$(SEMANTICS_RAW_PATCHED_DIR)%.md: $(SEMANTICS_RAW_DIR)%.md $(SEMANTICS_PATCH_DIR)%.md.patch
	patch -o $@ $^

$(SEMANTICS_PARSED_DIR)%.json: $(SEMANTICS_RAW_PATCHED_DIR)%.md
	cat $^ | python semantics_parser.py > $@

clean:
	rm $(SEMANTICS_PARSED_DIR)* $(SEMANTICS_RAW_PATCHED_DIR)*
