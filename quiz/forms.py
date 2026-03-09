from django import forms
from django.core.exceptions import ValidationError

from . import models


MCQ_HELP_TEXT = (
    "MCQ payload example: {\"options\": {\"0\": \"A\", \"1\": \"B\", \"2\": \"C\", \"3\": \"D\"}, "
    "\"correct_answer\": \"B\"} (you may also set correct_answer to option id like \"1\")."
)


class QuestionAdminForm(forms.ModelForm):
    payload = forms.JSONField(
        required=True,
        widget=forms.Textarea(attrs={"rows": 10, "class": "vLargeTextField"}),
        help_text=(
            f"{MCQ_HELP_TEXT} "
            "TF example: {\"correct_answer\": true}. "
            "FB example: {\"correct_answer\": \"answer\"}. "
            "READ example: {\"passage\": \"...\", \"sub_questions\": [{\"text\": \"...\", \"correct_answer\": \"...\"}]}."
        ),
    )

    class Meta:
        model = models.Question
        fields = "__all__"

    def clean_payload(self):
        payload = self.cleaned_data.get("payload") or {}
        question_type = self.cleaned_data.get("type") or getattr(self.instance, "type", None)

        if question_type == models.QuestionType.MULTIPLE_CHOICE:
            options = payload.get("options")
            correct_answer = payload.get("correct_answer")
            if not isinstance(options, dict) or not options:
                raise ValidationError("For MCQ, payload.options must be a non-empty object.")

            option_keys = {str(k) for k in options.keys()}
            option_values = {str(v).strip() for v in options.values() if str(v).strip()}

            if str(correct_answer) in option_keys:
                payload["correct_answer"] = options[str(correct_answer)]
            elif str(correct_answer).strip() not in option_values:
                raise ValidationError(
                    "For MCQ, correct_answer must match an option value (e.g. 'B') or an option id key (e.g. '1')."
                )

        if question_type == models.QuestionType.TRUE_FALSE:
            if not isinstance(payload.get("correct_answer"), bool):
                raise ValidationError("For True/False, correct_answer must be true or false.")

        if question_type == models.QuestionType.FILL_IN_THE_BLANK:
            if not str(payload.get("correct_answer", "")).strip():
                raise ValidationError("For Fill in the Blank, correct_answer cannot be empty.")

        if question_type == models.QuestionType.READING_PASSAGE:
            sub_questions = payload.get("sub_questions", [])
            if not isinstance(sub_questions, list):
                raise ValidationError("For Reading Passage, sub_questions must be an array.")

        return payload
