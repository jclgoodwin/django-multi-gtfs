"""Define Agency model for rows in agency.txt

Google documentation from
https://developers.google.com/transit/gtfs/reference

agency.txt is required

- agency_id (optional)
The agency_id field is an ID that uniquely identifies a transit agency. A
transit feed may represent data from more than one agency. The agency_id
is dataset unique. This field is optional for transit feeds that only
contain data for a single agency.

- agency_name (required)
The agency_name field contains the full name of the transit agency. Google
Maps will display this name.

- agency_url (required)
The agency_url field contains the URL of the transit agency. The value must
be a fully qualified URL that includes http:// or https://, and any special
characters in the URL must be correctly escaped. See
  http://www.w3.org/Addressing/URL/4_URI_Recommentations.html
for a description of how to create fully qualified URL values.

- agency_timezone (required)
The agency_timezone field contains the timezone where the transit agency is
located. Timezone names never contain the space character but may contain
an underscore. Please refer to
  http://en.wikipedia.org/wiki/List_of_tz_zones
for a list of valid values.  If multiple agencies are specified in the
feed, each must have the same agency_timezone.

- agency_lang (optional)
The agency_lang field contains a two-letter ISO 639-1 code for the primary
language used by this transit agency. The language code is case-insensitive
(both en and EN are accepted). This setting defines capitalization rules
and other language-specific settings for all text contained in this transit
agency's feed. Please refer to
  http://www.loc.gov/standards/iso639-2/php/code_list.php
for a list of valid values.

- agency_phone (optional)
The agency_phone field contains a single voice telephone number for the
specified agency. This field is a string value that presents the telephone
number as typical for the agency's service area. It can and should contain
punctuation marks to group the digits of the number. Dialable text (for
example, TriMet's "503-238-RIDE") is permitted, but the field must not
contain any other descriptive text.

- agency_fare_url (optional)
The agency_fare_url specifies the URL of a web page that allows a rider to
purchase tickets or other fare instruments for that agency online. The
value must be a fully qualified URL that includes http:// or https://, and
any special characters in the URL must be correctly escaped. See
  http://www.w3.org/Addressing/URL/4_URI_Recommentations.html
for a description of how to create fully qualified URL values.
"""

from csv import DictReader

from django.db import models


class Agency(models.Model):
    """One or more transit agencies that provide the data in this feed."""
    feed = models.ForeignKey('Feed')
    agency_id = models.CharField(
        max_length=255, blank=True, db_index=True,
        help_text="Unique identifier for transit agency")
    name = models.CharField(
        max_length=255,
        help_text="Full name of the transit agency")
    url = models.URLField(
        verify_exists=False, blank=True,
        help_text="URL of the transit agency")
    timezone = models.CharField(
        max_length=255,
        help_text="Timezone of the agency")
    lang = models.CharField(
        max_length=2, blank=True,
        help_text="ISO 639-1 code for the primary language")
    phone = models.CharField(
        max_length=255,
        help_text="Voice telephone number")
    fare_url = models.URLField(
        verify_exists=False, blank=True,
        help_text="URL for purchasing tickets online")

    def __unicode__(self):
        return u"%d-%s" % (self.feed.id, self.agency_id)

    class Meta:
        db_table = 'agency'
        app_label = 'multigtfs'
        verbose_name_plural = "agencies"


def import_agency_txt(agency_file, feed):
    """Import agency.txt into Agency records for feed.

    Keyword arguments:
    agency_file -- A open agency.txt for reading
    feed -- the Feed to associate the records with
    """
    reader = DictReader(agency_file)
    name_map = dict(agency_url='url', agency_name='name',
                    agency_phone='phone', agency_fare_url='fare_url',
                    agency_timezone='timezone', agency_lang='lang')
    for row in reader:
        fields = dict((name_map.get(k, k), v) for k, v in row.items())
        Agency.objects.create(feed=feed, **fields)
