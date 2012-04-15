from datetime import date
import StringIO

from django.test import TestCase

from multigtfs.models import Block, Feed, Route, Service, Shape, Trip
from multigtfs.models.trip import import_trips_txt


class TripTest(TestCase):
    def setUp(self):
        self.feed = Feed.objects.create()
        self.route = Route.objects.create(
            feed=self.feed, route_id='R1', rtype=3)

    def test_string(self):
        trip = Trip.objects.create(route=self.route, trip_id='T1')
        self.assertEqual(str(trip), '1-R1-T1')

    def test_import_trips_txt_minimal(self):
        trips_txt = StringIO.StringIO("""\
route_id,service_id,trip_id
R1,S1,T1
""")
        service = Service.objects.create(
            feed=self.feed, service_id='S1', start_date=date(2011, 4, 14),
            end_date=date(2011, 12, 31))
        import_trips_txt(trips_txt, self.feed)
        trip = Trip.objects.get()
        self.assertEqual(trip.route, self.route)
        self.assertEqual(list(trip.services.all()), [service])
        self.assertEqual(trip.trip_id, 'T1')
        self.assertEqual(trip.headsign, '')
        self.assertEqual(trip.short_name, '')
        self.assertEqual(trip.direction, '')
        self.assertEqual(trip.block, None)
        self.assertEqual(trip.shape, None)

    def test_import_trips_txt_maximal(self):
        trips_txt = StringIO.StringIO("""\
route_id,service_id,trip_id,trip_headsign,trip_short_name,direction_id,\
block_id,shape_id
R1,S1,T1,Headsign,HS,0,B1,S1
""")
        service = Service.objects.create(
            feed=self.feed, service_id='S1', start_date=date(2011, 4, 14),
            end_date=date(2011, 12, 31))
        block = Block.objects.create(feed=self.feed, block_id='B1')
        shape = Shape.objects.create(feed=self.feed, shape_id='S1')
        import_trips_txt(trips_txt, self.feed)
        trip = Trip.objects.get()
        self.assertEqual(trip.route, self.route)
        self.assertEqual(list(trip.services.all()), [service])
        self.assertEqual(trip.trip_id, 'T1')
        self.assertEqual(trip.headsign, 'Headsign')
        self.assertEqual(trip.short_name, 'HS')
        self.assertEqual(trip.direction, '0')
        self.assertEqual(trip.block, block)
        self.assertEqual(trip.shape, shape)

    def test_import_trips_txt_multiple_services(self):
        '''If a trip is associated with several services, one is created'''
        trips_txt = StringIO.StringIO("""\
route_id,service_id,trip_id
R1,S1,T1
R1,S2,T1
""")
        service1 = Service.objects.create(
            feed=self.feed, service_id='S1', start_date=date(2011, 4, 14),
            end_date=date(2011, 12, 31))
        service2 = Service.objects.create(
            feed=self.feed, service_id='S2', start_date=date(2012, 1, 1),
            end_date=date(2012, 4, 14))

        import_trips_txt(trips_txt, self.feed)
        trip = Trip.objects.get()
        self.assertEqual(trip.route, self.route)
        self.assertEqual(trip.services.count(), 2)
        self.assertTrue(service1 in trip.services.all())
        self.assertTrue(service2 in trip.services.all())
