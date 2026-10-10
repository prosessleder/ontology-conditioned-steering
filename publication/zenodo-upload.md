# Zenodo upload instructions

This package is ready for review and manual deposit as a **research protocol preprint**, not a completed empirical study. No Zenodo record has been created or published, and no DOI is claimed.

1. Review the author name (currently Tim O'Brien from the authenticated GitHub profile), author order, affiliation, ORCID, and licenses. No affiliation or ORCID was invented. Confirm coauthors, funding, and competing interests before adding declarations.
2. Upload output/pdf/controlling-incompatible-magic.pdf and publication/ontology-conditioned-steering-v0.1.0-source.zip. The archive contains the manuscript source, specifications, code, tests, and literature audit. It excludes credentials, model weights, generated model results, and the PDF itself.
3. Choose Publication / Preprint in the deposit form. Keep "Research protocol preprint; model experiments pending" in the description. For a single mixed manuscript/code record, the primary type should reflect the paper. A later software-only record can use a separate DOI and link to the manuscript.
4. Use the title and description from .zenodo.json. That file provides the GitHub integration metadata format; it is not a promise that a modern Zenodo API accepts the file directly. Enter publication date as the actual first public availability date, rather than automatically copying the draft's preparation date. Set manuscript license CC BY 4.0 and disclose MIT for code.
5. If no DOI already identifies this exact record, select that it has none. Zenodo can reserve a DOI in the draft. Only then insert the real reserved DOI into the manuscript if desired, regenerate the PDF, and upload the revised file. Do not create a placeholder DOI or reuse a related paper's DOI.
6. Preview the record, check the file list and metadata, and publish when the author is ready. Experimental results can be deposited as a clearly identified later version with frozen selections, raw outputs, and analysis reports.

Official guidance checked on 2026-10-09: [Create new upload](https://help.zenodo.org/docs/deposit/create-new-upload/). Zenodo describes draft saving, metadata, resource types, DOI reservation, and preview before publication there.

The source archive is rebuilt with `python scripts/build_source_archive.py`. Verify checksums in publication/SHA256SUMS before upload. PDF rendering uses `python scripts/build_pdf.py` with ReportLab, as described in README.md.
