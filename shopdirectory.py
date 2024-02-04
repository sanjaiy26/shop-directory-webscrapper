import scrapy
import csv

class MRTShopSpider(scrapy.Spider):
    name = 'mrt_shop_spider'
    allowed_domains = ['stellarlifestyle.com.sg', 'sbstransit.com.sg']
    start_urls = [
        'https://stellarlifestyle.com.sg/shop-directory',
        'https://www.sbstransit.com.sg/Service/Shop'
    ]

    def __init__(self):
        self.station_names = self.initialize_station_names()

    @staticmethod
    def initialize_station_names():
        # Define the station names based on their lines
        lines = {
            "north-south": [
                "Jurong East", "Bukit Batok", "Bukit Gombak", "Choa Chu Kang", "Yew Tee", "Kranji", "Marsiling", 
                "Woodlands", "Admiralty", "Sembawang", "Canberra", "Yishun", "Khatib", "Yio Chu Kang", "Ang Mo Kio", 
                "Bishan", "Braddell", "Toa Payoh", "Novena", "Newton", "Orchard", "Somerset", "Dhoby Ghaut", 
                "City Hall", "Raffles Place", "Pier"
            ],
            "east-west": [
                "Pasir Ris", "Tampines", "Simei", "Tanah Merah", "Bedok", "Kembangan", "Eunos", "Paya Lebar", "Aljunied", 
                "Kallang", "Lavender", "Bugis", "Tanjong Pagar", "Outram Park", "Tiong Bahru", "Redhill", "Queenstown", 
                "Commonwealth", "Buona Vista", "Dover", "Clementi", "Chinese Garden", "Lakeside", "Boon Lay", "Pioneer", 
                "Joo Koon", "Gul Circle", "Tuas Crescent", "Tuas West Road", "Tuas Link", "Expo"
            ],
            "north-east": [
                "Chinatown", "Clarke Quay", "Little India", "Farrer Park", "Boon Keng", "Potong Pasir", "Serangoon", 
                "Kovan", "Hougang", "Buangkok", "Sengkang", "Punggol"
            ],
            "circle": [
                "Esplanade", "Promenade", "Nicoll Highway", "Stadium", "Caldecott", "Botanic Gardens", "Holland Village", 
                "one-north", "Bayfront"
            ],
            "downtown": [
                "Bukit Panjang", "Hillview", "Beauty World", "King Albert Park", "Sixth Avenue", "Newton", "Rochor", 
                "Little India", "Bugis", "Promenade", "Downtown", "Telok Ayer", "Chinatown", "Bencoolen", "Jalan Besar", 
                "Bendemeer", "Geylang Bahru", "Mattar", "MacPherson", "Ubi", "Kaki Bukit", "Bedok Reservoir", 
                "Tampines East", "Expo"
            ],
            "thomson-east-coast": [
                "Woodlands South", "Springleaf", "Lentor", "Mayflower", "Bright Hill", "Upper Thomson", "Caldecott"
            ]
        }

        # Remove duplicates and flatten the list
        unique_stations = set()
        for line_stations in lines.values():
            unique_stations.update(line_stations)
        
        return list(unique_stations)

    def parse(self, response):
        if 'stellarlifestyle' in response.url:
            return self.parse_stellarlifestyle(response)
        elif 'sbstransit' in response.url:
            return self.parse_sbstransit(response)

    def parse_stellarlifestyle(self, response):
        for station in self.station_names:
            yield scrapy.FormRequest(
                url='https://stellarlifestyle.com.sg/shop-directory',
                formdata={'search_shop_station': station},
                callback=self.parse_stellar_station,
                meta={'station': station, 'source': 'stellarlifestyle'}
            )

    def parse_sbstransit(self, response):
        # Logic to parse the sbstransit website
        for station in self.station_names:
            yield scrapy.Request(
                url=f'https://www.sbstransit.com.sg/Service/Shop?station={station}',
                callback=self.parse_sbs_station,
                meta={'station': station, 'source': 'sbstransit'}
            )

    def parse_stellar_station(self, response):
        station = response.meta['station']
        source = response.meta['source']
        options = response.css('h3.gb-headline.gb-headline-d819c2b1.gb-headline-text::text').extract()
        self.export_to_csv(station, options, source)

    def parse_sbs_station(self, response):
        station = response.meta['station']
        source = response.meta['source']
        # Extract options based on the structure of the sbstransit website
        options = response.css('td.table shoptable tb-bus tbres tbbreak-app::text').extract()
        self.export_to_csv(station, options, source)

    def export_to_csv(self, station, options, source):
        with open(f'{source}_lifestyle.csv', 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Station', 'Options', 'Source']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if csvfile.tell() == 0:  # Check if the file is empty, write header only once
                writer.writeheader()

            writer.writerow({'Station': station, 'Options': ', '.join(options), 'Source': source})
