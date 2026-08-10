# Native Feishu report template

Use a user-provided or team-approved canonical template. Keep internal document
URLs and tokens in the installed private copy or provide them at runtime; do not
commit them to a public repository.

## Usage

1. Obtain the approved template URL or token. If none is available, create a new document from [report-structure.md](report-structure.md).
2. Read the `lark-drive` skill and use its document-copy workflow to create a copy of the canonical template.
3. Never edit, rename, or overwrite the canonical template.
4. Rename the copy to `【服务名】技术调研报告` or a more specific topic title.
5. Read the `lark-doc` skill before filling the copy. Preserve the evidence-grade table and evidence index.
6. Replace `【填写：…】` placeholders, remove instructions and unused rows, and delete optional sections that do not apply.
7. Keep solution comparison only when there are at least two real choices. Add a diagram only when it materially clarifies a complex relationship.
8. Fetch the finished document to verify its title, required sections, evidence IDs, and absence of leftover placeholders before returning the link.
