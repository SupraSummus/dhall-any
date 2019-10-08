Here I'm trying to build dhall implementation without manualy rewriting language rules from language specification. Join me and I'll be delighted ;)

Currently I'm focused on parsing semantic rules. Resulting files are attached in repo, in `build/` directory. If you want to make them yoursef:

    pipenv install  # instal python deps
    pipenv shell  # enter the environment
    make

To update semantics patches (because raw semantics description is not structured enough)

    make semantics_patches
