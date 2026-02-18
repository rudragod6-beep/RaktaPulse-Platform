from django.core.management.base import BaseCommand
from core.models import Hospital

class Command(BaseCommand):
    help = 'Seed the database with Kathmandu hospitals and coordinates'

    def handle(self, *args, **kwargs):
        hospitals = [
            {"name": "Bir Hospital", "location": "Kanti Path, Kathmandu", "phone": "01-4221988", "lat": 27.7058, "lng": 85.3135},
            {"name": "Kathmandu Valley Hospital", "location": "Bagh darbar marg, Kathmandu", "phone": "01-4255330", "lat": 27.7015, "lng": 85.3115},
            {"name": "Civil Service Hospital of Nepal", "location": "Minbhawan marg, Kathmandu", "phone": "01-4793000", "website": "https://csh.gov.np/ne", "lat": 27.6841, "lng": 85.3385},
            {"name": "Venus Hospital", "location": "Devkota Sadak, Kathmandu", "phone": "01-4475120", "lat": 27.6945, "lng": 85.3415},
            {"name": "Vayodha Hospital", "location": "Balkhu, Kathmandu", "phone": "01-4281666", "website": "https://www.vayodhahospitals.com/", "lat": 27.6855, "lng": 85.2935},
            {"name": "Grande City Hospital", "location": "Kanti path, Kathmandu", "phone": "01-4163500", "website": "http://grandecityhospital.com/", "lat": 27.7065, "lng": 85.3135},
            {"name": "Teaching Hospital", "location": "Maharajgunj, Kathmandu", "phone": "01-4412303", "website": "http://iom.edu.np/", "lat": 27.7351, "lng": 85.3315},
            {"name": "Kathmandu Hospital", "location": "Tripureshwor marg, Kathmandu", "phone": "01-4229656", "lat": 27.6935, "lng": 85.3145},
            {"name": "Kathmandu Neuro & General Hospital", "location": "Bagh Durbar marg, Kathmandu", "phone": "01-5327735", "lat": 27.7018, "lng": 85.3118},
            {"name": "Teku Hospital", "location": "Teku, Kathmandu", "phone": "01-4253396", "website": "http://www.stidh.gov.np/", "lat": 27.6961, "lng": 85.3025},
            {"name": "Nepal Eye Hospital", "location": "Tripureswor, Kathmandu", "phone": "01-4260813", "website": "https://www.nepaleyehospital.org/", "lat": 27.6940, "lng": 85.3140},
            {"name": "Everest Hospital Pvt. Ltd.", "location": "Kathmandu", "phone": "01-4793024", "website": "http://everesthospital.org.np/", "lat": 27.6925, "lng": 85.3345},
            {"name": "Om Hospital & Research Center", "location": "Chabil, Kathmandu", "phone": "01-4476225", "website": "https://omhospitalnepal.com/", "lat": 27.7175, "lng": 85.3485},
            {"name": "Annapurna Neuro Hospital", "location": "Maitighar mandala", "phone": "01-4256656", "website": "https://www.annapurnahospitals.com", "lat": 27.6945, "lng": 85.3215},
            {"name": "Norvic International Hospital", "location": "Kathmandu", "phone": "01-5970032", "website": "https://www.norvichospital.com/", "lat": 27.6897, "lng": 85.3235},
            {"name": "Blue Cross Hospital", "location": "Tripura marga, Kathmandu", "phone": "01-4262027", "lat": 27.6948, "lng": 85.3148},
            {"name": "Paropakar Maternity and Womens’ Hospital", "location": "Thapathali, Kathmandu", "phone": "01-4261363", "lat": 27.6915, "lng": 85.3215},
            {"name": "ERA INTERNATIONAL HOSPITAL Pvt. Ltd.", "location": "Kathmandu", "phone": "01-4352447", "website": "https://www.era-hospital.com/", "lat": 27.7215, "lng": 85.3015},
            {"name": "Birendra Military Hospital", "location": "Kathmandu", "phone": "01-4271941", "website": "https://birendrahospital.nepalarmy.mil.np/", "lat": 27.7085, "lng": 85.2815},
            {"name": "Capital Hospital", "location": "Kathmandu", "phone": "01-4168222", "lat": 27.7045, "lng": 85.3215},
            {"name": "Valley Maternity Nursing Home", "location": "Kathmandu", "phone": "01-4420224", "lat": 27.7125, "lng": 85.3245},
            {"name": "Medicare National Hospital & Research Center", "location": "Ring road, kathmandu", "phone": "01-4467067", "website": "http://medicarehosp.com/", "lat": 27.7145, "lng": 85.3415},
            {"name": "CIWEC Hospital Pvt. Ltd.", "location": "Kathmandu", "phone": "01-4435232", "lat": 27.7165, "lng": 85.3215},
            {"name": "Nepal-Bharat Maitri Hospital", "location": "Dakshinha murti marga, Kathmandu", "phone": "01-5241288", "lat": 27.7185, "lng": 85.3515},
            {"name": "Kantipur Hospital", "location": "Shriganesh Marg, Tripureshwor", "phone": "01-4111", "lat": 27.6938, "lng": 85.3142},
        ]

        for h_data in hospitals:
            Hospital.objects.update_or_create(
                name=h_data['name'],
                defaults={
                    'location': h_data['location'],
                    'phone': h_data['phone'],
                    'website': h_data.get('website', ''),
                    'latitude': h_data.get('lat'),
                    'longitude': h_data.get('lng'),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {len(hospitals)} hospitals with coordinates.'))
