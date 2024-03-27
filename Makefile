.PHONY: crossref
crossref:
	mkdir -p src/fpbase2/utils/crossref/
	rm -rf src/fpbase2/utils/crossref/_api_types
	datamodel-codegen  --url https://api.crossref.org/swagger-docs --output src/fpbase2/utils/crossref/_api_types.py --input-file-type=json
	rm -rf src/fpbase2/utils/crossref/_api_types/Funder*
	rm -rf src/fpbase2/utils/crossref/_api_types/Work*
	ruff check --fix src/fpbase2/utils/crossref/
	ruff format src/fpbase2/utils/crossref/
