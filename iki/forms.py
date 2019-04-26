from django import forms

class GoalResetForm(forms.Form):
   new_goal_grade = forms.FloatField(label="new_goal_grade")

   # if type
