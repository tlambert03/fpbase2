.PHONY: crossref
crossref:
	rm -rf fpbase2/utils/crossref/_api_types
	datamodel-codegen  --url https://api.crossref.org/swagger-docs --output fpbase2/utils/crossref/_api_types
	rm -rf fpbase2/utils/crossref/_api_types/Funder*
	rm -rf fpbase2/utils/crossref/_api_types/Work*
