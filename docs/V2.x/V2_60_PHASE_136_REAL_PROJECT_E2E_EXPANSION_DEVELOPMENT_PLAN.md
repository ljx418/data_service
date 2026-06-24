# V2.60 / Phase 136 Real Project E2E Expansion Development Plan

Date: 2026-06-23

## 1. Scope

Implement V2.60 real project E2E expansion for data_service, codexPat, HarnessOS, and Navia.

## 2. Development Tasks

1. Implement project E2E matrix generation.
2. Implement project failure diagnosis.
3. Implement artifact availability report.
4. Implement markdown E2E expansion report.
5. Add focused tests for accepted, unavailable, blocker, and mock-only rejection states.
6. Add real data_service E2E script.

## 3. Boundaries

- data_service must be accepted for phase acceptance.
- codexPat, HarnessOS, and Navia may be accepted only with real evidence.
- Unavailable projects must be `structured_unavailable` or `structured_blocker`, not accepted.
- Mock-only evidence must be rejected.

## 4. Expected User Experience

Maintainers can inspect which real projects passed E2E, which are unavailable, why they are unavailable, and which next action is required.
