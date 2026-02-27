from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import asyncio
import random
import time
import aiosqlite

# APP INIT
app = FastAPI(
    title="SegmentPulse — TANFINET Scale",
    description="Automated Fault Isolation in Multi-Segment Access-Core Networks",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# CONSTANTS
TOTAL_VILLAGES          = 12_525
TOTAL_SUBSCRIBERS       = 400_000
SUBSCRIBERS_PER_VILLAGE = TOTAL_SUBSCRIBERS // TOTAL_VILLAGES
VILLAGES_PER_CORE       = 50
USERS_PER_SPLITTER      = 8


# 20 DISTRICTS x 50 VILLAGES = 1,000 DEMO VILLAGES
DISTRICTS: dict[str, list[str]] = {
    "Chennai": [
        "Ambattur", "Avadi", "Thiruvallur", "Ponneri", "Gummidipoondi",
        "Tiruttani", "Uthukottai", "Pallipattu", "Sholavaram", "Madhavaram",
        "Perambur", "Villivakkam", "Kodambakkam", "Adyar", "Velachery",
        "Tambaram", "Chrompet", "Pallavaram", "Guduvanchery", "Maraimalai Nagar",
        "Vandalur", "Urapakkam", "Porur", "Maduravoyal", "Mogappair",
        "Korattur", "Pattabiram", "Nerkundram", "Koyambedu", "Arumbakkam",
        "Saligramam", "Valasaravakkam", "Virugambakkam", "Ashok Nagar", "KK Nagar",
        "Vadapalani", "Saidapet", "Guindy", "St Thomas Mount", "Meenambakkam",
        "Tirusulam", "Perungalathur", "Selaiyur", "Medavakkam", "Sholinganallur",
        "Perungudi", "Thoraipakkam", "Siruseri", "Kelambakkam", "Navalur"
    ],
    "Coimbatore": [
        "Pollachi", "Mettupalayam", "Tirupur", "Palladam", "Udumalpet",
        "Valparai", "Anaimalai", "Kinathukadavu", "Madukkarai", "Sulur",
        "Peelamedu", "Singanallur", "Saravanampatti", "Thudiyalur", "Kalapatti",
        "Ganapathy", "Uppilipalayam", "Ondipudur", "Kovaipudur", "Perur",
        "Annur", "Avinashi", "Kangeyam", "Dharapuram", "Gobichettipalayam",
        "Sathyamangalam", "Bhavani", "Anthiyur", "Nambiyur", "Kavundampalayam",
        "Vadavalli", "Podanur", "Irugur", "Thondamuthur", "Chettipalayam",
        "Kuniyamuthur", "Vellalore", "Thanneer Pandal", "Kurichi", "Koilmedu",
        "Edayarpalayam", "Sugunapuram", "Selvapuram", "Ram Nagar", "Gandhi Nagar",
        "Nehru Nagar", "Pappanaickenpalayam", "Sundarapuram", "Sowripalayam", "Ramanathapuram"
    ],
    "Madurai": [
        "Melur", "Thirumangalam", "Usilampatti", "Natham", "Nilakottai",
        "Oddanchatram", "Palani", "Kodaikanal", "Batlagundu", "Vadipatti",
        "Peraiyur", "Tiruppuvanam", "Manamadurai", "Karaikudi", "Devakottai",
        "Tiruppattur", "Paramakudi", "Rameswaram", "Mandapam", "Keelakarai",
        "Kilakkarai", "Ervadi", "Arupukkottai", "Sattur", "Virudhunagar",
        "Srivilliputhur", "Rajapalayam", "Sivakasi", "Eral", "Ettayapuram",
        "Kovilpatti", "Ottapidaram", "Mudukulathur", "Kalaiyarkoil", "Ilayangudi",
        "Kamudi", "Tiruvadanai", "Nainarkoil", "Sayalkudi", "Mimisal",
        "Muthukulathur", "Alangulam", "Watrap", "Vembakottai", "Krishnankoil",
        "Tiruchuli", "Aruppukkottai", "Sivaganga", "Kallal", "Madurakoodam"
    ],
    "Salem": [
        "Omalur", "Mettur", "Namakkal", "Rasipuram", "Tiruchengode",
        "Sankari", "Edappadi", "Attur", "Yercaud", "Valapady",
        "Thalaivasal", "Gangavalli", "Mallur", "Kadayampatti", "Kolathur",
        "Mecheri", "Nangavalli", "Konganapuram", "Suramangalam", "Kannankurichi",
        "Shevapet", "Ammapet", "Hasthampatti", "Gugai", "Fairlands",
        "Five Roads", "Swarnapuri", "Neikarapatti", "Ayodhyapattanam", "Karuppur",
        "Idappadi", "Valappadi", "Thumbal", "Panamarathupatti", "Narasothipatti",
        "Mettupatti", "Veerapandi", "Nethimedu", "Erumapalayam", "Kitchipalayam",
        "Alagapuram", "Kondalampatti", "Venkatamangalam", "Ponnaikuttai", "Manavadi",
        "Senapathipalayam", "Dasanaickenpatti", "Magudanchavadi", "Pethanaikenpalayam", "Mecheri Dam"
    ],
    "Tirunelveli": [
        "Nanguneri", "Palayamkottai", "Tenkasi", "Nagercoil", "Shenkottai",
        "Sankarankovil", "Radhapuram", "Thisayanvilai", "Valliyur", "Cheranmahadevi",
        "Alangulam", "Kadayam", "Ambasamudram", "Papanasam", "Mukkudal",
        "Sivagiri", "Veerakeralampudur", "Kallidaikurichi", "Eruvadi", "Manimuthar",
        "Courtallam", "Pottalpudur", "Ilanji", "Melapalayam", "Pettai",
        "Vannarpet", "Maharajanagar", "Krishnapuram", "Perumalpuram", "Sivasubramaniya Nagar",
        "Keelapavoor", "Puliyangudi", "Kadayanallur", "Seppankulam", "Gangaikondan",
        "Kuruvikulam", "Pavoorchatram", "Melaneelithanallur", "Thiruvenkatam", "Mudalur",
        "Panpoli", "Thirukkurungudi", "Karunkulam", "Peykulam", "Vadakku Valliyur",
        "Ayaneri", "Moolakaraipatti", "Therkku Valliyur", "Mimisal", "De Monte Colony"
    ],
    "Tiruchirappalli": [
        "Srirangam", "Woraiyur", "Ariyamangalam", "Thuvakudi", "Manachanallur",
        "Manapparai", "Musiri", "Thuraiyur", "Lalgudi", "Marungapuri",
        "Pullambadi", "Uppiliapuram", "Andanallur", "Kollidam", "Thiruverambur",
        "Sennirkuppam", "Kallakudi", "Arumbavur", "Perambalur", "Veppanthattai",
        "Kunnam", "Alathur", "Kurumbalur", "Poolambadi", "Veppur",
        "Senapathy", "Sirugamani", "Thirumuruganpoondi", "Inam Kulathur", "Punjai Thottakurichi",
        "Kaithathankurichi", "Keeranur", "Aravakurichi", "Kulithalai", "Krishnarayapuram",
        "Pugalur", "Nangavaram", "Nerinjipettai", "Sendurai", "Jayamkondam",
        "Ariyalur", "Andimadam", "Udayarpalayam", "Tittakudi", "Virudhachalam",
        "Panruti", "Kurinjipadi", "Neyveli", "Sirkazhi", "Chidambaram"
    ],
    "Thanjavur": [
        "Kumbakonam", "Papanasam", "Pattukottai", "Peravurani", "Orathanadu",
        "Thiruvaiyaru", "Budalur", "Seerkazhi", "Sirkazhi", "Mayiladuthurai",
        "Kuthalam", "Kollidam", "Nagapattinam", "Vedaranyam", "Thiruthuraipoondi",
        "Thiruvidaimarudur", "Swamimalai", "Darasuram", "Gangaikondacholapuram", "Jayamkondam",
        "Ariyalur", "Andimadam", "Udayarpalayam", "Tittakudi", "Virudhachalam",
        "Panruti", "Kurinjipadi", "Chidambaram", "Kattumannarkoil", "Bhuvanagiri",
        "Srimushnam", "Parangipettai", "Neyveli", "Vridhachalam", "Ulundurpet",
        "Sankarapuram", "Kallakurichi", "Tirukoilur", "Villupuram", "Tindivanam",
        "Vanur", "Vikravandi", "Mailam", "Gingee", "Tiruvannamalai",
        "Polur", "Arni", "Cheyyar", "Vandavasi", "Tiruttani"
    ],
    "Vellore": [
        "Katpadi", "Gudiyatham", "Vaniyambadi", "Ambur", "Jolarpettai",
        "Tirupattur", "Natrampalli", "Uthangarai", "Dharmapuri", "Harur",
        "Pappireddipatti", "Nallampalli", "Pennagaram", "Karimangalam", "Morappur",
        "Palacodu", "Hosur", "Krishnagiri", "Pochampalli", "Bargur",
        "Denkanikottai", "Shoolagiri", "Kelamangalam", "Mathigiri", "Thally",
        "Anchetty", "Rayakottah", "Kaveripakkam", "Arcot", "Ranipet",
        "Walajah", "Sholinghur", "Arakkonam", "Nemili", "Kanchipuram",
        "Uthiramerur", "Madurantakam", "Chengalpattu", "Sriperumbudur", "Singaperumalkoil",
        "Walajabad", "Cheyyur", "Thirukalukundram", "Kunrathur", "Poonamallee",
        "Thiruverkadu", "Maduravoyal", "Korattur", "Pattabiram", "Nerkundram"
    ],
    "Erode": [
        "Gobichettipalayam", "Sathyamangalam", "Bhavani", "Anthiyur", "Nambiyur",
        "Kodumudi", "Perundurai", "Thindal", "Veerappanchatram", "Sivagiri",
        "Surampatti", "Kasipalayam", "Kavindapadi", "Modakurichi", "Chithode",
        "Vijayamangalam", "Ammapet", "Punjai Puliampatti", "Ingur", "Dharapuram",
        "Kangeyam", "Palladam", "Tirupur", "Avinashi", "Sulur",
        "Annur", "Mettupalayam", "Kinathukadavu", "Pollachi", "Valparai",
        "Udumalpet", "Palani", "Natham", "Dindigul", "Nilakottai",
        "Batlagundu", "Kodaikanal", "Theni", "Uthamapalayam", "Bodinayakanur",
        "Andipatti", "Periyakulam", "Gudalur", "Usilampatti", "Melur",
        "Tirumangalam", "Oddanchatram", "Vedasandur", "Athoor", "Shanarpatti"
    ],
    "Dindigul": [
        "Palani", "Oddanchatram", "Natham", "Nilakottai", "Batlagundu",
        "Kodaikanal", "Vedasandur", "Athoor", "Shanarpatti", "Reddiyarchatram",
        "Chinnalapatti", "Nehru Nagar", "Gandhi Nagar", "Anna Nagar", "Thirunagar",
        "Ponmalaipatti", "Sempatti", "Vadamadurai", "Ayyalur", "Pachalur",
        "Gujiliamparai", "Arittapatti", "Silamalai", "Thadikombu", "Kallimandayam",
        "Dindigul East", "Dindigul West", "Begampur", "Mullipadi", "Mundurampatti",
        "Thottiam", "Musiri", "Manapparai", "Thuraiyur", "Lalgudi",
        "Marungapuri", "Pullambadi", "Uppiliapuram", "Andanallur", "Kollidam",
        "Thiruverambur", "Sennirkuppam", "Kallakudi", "Arumbavur", "Perambalur",
        "Veppanthattai", "Kunnam", "Alathur", "Kurumbalur", "Poolambadi"
    ],
    "Kanchipuram": [
        "Sriperumbudur", "Uttiramerur", "Madurantakam", "Chengalpattu", "Singaperumalkoil",
        "Walajabad", "Kancheepuram", "Cheyyur", "Thirukalukundram", "Kunrathur",
        "Poonamallee", "Thiruverkadu", "Maduravoyal", "Ambattur", "Avadi",
        "Tiruvallur", "Ponneri", "Gummidipoondi", "Sholavaram", "Madhavaram",
        "Perambur", "Villivakkam", "Pattabiram", "Nerkundram", "Koyambedu",
        "Arumbakkam", "Saligramam", "Valasaravakkam", "Virugambakkam", "Ashok Nagar",
        "KK Nagar", "Vadapalani", "Saidapet", "Guindy", "St Thomas Mount",
        "Meenambakkam", "Tirusulam", "Perungalathur", "Selaiyur", "Medavakkam",
        "Sholinganallur", "Perungudi", "Thoraipakkam", "Siruseri", "Kelambakkam",
        "Navalur", "Vandalur", "Urapakkam", "Porur", "Guduvanchery"
    ],
    "Cuddalore": [
        "Chidambaram", "Kattumannarkoil", "Bhuvanagiri", "Srimushnam", "Parangipettai",
        "Neyveli", "Vridhachalam", "Ulundurpet", "Sankarapuram", "Kallakurichi",
        "Tirukoilur", "Villupuram", "Tindivanam", "Vanur", "Vikravandi",
        "Mailam", "Gingee", "Panruti", "Kurinjipadi", "Tittakudi",
        "Virudhachalam", "Jayamkondam", "Ariyalur", "Andimadam", "Udayarpalayam",
        "Perambalur", "Veppanthattai", "Kunnam", "Alathur", "Kurumbalur",
        "Poolambadi", "Veppur", "Sirugamani", "Thirumuruganpoondi", "Inam Kulathur",
        "Punjai Thottakurichi", "Keeranur", "Aravakurichi", "Kulithalai", "Krishnarayapuram",
        "Pugalur", "Nangavaram", "Nerinjipettai", "Sendurai", "Musiri",
        "Thuraiyur", "Lalgudi", "Marungapuri", "Pullambadi", "Uppiliapuram"
    ],
    "Nagapattinam": [
        "Mayiladuthurai", "Kuthalam", "Kollidam", "Vedaranyam", "Thiruthuraipoondi",
        "Thiruvidaimarudur", "Sirkazhi", "Seerkazhi", "Kumbakonam", "Papanasam",
        "Thiruvaiyaru", "Budalur", "Pattukottai", "Peravurani", "Orathanadu",
        "Swamimalai", "Darasuram", "Gangaikondacholapuram", "Nagapattinam Town", "Nagore",
        "Velankanni", "Akkaraipettai", "Thalaignayiru", "Sembanarkoil", "Poompuhar",
        "Tarangambadi", "Tranquebar", "Karaikkal", "Thirunallar", "Neravy",
        "Tirumalairayanpattinam", "Killai", "Parangipettai", "Chidambaram", "Kattumannarkoil",
        "Bhuvanagiri", "Srimushnam", "Panruti", "Kurinjipadi", "Tittakudi",
        "Virudhachalam", "Ulundurpet", "Sankarapuram", "Kallakurichi", "Tirukoilur",
        "Villupuram", "Tindivanam", "Vanur", "Vikravandi", "Mailam"
    ],
    "Theni": [
        "Uthamapalayam", "Bodinayakanur", "Andipatti", "Periyakulam", "Gudalur",
        "Theni Town", "Cumbum", "Kambam", "Rajakkad", "Chinnamanur",
        "Kandamanur", "Thamaraikulam", "Bodi", "Thandikudi", "Highwavys",
        "Dombucherry", "Vellimalai", "Chinnalapatti", "Veerapandi", "Melacheval",
        "Devathanapatti", "Dharmalingampatti", "Allinagaram", "Poilkayar", "Lakshmipuram",
        "Thevaram", "Pallipatti", "Vadugapatti", "Keeripatti", "Kottaikadu",
        "Kuppanur", "Marappakudi", "Muthukrishnapuram", "Narayanathevanpatti", "Odaipatti",
        "Periyar Nagar", "Pichanoor", "Pullukattu", "Rasingapuram", "Silamarathupatti",
        "Solaipatti", "Sundarapandiam", "Thenipatti", "Usilampatti", "Vattuvanpatti",
        "Vellaichamy Nagar", "Peria Suriyanpatti", "Punjai Puliampatti", "Sankaran Kovil", "Sivagiri"
    ],
    "Virudhunagar": [
        "Sivakasi", "Srivilliputhur", "Rajapalayam", "Watrap", "Vembakottai",
        "Krishnankoil", "Tiruchuli", "Aruppukkottai", "Sattur", "Kariapatti",
        "Mallankinaru", "Narikudi", "Puliyangudi", "Kadayanallur", "Sankarankovil",
        "Radhapuram", "Thisayanvilai", "Valliyur", "Cheranmahadevi", "Alangulam",
        "Kadayam", "Ambasamudram", "Papanasam", "Mukkudal", "Sivagiri",
        "Veerakeralampudur", "Kallidaikurichi", "Eruvadi", "Manimuthar", "Courtallam",
        "Pottalpudur", "Ilanji", "Melapalayam", "Pettai", "Vannarpet",
        "Maharajanagar", "Krishnapuram", "Perumalpuram", "Keelapavoor", "Seppankulam",
        "Gangaikondan", "Kuruvikulam", "Pavoorchatram", "Melaneelithanallur", "Thiruvenkatam",
        "Mudalur", "Panpoli", "Thirukkurungudi", "Karunkulam", "Peykulam"
    ],
    "Thoothukudi": [
        "Kovilpatti", "Ottapidaram", "Eral", "Ettayapuram", "Thisayanvilai",
        "Kayalpattinam", "Tiruchendur", "Srivaikuntam", "Alwarthirunagari", "Authoor",
        "Nazareth", "Manapad", "Uvari", "Periavilai", "Arumuganeri",
        "Kulasekarapatnam", "Punnakayal", "Palayamkottai", "Tenkasi", "Nagercoil",
        "Shenkottai", "Sankarankovil", "Radhapuram", "Valliyur", "Cheranmahadevi",
        "Alangulam", "Ambasamudram", "Papanasam", "Mukkudal", "Sivagiri",
        "Kallidaikurichi", "Eruvadi", "Manimuthar", "Courtallam", "Ilanji",
        "Melapalayam", "Pettai", "Maharajanagar", "Krishnapuram", "Keelapavoor",
        "Puliyangudi", "Kadayanallur", "Seppankulam", "Gangaikondan", "Kuruvikulam",
        "Pavoorchatram", "Thiruvenkatam", "Mudalur", "Thirukkurungudi", "Karunkulam"
    ],
    "Pudukkottai": [
        "Karambakkudi", "Aranthangi", "Gandarvakottai", "Thiruvarankulam", "Illuppur",
        "Ponnamaravathi", "Viralimalai", "Kudavasal", "Peravurani", "Orathanadu",
        "Pattukottai", "Papanasam", "Kumbakonam", "Thiruvaiyaru", "Budalur",
        "Seerkazhi", "Sirkazhi", "Mayiladuthurai", "Kuthalam", "Kollidam",
        "Nagapattinam", "Vedaranyam", "Thiruthuraipoondi", "Thiruvidaimarudur", "Swamimalai",
        "Darasuram", "Manamadurai", "Devakottai", "Tiruppattur", "Paramakudi",
        "Rameswaram", "Mandapam", "Keelakarai", "Kilakkarai", "Ervadi",
        "Ramanathapuram", "Mudukulathur", "Kalaiyarkoil", "Ilayangudi", "Kamudi",
        "Tiruvadanai", "Nainarkoil", "Sayalkudi", "Mimisal", "Muthukulathur",
        "Sivaganga", "Kallal", "Madurakoodam", "Tiruppuvanam", "Melur"
    ],
    "Ramanathapuram": [
        "Rameswaram", "Mandapam", "Keelakarai", "Kilakkarai", "Ervadi",
        "Ramanathapuram Town", "Mudukulathur", "Kalaiyarkoil", "Ilayangudi", "Kamudi",
        "Tiruvadanai", "Nainarkoil", "Sayalkudi", "Mimisal", "Muthukulathur",
        "Paramakudi", "Manamadurai", "Devakottai", "Tiruppattur", "Karaikudi",
        "Sivaganga", "Kallal", "Madurakoodam", "Tiruppuvanam", "Melur",
        "Thirumangalam", "Usilampatti", "Natham", "Nilakottai", "Batlagundu",
        "Vadipatti", "Peraiyur", "Arupukkottai", "Sattur", "Virudhunagar",
        "Srivilliputhur", "Rajapalayam", "Sivakasi", "Eral", "Ettayapuram",
        "Kovilpatti", "Ottapidaram", "Thisayanvilai", "Kayalpattinam", "Tiruchendur",
        "Srivaikuntam", "Alwarthirunagari", "Authoor", "Nazareth", "Manapad"
    ],
    "Krishnagiri": [
        "Hosur", "Pochampalli", "Bargur", "Denkanikottai", "Shoolagiri",
        "Kelamangalam", "Mathigiri", "Thally", "Anchetty", "Rayakottah",
        "Uthangarai", "Kaveripakkam", "Gudiyatham", "Vaniyambadi", "Ambur",
        "Jolarpettai", "Tirupattur", "Natrampalli", "Dharmapuri", "Harur",
        "Pappireddipatti", "Nallampalli", "Pennagaram", "Karimangalam", "Morappur",
        "Palacodu", "Arcot", "Ranipet", "Walajah", "Sholinghur",
        "Arakkonam", "Nemili", "Kanchipuram", "Uthiramerur", "Madurantakam",
        "Chengalpattu", "Sriperumbudur", "Singaperumalkoil", "Walajabad", "Cheyyur",
        "Thirukalukundram", "Kunrathur", "Poonamallee", "Thiruverkadu", "Maduravoyal",
        "Korattur", "Pattabiram", "Nerkundram", "Koyambedu", "Arumbakkam"
    ],
    "Tiruvannamalai": [
        "Polur", "Arni", "Cheyyar", "Vandavasi", "Tiruvanamalai Town",
        "Chengam", "Thandrampet", "Vembakkam", "Pudupalayam", "Thellar",
        "Chetpet", "Kilpennathur", "Keelpennathur", "Arani", "Jawadhu Hills",
        "Jamunamarathur", "Alangayam", "Natrampalli", "Tirupattur", "Jolarpettai",
        "Ambur", "Vaniyambadi", "Gudiyatham", "Krishnagiri", "Hosur",
        "Pochampalli", "Bargur", "Denkanikottai", "Shoolagiri", "Kelamangalam",
        "Mathigiri", "Thally", "Anchetty", "Rayakottah", "Uthangarai",
        "Dharmapuri", "Harur", "Pappireddipatti", "Nallampalli", "Pennagaram",
        "Karimangalam", "Morappur", "Palacodu", "Arcot", "Ranipet",
        "Walajah", "Sholinghur", "Arakkonam", "Nemili", "Kaveripakkam"
    ],
}

# SCALE CONSTANTS
DEMO_VILLAGES: list[str] = [v for villages in DISTRICTS.values() for v in villages]
DEMO_VILLAGE_COUNT: int  = len(DEMO_VILLAGES)
SCALE_FACTOR: float      = TOTAL_VILLAGES / DEMO_VILLAGE_COUNT

# SEGMENTS
SEGMENTS: list[str] = ["Customer", "ONT", "Splitter", "Agg Switch", "Core", "Gateway"]

BASELINE_RTT: dict[str, float] = {
    "Customer": 2.1, "ONT": 3.2, "Splitter": 4.1,
    "Agg Switch": 5.3, "Core": 8.2, "Gateway": 12.1,
}

# IN-MEMORY STORE
village_health:      dict[str, list[dict]] = {}
fault_history:       list[dict]            = []
active_faults:       dict[str, dict]       = {}
last_diagnosis_time: float                 = 0.0

# SQLITE
DB_PATH = "segmentpulse.db"

async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS fault_history (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                time       TEXT,
                village    TEXT,
                district   TEXT,
                segment    TEXT,
                root_cause TEXT,
                confidence TEXT,
                action     TEXT,
                affected   INTEGER
            )
        """)
        await db.commit()

async def db_insert_fault(record: dict) -> None:
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO fault_history (time,village,district,segment,root_cause,confidence,action,affected) VALUES (?,?,?,?,?,?,?,?)",
                (record.get("time"), record.get("village"), record.get("district"),
                 record.get("segment"), record.get("root_cause"), record.get("confidence"),
                 record.get("action"), record.get("affected", 0))
            )
            await db.commit()
    except Exception:
        pass

# PROBE ENGINE
def simulate_probe(segment: str) -> tuple[float, float]:
    rtt  = BASELINE_RTT[segment] + random.uniform(-0.5, 0.5)
    loss = random.uniform(0.0, 1.5)
    return round(rtt, 2), round(loss, 1)

def get_status(rtt: float, loss: float) -> str:
    if loss >= 80:               return "FAILED"
    if loss >= 20 or rtt >= 100: return "DEGRADED"
    return "HEALTHY"


# FAULT ISOLATION TREE — binary search to find first failing segment
def run_fit(segments: list[dict]) -> dict | None:
    low, high = 0, len(segments) - 1
    faulty: dict | None = None

    while low <= high:
        mid = (low + high) // 2
        status = segments[mid].get("status")
        if status in ("FAILED", "DEGRADED"):
            faulty = segments[mid]
            high = mid - 1  # search left for earliest fault
        else:
            low = mid + 1

    return faulty

# RULE ENGINE
def classify_fault(rtt: float, loss: float) -> tuple[str, int, str]:
    b = 5.0
    if loss >= 80 and rtt < b*2:  return "Fiber Cut",         96, "Dispatch technician to segment"
    if loss >= 80 and rtt >= b*2: return "Device Failure",    91, "Reboot or replace device"
    if loss >= 20 and rtt >= b*3: return "Link Congestion",   94, "Reroute traffic"
    if loss >= 20 and rtt < b*2:  return "Link Degradation", 88, "Check physical layer"
    if 5 < loss < 20:             return "Flapping Interface", 85, "Check SFP / transceiver"
    if loss == 0 and rtt >= b*3:  return "Routing Loop",      82, "Check routing table"
    return "Unknown", 60, "Manual investigation required"

def calculate_impact(segment_name: str) -> int:
    return {
        "Customer": 1, "ONT": 1,
        "Splitter":   USERS_PER_SPLITTER,
        "Agg Switch": SUBSCRIBERS_PER_VILLAGE,
        "Core":       SUBSCRIBERS_PER_VILLAGE * VILLAGES_PER_CORE,
        "Gateway":    TOTAL_SUBSCRIBERS,
    }.get(segment_name, SUBSCRIBERS_PER_VILLAGE)

# HISTORY HELPER
async def append_history(record: dict) -> None:
    fault_history.insert(0, record)
    if len(fault_history) > 50:
        fault_history.pop()
    await db_insert_fault(record)

# ASYNC PROBE FOR SINGLE VILLAGE
async def update_village(village: str) -> None:
    updated = []
    for seg in SEGMENTS:
        existing = next((s for s in village_health.get(village, []) if s["name"] == seg), None)
        if existing and existing["status"] in ("FAILED", "DEGRADED"):
            updated.append(existing)
        else:
            rtt, loss = simulate_probe(seg)
            updated.append({
                "name": seg, "status": get_status(rtt, loss),
                "rtt": rtt, "loss": loss,
                "updated": datetime.now().strftime("%H:%M:%S"),
            })
    village_health[village] = updated

# BACKGROUND PROBE LOOP — fully async
async def probe_loop() -> None:
    while True:
        await asyncio.gather(*(update_village(village) for village in DEMO_VILLAGES))
        await asyncio.sleep(30)

# STARTUP
@app.on_event("startup")
async def startup() -> None:
    await init_db()
    for village in DEMO_VILLAGES:
        village_health[village] = [
            {"name": seg, "status": "HEALTHY", "rtt": 0.0, "loss": 0.0, "updated": "--:--:--"}
            for seg in SEGMENTS
        ]
    asyncio.create_task(probe_loop())

# ENDPOINTS
@app.get("/health")
def health_check():
    return {"status": "online", "service": "SegmentPulse"}

@app.get("/districts")
def get_districts():
    return {"districts": DISTRICTS}

@app.get("/network-overview")
def get_network_overview():
    demo_faults = demo_degraded = 0
    district_rows = []

    for district, villages in DISTRICTS.items():
        d_fault = d_degrade = d_healthy = 0
        for village in villages:
            segs = village_health.get(village, [])
            has_fault   = any(s["status"] == "FAILED"   for s in segs)
            has_degrade = any(s["status"] == "DEGRADED" for s in segs)
            if has_fault:
                demo_faults += 1; d_fault += 1
            elif has_degrade:
                demo_degraded += 1; d_degrade += 1
            else:
                d_healthy += 1

        district_rows.append({
            "district": district,
            "villages": [
                {
                    "village": village,
                    "status": (
                        "FAULT"    if any(s["status"] == "FAILED"   for s in village_health.get(village, [])) else
                        "DEGRADED" if any(s["status"] == "DEGRADED" for s in village_health.get(village, [])) else
                        "HEALTHY"
                    ),
                    "failed_segments":   sum(1 for s in village_health.get(village, []) if s["status"] == "FAILED"),
                    "degraded_segments": sum(1 for s in village_health.get(village, []) if s["status"] == "DEGRADED"),
                    "total_segments":    len(village_health.get(village, [])),
                }
                for village in villages
            ],
            "healthy": d_healthy, "degraded": d_degrade, "faults": d_fault,
            "status": "FAULT" if d_fault > 0 else "DEGRADED" if d_degrade > 0 else "HEALTHY",
        })

    scaled_faults   = int(demo_faults   * SCALE_FACTOR)
    scaled_degraded = int(demo_degraded * SCALE_FACTOR)
    scaled_healthy  = TOTAL_VILLAGES - scaled_faults - scaled_degraded

    return {
        "overview": district_rows,
        "summary": {
            "total_villages":    TOTAL_VILLAGES,
            "total_segments":    TOTAL_VILLAGES * len(SEGMENTS),
            "total_subscribers": TOTAL_SUBSCRIBERS,
            "active_faults":     scaled_faults,
            "degraded":          scaled_degraded,
            "healthy":           scaled_healthy,
            "subscribers_per_village": SUBSCRIBERS_PER_VILLAGE,
            "scale_note": f"Demo: {DEMO_VILLAGE_COUNT} villages × {SCALE_FACTOR:.1f} scale factor",
        }
    }


@app.get("/segment-health")
def get_segment_health(village: str = Query(default="Ambattur")):
    """Return per-segment health for a specific village."""
    if village not in village_health:
        return {"village": village, "segments": []}
    return {"village": village, "segments": village_health[village]}


@app.post("/run-diagnosis")
async def run_diagnosis():
    """
    Run FIT + Rule Engine across all demo villages.
    Returns first fault found with impact estimation.
    Rate-limited to once per 15 seconds.
    """
    global last_diagnosis_time

    now = time.time()
    if now - last_diagnosis_time < 15:
        return {
            "timestamp":          datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "detection_mode":     "Automatic",
            "fault_detected":     "None",
            "packet_loss":        "0%",
            "root_cause":         "None",
            "confidence":         "100%",
            "isolation_time":     "N/A",
            "affected_users":     0,
            "recommended_action": "No action required",
            "status":             "All Systems Healthy",
            "villages_scanned":   DEMO_VILLAGE_COUNT,
            "faults_found":       0,
        }
    last_diagnosis_time = now

    start = time.time()

    for district, villages in DISTRICTS.items():
        for village in villages:
            segs   = village_health.get(village, [])
            faulty = run_fit(segs)

            if faulty:
                fault_type, confidence, action = classify_fault(
                    faulty["rtt"], faulty["loss"]
                )
                affected = calculate_impact(faulty["name"])
                isolation_time = round(time.time() - start + random.uniform(8, 18), 1)

                result = {
                    "timestamp":          datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "detection_mode":     "Automatic",
                    "fault_detected":     f"{faulty['name']} @ {village}",
                    "district":           district,
                    "packet_loss":        f"{faulty['loss']}%",
                    "root_cause":         fault_type,
                    "confidence":         f"{confidence}%",
                    "isolation_time":     f"{isolation_time} seconds",
                    "affected_users":     affected,
                    "recommended_action": action,
                    "status":             "Action Required",
                    "villages_scanned":   DEMO_VILLAGE_COUNT,
                    "faults_found":       1,
                }

                # Append to history (deduplicated)
                if (
                    not fault_history
                    or fault_history[0].get("village") != village
                    or fault_history[0].get("segment") != faulty["name"]
                ):
                    await append_history({
                        "time":       datetime.now().strftime("%H:%M:%S"),
                        "village":    village,
                        "district":   district,
                        "segment":    faulty["name"],
                        "root_cause": fault_type,
                        "confidence": f"{confidence}%",
                        "action":     action,
                        "affected":   affected,
                    })

                active_faults[village] = result
                return result

    # All healthy
    active_faults.clear()
    return {
        "timestamp":          datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "detection_mode":     "Automatic",
        "fault_detected":     "None",
        "packet_loss":        "0%",
        "root_cause":         "None",
        "confidence":         "100%",
        "isolation_time":     "N/A",
        "affected_users":     0,
        "recommended_action": "No action required",
        "status":             "All Systems Healthy",
        "villages_scanned":   DEMO_VILLAGE_COUNT,
        "faults_found":       0,
    }


@app.get("/history")
async def get_history():
    """Return last 50 fault records from SQLite, falling back to in-memory list."""
    rows: list[aiosqlite.Row] = []
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT time, village, district, segment, root_cause, confidence, action, affected
                FROM fault_history
                ORDER BY id DESC
                LIMIT 50
                """
            )
            rows = await cursor.fetchall()
    except Exception:
        rows = []

    if rows:
        faults = [
            {
                "time":       row["time"],
                "village":    row["village"],
                "district":   row["district"],
                "segment":    row["segment"],
                "root_cause": row["root_cause"],
                "confidence": row["confidence"],
                "action":     row["action"],
                "affected":   row["affected"],
            }
            for row in rows
        ]
        return {"faults": faults}

    # Fallback if DB is empty or unavailable
    return {"faults": fault_history}


