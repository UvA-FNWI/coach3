from django import forms

class GoalResetForm(forms.Form):
   "Form for resetting the goal grade"
   new_goal_grade = forms.FloatField(label="new_goal_grade")
