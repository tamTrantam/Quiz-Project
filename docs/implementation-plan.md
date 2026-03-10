# LMS Implementation Plan

This plan follows the current project state and defines the next development phases.

## Current completed baseline
- Stabilized templates and routing
- Normalized homepage auth entry
- Completed local auth flows (login/logout/reset)
- Partial Google auth wiring (provider and routes integrated)

## Checkpoint (2026-03-09)
- Student workflow views are implemented: assignment list/detail and document access from dashboard.
- Student workflow tests pass under `manage.py test quiz`.
- Question admin CRUD has been improved with a custom admin form for `payload` guidance and validation.
- Admin now accepts MCQ `correct_answer` as option id (e.g. `"1"`) or option value (e.g. `"B"`), then normalizes to option value.
- Teacher workflow phase is implemented: teacher quiz/doc dashboards and per-course roster/content detail view are now live.
- Teacher access tests are passing in `accounts/tests.py` for role and membership guard behavior.

### Resume from here
1. Optional teacher polish: add search/filter on teacher course roster pages.
2. Optional teacher polish: add quick links from teacher course detail to assignment/document admin changelists.
3. Start `Phase 4: Grading and ranking`.

## Phase 1: Doc and Assignment models
Goal: Introduce content and assignment entities that connect to courses.

### Tasks
- Add `CourseDocument` model with hierarchy support (`parent` self FK).
- Add `Assignment` model with type (`quiz`, `document`, `homework`) and course linkage.
- Add validation constraints (e.g., `type=quiz` requires `quiz` reference).
- Register both models in admin with list/search/filter configuration.
- Create and apply migrations.

### Acceptance criteria
- Admin can create folder/file/link documents per course.
- Admin can create assignments tied to courses.
- Invalid model combinations are blocked by validation.

## Phase 2: Student workflow views
Goal: Student can view assigned work and documents.

### Tasks
- Create student assignment list/detail views.
- Create student document tree/list view.
- Add URL routes under `quiz/urls.py`.
- Restrict results to active student memberships.
- Render in the current dashboard viewport style.

### Acceptance criteria
- Student only sees data for enrolled courses.
- Breadcrumbs update according to page context.

## Phase 3: Teacher workflow views
Goal: Teacher can manage course content and student list.

### Tasks
- Add teacher course list view.
- Add per-course student list (filter/search by name).
- Add placeholder forms/pages for document upload and assignment creation.
- Restrict access to teacher/superuser.

### Acceptance criteria
- Teacher can navigate course -> students -> content pages.
- Student cannot access teacher-only pages.

## Phase 4: Grading and ranking
Goal: Implement completion and average-based ranking.

### Tasks
- Add `Submission` model (`assignment`, `student`, `status`, `score`, timestamps).
- Add statistics query helpers.
- Implement ranking order:
  1) completed assignments DESC
  2) average grade DESC

### Acceptance criteria
- Teacher can view per-student completion, average, and rank in course context.

## Phase 5: Notifications
Goal: Notify students when new work is published.

### Tasks
- Add `Notification` model (`user`, `title`, `message`, `is_read`, timestamps).
- Trigger notification on assignment publish.
- Add in-app notification area in dashboard.
- Optional email notifications via backend (toggle with env).

### Acceptance criteria
- Student sees notification entries for newly published assignments.

## Phase 6: Permission hardening
Goal: Prevent cross-role and cross-course data leaks.

### Tasks
- Enforce role decorators/checks on all new views.
- Enforce membership checks in all course queries.
- Add negative-path tests for unauthorized access.

### Acceptance criteria
- Unauthorized requests are redirected or denied consistently.

## Phase 7: Seed and demo readiness
Goal: Make demo setup reproducible.

### Tasks
- Create management command: `python manage.py seed_demo`.
- Seed users, courses, memberships, documents, quizzes, assignments, submissions.
- Improve admin UX with search/list filters.
- Document demo credentials and walkthrough in README.

### Acceptance criteria
- Fresh database can be demo-ready in one command sequence.

## Suggested execution order
1. Phase 1 (models + migrations)
2. Phase 2 and 3 (basic student/teacher pages)
3. Phase 4 (grading + ranking)
4. Phase 5 (notifications)
5. Phase 6 (permissions)
6. Phase 7 (seeding and demo docs)

## Deployment safety checklist per phase
- Run `python manage.py makemigrations`
- Run `python manage.py migrate`
- Run `python manage.py check`
- Run `python manage.py test` (or targeted tests)
- For production releases, run `python manage.py check --deploy`
