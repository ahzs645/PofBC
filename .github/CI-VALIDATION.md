# Validation scope and local commands

Salary UI changes keep the Node data/UI tests and preview build. Parser scripts, published/research data, generated indexes, shared configuration, unknown paths and manual runs retain parser fixtures, frozen historical replay, regeneration and preservation checks. Salary-search owns exhaustive discovery and mounted UI checks. The salary workflow owns their shared unit suite and preview.

## Local entry points

```sh
npm ci --ignore-scripts
node --test src/salaries/*.test.js scripts/salary-search.test.mjs
npm run check:salary-search
# Full source reconstruction: Actions → Verify salary sources and exports → Run workflow
# Preview: npm run preview:salaries -- --build
```

Feature branches without an open PR use local commands. A local pass does not replace validation of the submitted revision. Main/release publication keeps the workflow's existing authorization and artifact conditions.

CI optimization batch: November 7, 2026. Workflow syntax and focused orchestration/selection checks are separate from complete application, native-platform and research validation.
