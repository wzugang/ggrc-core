# Copyright (C) 2016 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

# pylint: disable=maybe-no-member

"""Test request import and updates."""

from ggrc import models
from ggrc.converters import errors
from integration.ggrc import converters


class TestRequestImport(converters.TestCase):

  """Basic Request import tests with.

  This test suite should test new Request imports and updates. The main focus
  of these tests is checking error messages for invalid state transitions.
  """

  def setUp(self):
    """ Set up for Request test cases """
    converters.TestCase.setUp(self)
    self.client.get("/login")

  def _test_request_users(self, request, users):
    """ Test that all users have correct roles on specified Request"""
    verification_errors = ""
    for user_name, expected_types in users.items():
      try:
        user = models.Person.query.filter_by(name=user_name).first()
        rel = models.Relationship.find_related(request, user)
        if expected_types:
          self.assertNotEqual(
              rel,
              None,
              "User {} is not mapped to {}".format(user.email, request.slug)
          )
          self.assertIn("AssigneeType", rel.relationship_attrs)
          self.assertEqual(
              set(rel.relationship_attrs[
                  "AssigneeType"].attr_value.split(",")),
              expected_types
          )
        else:
          self.assertEqual(
              rel,
              None,
              "User {} is mapped to {}".format(user.email, request.slug)
          )
      except AssertionError as error:
        verification_errors += "\n\nChecks for Users-Request mapping failed "\
            "for user '{}' with:\n{}".format(user_name, str(error))

    self.assertEqual(verification_errors, "", verification_errors)

  def test_request_full_no_warnings(self):
    """ Test full request import with no warnings

    CSV sheet:
      https://docs.google.com/spreadsheets/d/1Jg8jum2eQfvR3kZNVYbVKizWIGZXvfqv3yQpo2rIiD8/edit#gid=704933240&vpid=A7
    """
    filename = "request_full_no_warnings.csv"
    response = self.import_file(filename)
    self._check_csv_response(response, {})

    # Test first request line in the CSV file
    request_1 = models.Request.query.filter_by(slug="Request 1").first()
    users = {
        "user 1": {"Assignee"},
        "user 2": {"Assignee", "Requester"},
        "user 3": {"Requester", "Verifier"},
        "user 4": {"Verifier"},
        "user 5": {"Verifier"},
    }
    self._test_request_users(request_1, users)
    self.assertEqual(request_1.status, models.Request.START_STATE)
    self.assertEqual(request_1.request_type, "documentation")

    # Test second request line in the CSV file
    request_2 = models.Request.query.filter_by(slug="Request 2").first()
    users = {
        "user 1": {"Assignee"},
        "user 2": {"Requester"},
        "user 3": {"Verifier"},
        "user 4": {},
        "user 5": {},
    }

    self._test_request_users(request_2, users)
    self.assertEqual(request_2.status, models.Request.PROGRESS_STATE)
    self.assertEqual(request_2.request_type, "interview")

  def test_request_import_states(self):
    """ Test Request state imports

    These tests are an intermediate part for zucchini release and will be
    updated in the next release.

    CSV sheet:
      https://docs.google.com/spreadsheets/d/1Jg8jum2eQfvR3kZNVYbVKizWIGZXvfqv3yQpo2rIiD8/edit#gid=299569476
    """
    self.import_file("request_full_no_warnings.csv")
    response = self.import_file("request_update_intermediate.csv")

    expected_errors = {
        "Request": {
            "block_errors": set(),
            "block_warnings": set(),
            "row_errors": set(),
            "row_warnings": set([
                errors.REQUEST_INVALID_STATE.format(line=5),
                errors.REQUEST_INVALID_STATE.format(line=6),
                errors.REQUEST_INVALID_STATE.format(line=11),
                errors.REQUEST_INVALID_STATE.format(line=12),
            ]),
        }
    }
    self._check_csv_response(response, expected_errors)

    requests = {r.slug: r for r in models.Request.query.all()}
    self.assertEqual(requests["Request 60"].status, models.Request.START_STATE)
    self.assertEqual(requests["Request 61"].status,
                     models.Request.PROGRESS_STATE)
    self.assertEqual(requests["Request 62"].status, models.Request.DONE_STATE)
    self.assertEqual(requests["Request 63"].status,
                     models.Request.PROGRESS_STATE)
    self.assertEqual(requests["Request 64"].status,
                     models.Request.PROGRESS_STATE)
    self.assertEqual(requests["Request 3"].status,
                     models.Request.PROGRESS_STATE)
    self.assertEqual(requests["Request 4"].status,
                     models.Request.PROGRESS_STATE)

    # Check that there is only one attachment left
    request1 = requests["Request 1"]
    self.assertEqual(len(request1.documents), 1)

    # Check that there are only the two new URLs present in request 1
    url_titles = set(obj.title for obj in request1.related_objects()
                     if isinstance(obj, models.Document))
    self.assertEqual(url_titles, set(["a.b.com", "c.d.com"]))

  def test_request_warnings_errors(self):
    """ Test full request import with warnings and errors

    CSV sheet:
      https://docs.google.com/spreadsheets/d/1Jg8jum2eQfvR3kZNVYbVKizWIGZXvfqv3yQpo2rIiD8/edit#gid=889865936
    """
    self.import_file("request_full_no_warnings.csv")
    response = self.import_file("request_with_warnings_and_errors.csv")

    expected_errors = {
        "Request": {
            "block_errors": set([]),
            "block_warnings": set([
                errors.UNKNOWN_COLUMN.format(
                    line=2,
                    column_name="error description - non existing column will "
                    "be ignored"
                ),
                errors.UNKNOWN_COLUMN.format(
                    line=2,
                    column_name="actual error message"
                ),
            ]),
            "row_errors": set([
                errors.UNKNOWN_OBJECT.format(
                    line=18,
                    object_type="Audit",
                    slug="not existing"
                ),
                errors.DUPLICATE_VALUE_IN_CSV.format(
                    line_list="19, 21",
                    column_name="Code",
                    value="Request 22",
                    s="",
                    ignore_lines="21",
                ),
            ]),
            "row_warnings": set([
                errors.UNKNOWN_USER_WARNING.format(
                    line=14,
                    email="non_existing@a.com",

                ),
                errors.UNKNOWN_OBJECT.format(
                    line=14,
                    object_type="Project",
                    slug="proj-55"
                ),
                errors.REQUEST_INVALID_STATE.format(line=20),
                errors.REQUEST_INVALID_STATE.format(line=21),
                errors.WRONG_REQUIRED_VALUE.format(
                    line=19,
                    column_name="Status",
                    value="open",
                ),
                errors.WRONG_VALUE.format(line=3, column_name="Url"),
            ]),
        }
    }
    self._check_csv_response(response, expected_errors)
