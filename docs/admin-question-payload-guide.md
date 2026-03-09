# Question Payload Admin Guide

This guide documents how to enter `Question.payload` safely in Django Admin.

## Where this is used
- Model: `quiz.models.Question`
- Admin form: `quiz.forms.QuestionAdminForm`
- Admin registration: `quiz.admin.QuestionAdmin`

## MCQ payload format
Use this JSON shape:

```json
{
  "options": {
    "0": "A",
    "1": "B",
    "2": "C",
    "3": "D"
  },
  "correct_answer": "B"
}
```

Notes:
- `correct_answer` can be either an option value (recommended) or an option id key.
- If you enter an id key such as `"1"`, admin validation normalizes it to the value `"B"`.

## Other payload examples

True/False:

```json
{
  "correct_answer": true
}
```

Fill in the Blank:

```json
{
  "correct_answer": "photosynthesis"
}
```

Reading Passage:

```json
{
  "passage": "Read the text...",
  "sub_questions": [
    {
      "text": "What is the main idea?",
      "correct_answer": "The main idea"
    }
  ]
}
```

## Validation behavior
- Missing required keys are rejected by model validation.
- Type-specific checks are enforced in admin form validation.
- `Question.save()` calls `full_clean()`, so invalid payload cannot be persisted.

## Why this approach
- Keeps one flexible JSON model for custom workflows and APIs.
- Makes admin CRUD less error-prone with explicit examples and normalization.
- Avoids schema churn while teacher/student workflow pages are still being developed.