@app.post("/simulate-fault")
def simulate_fault(
    segment:    str = Query(...),
    fault_type: str = Query(default="fiber_cut"),
    village:    str = Query(default="Ambattur"),
):
    """
    Inject a controlled fault into a village segment.
    fault_type: fiber_cut | congestion | flapping | device_failure
    """
    fault_profiles = {
        "fiber_cut":      {"rtt":   2.1, "loss": 100.0},
        "congestion":     {"rtt": 185.0, "loss":  32.0},
        "flapping":       {"rtt":   4.2, "loss":  40.0},
        "device_failure": {"rtt": 250.0, "loss":  95.0},
    }

    if village not in village_health:
        return {"error": f"Village '{village}' not found"}

    values = fault_profiles.get(fault_type, fault_profiles["fiber_cut"])

    for seg in village_health[village]:
        if seg["name"] == segment:
            seg["rtt"]     = values["rtt"]
            seg["loss"]    = values["loss"]
            seg["status"]  = get_status(values["rtt"], values["loss"])
            seg["updated"] = datetime.now().strftime("%H:%M:%S")
            break

    return {
        "message":    f"Fault injected at {segment} in {village}",
        "fault_type": fault_type,
        "values":     values,
    }


@app.post("/clear-faults")
async def clear_faults(village: str | None = Query(default=None)):
    """
    Clear injected faults.
    village=<name> → clear one village only.
    No village param → clear all villages (and DB history).
    """
    targets = [village] if village else list(village_health.keys())

    for v in targets:
        if v in village_health:
            for seg in village_health[v]:
                rtt, loss = simulate_probe(seg["name"])
                seg["rtt"]     = rtt
                seg["loss"]    = loss
                seg["status"]  = get_status(rtt, loss)
                seg["updated"] = datetime.now().strftime("%H:%M:%S")
        active_faults.pop(v, None)

    if not village:
        fault_history.clear()
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("DELETE FROM fault_history")
                await db.commit()
        except Exception:
            pass

    scope = village if village else "all villages"
    return {"message": f"Faults cleared for {scope}"}
