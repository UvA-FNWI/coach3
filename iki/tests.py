from django.test import TestCase
from utils.ComparisonBuckets import frequency_count_comp

# Create your tests here.
# class ModelTest(TestCase):
#     def test_buckets(self):
#         buckets = frequency_count_comp([8,8,8,8,8], 10)
#         print(buckets)

buckets = frequency_count_comp([8,8,8,8,8], 10)
print(buckets)