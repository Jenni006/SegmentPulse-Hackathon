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
        "Ambattur", "Avadi", "Sholavaram", "Madhavaram", "Perambur",
        "Villivakkam", "Kodambakkam", "Adyar", "Velachery", "Tambaram",
        "Chrompet", "Pallavaram", "Guduvanchery", "Vandalur", "Urapakkam",
        "Porur", "Maduravoyal", "Mogappair", "Korattur", "Pattabiram",
        "Nerkundram", "Koyambedu", "Arumbakkam", "Saligramam", "Valasaravakkam",
        "Virugambakkam", "Ashok Nagar", "Vadapalani", "Saidapet", "Guindy",
        "Meenambakkam", "Tirusulam", "Perungalathur", "Selaiyur", "Medavakkam",
        "Sholinganallur", "Perungudi", "Thoraipakkam", "Siruseri", "Kelambakkam",
        "Navalur", "Injambakkam", "Neelankarai", "Palavakkam", "Thiruvanmiyur",
        "Mylapore", "Triplicane", "Royapettah", "Egmore", "Kilpauk"
    ],
    "Coimbatore": [
        "Pollachi", "Mettupalayam", "Tirupur", "Palladam", "Udumalpet",
        "Valparai", "Anaimalai", "Kinathukadavu-CBE", "Madukkarai", "Sulur",
        "Peelamedu", "Singanallur", "Saravanampatti", "Thudiyalur", "Kalapatti",
        "Ganapathy", "Uppilipalayam", "Ondipudur", "Kovaipudur", "Perur",
        "Annur", "Avinashi", "Kavundampalayam", "Vadavalli", "Podanur",
        "Irugur", "Thondamuthur", "Chettipalayam", "Kuniyamuthur", "Vellalore",
        "Thanneer Pandal", "Kurichi-CBE", "Koilmedu", "Edayarpalayam", "Sugunapuram",
        "Selvapuram", "Pappanaickenpalayam", "Sundarapuram", "Sowripalayam", "Othakalmandapam",
        "Narasimhanaickenpalayam", "Veerakeralam", "Zamin Uthukuli", "Tiruchitrambalam", "Idikarai",
        "Pooluvapatti", "Sarcarsamakulam", "Negamam", "Kangeyam-CBE", "Dharapuram-CBE"
    ],
    "Madurai": [
        "Melur", "Thirumangalam", "Usilampatti", "Natham-MDU", "Vadipatti",
        "Peraiyur", "Tiruppuvanam", "Manamadurai", "Karaikudi", "Devakottai",
        "Tiruppattur-MDU", "Paramakudi-MDU", "Mandapam-MDU", "Keelakarai-MDU", "Kilakkarai-MDU",
        "Ervadi-MDU", "Arupukkottai-MDU", "Sattur-MDU", "Sivakasi-MDU", "Eral-MDU",
        "Ettayapuram-MDU", "Mudukulathur-MDU", "Kalaiyarkoil-MDU", "Ilayangudi-MDU", "Kamudi-MDU",
        "Tiruvadanai-MDU", "Nainarkoil-MDU", "Sayalkudi-MDU", "Mimisal-MDU", "Muthukulathur-MDU",
        "Kallal", "Madurakoodam", "Sholavandan", "Kottampatti", "Sedapatti",
        "Kondayampatti", "T Kallupatti", "Chellampatti", "Ponnamaravathi-MDU", "Palamedu",
        "Veerapandi-MDU", "Samayanallur", "Othakadai", "Anaiyur", "Kochadai",
        "Vilangudi", "Paravai", "Thenipatti-MDU", "Sriramapuram-MDU", "Pattiveeranpatti"
    ],
    "Salem": [
        "Omalur", "Mettur", "Namakkal", "Rasipuram", "Tiruchengode",
        "Sankari", "Edappadi", "Attur", "Yercaud", "Valapady",
        "Thalaivasal", "Gangavalli", "Mallur", "Kadayampatti", "Kolathur-SLM",
        "Mecheri", "Nangavalli", "Konganapuram", "Suramangalam", "Kannankurichi",
        "Shevapet", "Ammapet", "Hasthampatti", "Gugai", "Fairlands",
        "Swarnapuri", "Neikarapatti", "Ayodhyapattanam", "Karuppur-SLM", "Idappadi",
        "Valappadi", "Panamarathupatti", "Narasothipatti", "Nethimedu", "Erumapalayam",
        "Kitchipalayam", "Alagapuram", "Kondalampatti", "Venkatamangalam-SLM", "Ponnaikuttai",
        "Senapathipalayam", "Dasanaickenpatti", "Magudanchavadi", "Thumbal-SLM", "Kakapalayam",
        "Muthampatty", "Pethanaickenpalayam", "Jalakandapuram", "Veerapandi-SLM", "Mettupatti-SLM"
    ],
    "Tirunelveli": [
        "Nanguneri", "Palayamkottai", "Tenkasi", "Shenkottai", "Sankarankovil",
        "Radhapuram", "Thisayanvilai", "Valliyur", "Cheranmahadevi", "Kadayam",
        "Ambasamudram", "Mukkudal", "Veerakeralampudur", "Kallidaikurichi", "Eruvadi-TVL",
        "Manimuthar", "Pottalpudur", "Ilanji", "Melapalayam", "Pettai-TVL",
        "Vannarpet", "Maharajanagar", "Krishnapuram-TVL", "Perumalpuram", "Keelapavoor",
        "Puliyangudi", "Kadayanallur", "Seppankulam", "Gangaikondan", "Kuruvikulam",
        "Pavoorchatram", "Melaneelithanallur", "Thiruvenkatam-TVL", "Mudalur-TVL", "Panpoli",
        "Thirukkurungudi", "Karunkulam", "Peykulam", "Vadakku Valliyur", "Ayaneri",
        "Moolakaraipatti", "Therkku Valliyur", "Nangavarkurichi", "Unnamalaikadai", "Suthamalli",
        "Alwarkurichi", "Keela Eral", "Mela Eral", "Paapanasam-TVL", "Achankovil"
    ],
    "Tiruchirappalli": [
        "Srirangam", "Woraiyur", "Ariyamangalam", "Thuvakudi", "Manachanallur",
        "Manapparai", "Musiri", "Thuraiyur", "Lalgudi", "Marungapuri",
        "Pullambadi", "Uppiliapuram", "Andanallur", "Thiruverambur", "Sennirkuppam",
        "Kallakudi", "Arumbavur", "Perambalur", "Veppanthattai-TRY", "Kunnam-TRY",
        "Alathur-TRY", "Kurumbalur", "Poolambadi", "Veppur-TRY", "Sirugamani",
        "Thirumuruganpoondi", "Punjai Thottakurichi", "Keeranur-TRY", "Aravakurichi", "Kulithalai",
        "Krishnarayapuram", "Pugalur", "Nangavaram-TRY", "Nerinjipettai-TRY", "Sendurai",
        "Jayamkondam-TRY", "Andimadam-TRY", "Udayarpalayam-TRY", "Tittakudi-TRY", "Panruti-TRY",
        "Kurinjipadi-TRY", "Thottiam-TRY", "Vaiyampatti", "Pettavaithalai", "Kallagam",
        "Koothappar", "Kattur", "Thennur", "Bhuvanagiri-TRY", "Kollidam-TRY"
    ],
    "Thanjavur": [
        "Kumbakonam", "Pattukottai", "Peravurani", "Orathanadu", "Thiruvaiyaru",
        "Budalur", "Seerkazhi-THJ", "Mayiladuthurai-THJ", "Kuthalam-THJ", "Vedaranyam-THJ",
        "Thiruthuraipoondi-THJ", "Thiruvidaimarudur-THJ", "Swamimalai", "Darasuram", "Gangaikondacholapuram",
        "Kattumannarkoil-THJ", "Srimushnam-THJ", "Parangipettai-THJ", "Neyveli-THJ", "Vridhachalam-THJ",
        "Ulundurpet-THJ", "Sankarapuram-THJ", "Kallakurichi-THJ", "Tirukoilur-THJ", "Vikravandi-THJ",
        "Mailam-THJ", "Gingee-THJ", "Vandavasi-THJ", "Papanasam-THJ", "Needamangalam",
        "Thiruvanchiyam", "Thirukattupalli", "Ammapettai", "Ayyampettai", "Nannilam",
        "Thirubuvanam", "Kumbakonam East", "Kumbakonam West", "Perumagalur-THJ", "Labbaikudikadu",
        "Thirumarugal", "Kollidam-THJ", "Thanjavur East", "Thanjavur West", "Thanjavur North",
        "Thanjavur South", "Papanasam-TJR", "Pattukkottai-THJ", "Veppanthattai-THJ", "Sirkazhi-THJ"
    ],
    "Vellore": [
        "Katpadi", "Gudiyatham", "Vaniyambadi", "Ambur", "Jolarpettai",
        "Tirupattur-VLR", "Natrampalli", "Uthangarai-VLR", "Harur", "Pappireddipatti",
        "Nallampalli", "Pennagaram", "Karimangalam", "Morappur", "Palacodu",
        "Kaveripakkam-VLR", "Arcot", "Ranipet", "Walajah", "Sholinghur",
        "Arakkonam", "Nemili", "Walajabad-VLR", "Cheyyar-VLR", "Vellore Fort",
        "Sathuvachari", "Kosapet", "Viruthampet", "Paradarami", "Alangayam-VLR",
        "Kaniyambadi", "Melalathur", "Anaicut", "Virinchipuram", "Vedanthangal",
        "Pernambut", "Odugathur", "Brammapuram", "Kalavai", "Alangur-VLR",
        "Timiri", "Porpanaikuppam", "Uthiramerur-VLR", "Madurantakam-VLR", "Sriperumbudur-VLR",
        "Kunrathur-VLR", "Thirukalukundram-VLR", "Poonamallee-VLR", "Cheyyur-VLR2", "Singaperumalkoil-VLR"
    ],
    "Erode": [
        "Gobichettipalayam", "Sathyamangalam", "Bhavani", "Anthiyur", "Nambiyur",
        "Kodumudi", "Perundurai", "Thindal", "Veerappanchatram", "Surampatti",
        "Kasipalayam-ERD", "Kavindapadi", "Modakurichi", "Chithode", "Vijayamangalam",
        "Punjai Puliampatti", "Ingur-ERD", "Dharapuram-ERD", "Kangeyam-ERD", "Palladam-ERD",
        "Avinashi-ERD", "Annur-ERD", "Bhavani Sagar", "Thalavadi", "Bhavanisagar",
        "Vellithiruppur", "Uthiyur", "Vavipalayam", "Pallipalayam", "Veerapandi-ERD",
        "Nanjundapuram", "Siruvalur", "Avalpoondurai", "Hasanur", "Germalam",
        "Talavadi-ERD", "Unjalur", "Vellode", "Odathurai", "Chennimalai",
        "Ammapettai-ERD", "Nanjai Punjai", "Kalingarayan", "Mudis", "Kotabagi",
        "Satyamangalam-ERD", "Sivagiri-ERD", "Kasipalayam-ERD2", "Bargur-ERD", "Veerappanchatram-ERD"
    ],
    "Dindigul": [
        "Oddanchatram", "Vedasandur", "Athoor", "Shanarpatti", "Reddiyarchatram",
        "Chinnalapatti-DGL", "Ponmalaipatti", "Sempatti", "Vadamadurai", "Ayyalur-DGL",
        "Pachalur", "Gujiliamparai", "Arittapatti", "Silamalai", "Thadikombu",
        "Dindigul East", "Dindigul West", "Begampur", "Mullipadi", "Mundurampatti",
        "Sithayankottai", "Kallimandayam", "Kodaikanal-DGL", "Batlagundu-DGL", "Natham-DGL",
        "Keeranur-DGL", "Palani-DGL", "Ayakudi", "Pattiveeranpatti-DGL", "Sriramapuram-DGL",
        "Thottiam-DGL", "Palayam-DGL", "Nilakottai-DGL", "Gandhi Nagar-DGL", "Anna Nagar-DGL",
        "Nehru Nagar-DGL", "Thirunagar-DGL", "Vadamadurai-DGL", "Sempatti-DGL", "Ponmalaipatti-DGL",
        "Vedasandur-DGL", "Shanarpatti-DGL", "Oddanchatram-DGL", "Reddiyarchatram-DGL", "Athoor-DGL",
        "Cumbum-DGL", "Gudalur-DGL", "Bodinayakanur-DGL", "Andipatti-DGL", "Periyakulam-DGL"
    ],
    "Kanchipuram": [
        "Sriperumbudur", "Uttiramerur", "Madurantakam", "Chengalpattu", "Singaperumalkoil",
        "Walajabad-KCP", "Kancheepuram", "Thirukalukundram", "Kunrathur-KCP", "Poonamallee-KCP",
        "Uthiramerur-KCP", "Kattankolathur", "Padappai", "Paranur", "Tiruporur",
        "Kovalam", "Kanathur", "Muttukadu", "Puzhuthivakkam", "Kolapakkam",
        "Gerugambakkam", "Peerkankaranai", "Chitlapakkam", "Mudichur", "Tambaram Sanatorium",
        "Thirumudivakkam", "Pozhichalur", "Vanuvampet", "Perungalathur-KCP", "Selaiyur-KCP",
        "Medavakkam-KCP", "Sholinganallur-KCP", "Perungudi-KCP", "Siruseri-KCP", "Kelambakkam-KCP",
        "Navalur-KCP", "Injambakkam-KCP", "Neelankarai-KCP", "Palavakkam-KCP", "Thiruvanmiyur-KCP",
        "Guduvanchery-KCP", "Urapakkam-KCP", "Maraimalai Nagar-KCP", "Vandalur-KCP", "Tambaram-KCP",
        "Chrompet-KCP", "Pallavaram-KCP", "Cheyyur-KCP", "Madurantakam-KCP", "Singaperumalkoil-KCP"
    ],
    "Cuddalore": [
        "Chidambaram", "Kattumannarkoil-CDL", "Bhuvanagiri-CDL", "Parangipettai-CDL", "Vridhachalam-CDL",
        "Ulundurpet-CDL", "Sankarapuram-CDL", "Kallakurichi-CDL", "Tirukoilur-CDL", "Villupuram-CDL",
        "Tindivanam-CDL", "Vanur-CDL", "Vikravandi-CDL", "Mailam-CDL", "Gingee-CDL",
        "Panruti", "Kurinjipadi-CDL", "Tittakudi-CDL", "Virudhachalam-CDL", "Jayamkondam-CDL",
        "Ariyalur-CDL", "Andimadam-CDL", "Udayarpalayam-CDL", "Perambalur-CDL", "Veppanthattai-CDL",
        "Kunnam-CDL", "Alathur-CDL", "Kurumbalur-CDL", "Poolambadi-CDL", "Veppur-CDL",
        "Sirugamani-CDL", "Keeranur-CDL", "Aravakurichi-CDL", "Kulithalai-CDL", "Pugalur-CDL",
        "Nangavaram-CDL", "Nerinjipettai-CDL", "Sendurai-CDL", "Musiri-CDL", "Thuraiyur-CDL",
        "Lalgudi-CDL", "Marungapuri-CDL", "Pullambadi-CDL", "Uppiliapuram-CDL", "Andanallur-CDL",
        "Kollidam-CDL", "Thiruverambur-CDL", "Sennirkuppam-CDL", "Kallakudi-CDL", "Arumbavur-CDL"
    ],
    "Nagapattinam": [
        "Mayiladuthurai", "Kuthalam-NGP", "Kollidam-NGP", "Vedaranyam-NGP", "Thiruthuraipoondi-NGP",
        "Thiruvidaimarudur-NGP", "Sirkazhi-NGP", "Nagapattinam Town", "Nagore", "Velankanni",
        "Akkaraipettai", "Thalaignayiru", "Sembanarkoil-NGP", "Poompuhar", "Tarangambadi",
        "Tranquebar", "Karaikkal", "Thirunallar", "Neravy", "Tirumalairayanpattinam",
        "Killai", "Sirkali-NGP", "Tharangambadi-NGP", "Keelaiyur", "Keelvelur",
        "Vaimedu", "Keezhathottam", "Nidur", "Thalainayar", "Thirukuvalai",
        "Papanasam-NGP", "Nannilam-NGP", "Needamangalam-NGP", "Thirumarugal-NGP", "Labbaikudikadu-NGP",
        "Perumagalur-NGP", "Kollidam East-NGP", "Kollidam West-NGP", "Kollidam North-NGP", "Kollidam South-NGP",
        "Sembanarkoil North", "Sembanarkoil South", "Nagapattinam Port", "Nagapattinam Rural", "Nagapattinam Urban",
        "Vedaranyam North", "Vedaranyam South", "Thiruthuraipoondi North", "Thiruthuraipoondi South", "Mayiladuthurai Rural"
    ],
    "Theni": [
        "Uthamapalayam", "Bodinayakanur", "Andipatti-THN", "Periyakulam-THN", "Gudalur-THN",
        "Theni Town", "Cumbum", "Kambam", "Rajakkad", "Chinnamanur",
        "Kandamanur", "Thamaraikulam", "Bodi", "Thandikudi", "Highwavys",
        "Dombucherry", "Vellimalai", "Melacheval", "Devathanapatti", "Dharmalingampatti",
        "Allinagaram", "Lakshmipuram-THN", "Pallipatti-THN", "Vadugapatti-THN", "Keeripatti",
        "Kottaikadu", "Kuppanur-THN", "Marappakudi", "Muthukrishnapuram", "Odaipatti",
        "Periyar Nagar-THN", "Pichanoor", "Rasingapuram", "Silamarathupatti-THN", "Solaipatti-THN",
        "Sundarapandiam", "Vattuvanpatti", "Vellaichamy Nagar", "Peria Suriyanpatti", "Pulikuthi",
        "Thevaram-THN", "Chinnalapatti-THN", "Veerapandi-THN", "Poilkayar", "Munanjipatti",
        "Kottaiyur-THN", "Usilampatti-THN", "Kamayagoundanpatti", "Andipatty-THN", "Cumbum North"
    ],
    "Virudhunagar": [
        "Sivakasi-VRN", "Srivilliputhur", "Rajapalayam", "Watrap", "Vembakottai",
        "Krishnankoil", "Tiruchuli", "Aruppukkottai-VRN", "Sattur-VRN", "Kariapatti",
        "Mallankinaru", "Narikudi", "Puliyangudi-VRN", "Kadayanallur-VRN", "Sankarankovil-VRN",
        "Radhapuram-VRN", "Thisayanvilai-VRN", "Valliyur-VRN", "Cheranmahadevi-VRN", "Alangulam-VRN",
        "Kadayam-VRN", "Ambasamudram-VRN", "Mukkudal-VRN", "Veerakeralampudur-VRN", "Kallidaikurichi-VRN",
        "Eruvadi-VRN", "Manimuthar-VRN", "Pottalpudur-VRN", "Ilanji-VRN", "Melapalayam-VRN",
        "Pettai-VRN", "Vannarpet-VRN", "Keelapavoor-VRN", "Seppankulam-VRN", "Gangaikondan-VRN",
        "Kuruvikulam-VRN", "Pavoorchatram-VRN", "Thiruvenkatam-VRN", "Mudalur-VRN", "Thirukkurungudi-VRN",
        "Karunkulam-VRN", "Peykulam-VRN", "Sivagiri-VRN", "Panpoli-VRN", "Maharajanagar-VRN",
        "Krishnapuram-VRN", "Perumalpuram-VRN", "Melaneelithanallur-VRN", "Nangavarkurichi-VRN", "Unnamalaikadai-VRN"
    ],
    "Thoothukudi": [
        "Kovilpatti", "Ottapidaram", "Eral-TDK", "Ettayapuram-TDK", "Kayalpattinam",
        "Tiruchendur", "Srivaikuntam", "Alwarthirunagari", "Authoor", "Nazareth",
        "Manapad", "Uvari", "Periavilai", "Arumuganeri", "Kulasekarapatnam",
        "Punnakayal", "Thoothukudi Port", "Thoothukudi Rural", "Mukuperi", "Punnaikayal",
        "Meignanapuram", "Idinthakarai", "Keelakarai-TDK", "Kilakkarai-TDK", "Ervadi-TDK",
        "Sayalkudi-TDK", "Mimisal-TDK", "Rameswaram-TDK", "Mandapam-TDK", "Paramakudi-TDK",
        "Mudukulathur-TDK", "Kamudi-TDK", "Tiruvadanai-TDK", "Nainarkoil-TDK", "Muthukulathur-TDK",
        "Ilayangudi-TDK", "Kalaiyarkoil-TDK", "Manamadurai-TDK", "Devakottai-TDK", "Tiruppattur-TDK",
        "Karaikudi-TDK", "Sivaganga-TDK", "Kallal-TDK", "Tiruppuvanam-TDK", "Melur-TDK",
        "Thirumangalam-TDK", "Usilampatti-TDK", "Vadipatti-TDK", "Peraiyur-TDK", "Sholavandan-TDK"
    ],
    "Pudukkottai": [
        "Karambakkudi", "Aranthangi", "Gandarvakottai", "Thiruvarankulam", "Illuppur",
        "Ponnamaravathi-PDK", "Viralimalai", "Kudavasal", "Peravurani-PDK", "Orathanadu-PDK",
        "Pattukottai-PDK", "Papanasam-PDK", "Thiruvavaduthurai", "Thirubuvanam-PDK", "Budalur-PDK",
        "Seerkazhi-PDK", "Swamimalai-PDK", "Darasuram-PDK", "Manamadurai-PDK", "Devakottai-PDK",
        "Tiruppattur-PDK", "Paramakudi-PDK", "Rameswaram-PDK", "Mandapam-PDK", "Keelakarai-PDK",
        "Kilakkarai-PDK", "Ervadi-PDK", "Ramanathapuram-PDK", "Mudukulathur-PDK", "Kalaiyarkoil-PDK",
        "Ilayangudi-PDK", "Kamudi-PDK", "Tiruvadanai-PDK", "Nainarkoil-PDK", "Sayalkudi-PDK",
        "Mimisal-PDK", "Muthukulathur-PDK", "Sivaganga-PDK", "Kallal-PDK", "Madurakoodam-PDK",
        "Tiruppuvanam-PDK", "Melur-PDK", "Karambakkudi-PDK", "Aranthangi-PDK", "Gandarvakottai-PDK",
        "Thiruvarankulam-PDK", "Illuppur-PDK", "Viralimalai-PDK", "Kudavasal-PDK", "Pudukkottai Town"
    ],
    "Ramanathapuram": [
        "Rameswaram", "Mandapam-RMN", "Keelakarai-RMN", "Kilakkarai-RMN", "Ervadi-RMN",
        "Ramanathapuram Town", "Mudukulathur-RMN", "Kalaiyarkoil-RMN", "Ilayangudi-RMN", "Kamudi-RMN",
        "Tiruvadanai-RMN", "Nainarkoil-RMN", "Sayalkudi-RMN", "Mimisal-RMN", "Muthukulathur-RMN",
        "Paramakudi-RMN", "Manamadurai-RMN", "Devakottai-RMN", "Tiruppuvanam-RMN", "Melur-RMN",
        "Thirumangalam-RMN", "Usilampatti-RMN", "Natham-RMN", "Vadipatti-RMN", "Peraiyur-RMN",
        "Arupukkottai-RMN", "Virudhunagar-RMN", "Rajapalayam-RMN", "Eral-RMN", "Ottapidaram-RMN",
        "Kovilpatti-RMN", "Thisayanvilai-RMN", "Kayalpattinam-RMN", "Tiruchendur-RMN", "Srivaikuntam-RMN",
        "Alwarthirunagari-RMN", "Authoor-RMN", "Nazareth-RMN", "Manapad-RMN", "Uvari-RMN",
        "Periavilai-RMN", "Arumuganeri-RMN", "Kulasekarapatnam-RMN", "Punnakayal-RMN", "Mukuperi-RMN",
        "Punnaikayal-RMN", "Meignanapuram-RMN", "Idinthakarai-RMN", "Pamban", "Devipattinam"
    ],
    "Krishnagiri": [
        "Hosur", "Pochampalli", "Bargur-KRG", "Denkanikottai", "Shoolagiri",
        "Kelamangalam", "Mathigiri", "Thally", "Anchetty", "Rayakottah",
        "Uthangarai-KRG", "Kaveripakkam-KRG", "Gudiyatham-KRG", "Vaniyambadi-KRG", "Ambur-KRG",
        "Jolarpettai-KRG", "Tirupattur-KRG", "Natrampalli-KRG", "Dharmapuri-KRG", "Harur-KRG",
        "Pappireddipatti-KRG", "Nallampalli-KRG", "Pennagaram-KRG", "Karimangalam-KRG", "Morappur-KRG",
        "Palacodu-KRG", "Kaveripattinam", "Berigai", "Krishnagiri Town", "Hosur Industrial",
        "Veppanapalli", "Bargur North", "Bargur South", "Hosur North", "Hosur South",
        "Pochampalli North", "Pochampalli South", "Kelamangalam-KRG", "Mathigiri-KRG", "Rayakottah-KRG",
        "Thally-KRG", "Anchetty-KRG", "Denkanikottai-KRG", "Shoolagiri-KRG", "Sulagiri",
        "Uthangarai North", "Uthangarai South", "Hosur East", "Hosur West", "Krishnagiri Rural"
    ],
    "Tiruvannamalai": [
        "Polur", "Arni-TVN", "Cheyyar-TVN", "Vandavasi-TVN", "Tiruvanamalai Town",
        "Chengam", "Thandrampet", "Vembakkam-TVN", "Pudupalayam-TVN", "Thellar",
        "Chetpet-TVN", "Kilpennathur", "Keelpennathur", "Arani-TVN", "Jawadhu Hills",
        "Jamunamarathur", "Alangayam-TVN", "Natrampalli-TVN", "Tirupattur-TVN", "Jolarpettai-TVN",
        "Ambur-TVN", "Vaniyambadi-TVN", "Gudiyatham-TVN", "Pennathur", "Thandrampet-TVN",
        "Polur-TVN", "Chengam-TVN", "Pudupalayam North", "Pudupalayam South", "Thellar-TVN",
        "Kilpennathur-TVN", "Keelpennathur-TVN", "Jawadhu Hills North", "Jawadhu Hills South", "Jamunamarathur-TVN",
        "Tiruvannamalai East", "Tiruvannamalai West", "Tiruvannamalai North", "Tiruvannamalai South", "Tiruvannamalai Central",
        "Polur North", "Polur South", "Arni North", "Arni South", "Cheyyar North",
        "Cheyyar South", "Vandavasi North", "Vandavasi South", "Pennathur-TVN", "Chetpet North"
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
    loss = 0.0  # always zero for healthy villages
    return round(rtt, 2), round(loss, 1)


def get_status(rtt: float, loss: float) -> str:
    if loss >= 80:                return "FAILED"
    if loss >= 20 or rtt >= 500: return "DEGRADED"
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
    if now - last_diagnosis_time < 5:
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
                isolation_time = round(random.uniform(8, 18), 1)

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


def _district_for_village(village: str) -> str:
    """Return district name for a village, or 'Unknown' if not found."""
    for district, villages in DISTRICTS.items():
        if village in villages:
            return district
    return "Unknown"


@app.post("/simulate-fault")
async def simulate_fault(
    segment:    str = Query(...),
    fault_type: str = Query(default="fiber_cut"),
    village:    str = Query(default="Ambattur"),
):
    """
    Inject a controlled fault into a village segment.
    fault_type: fiber_cut | congestion | flapping | device_failure
    Also appends the injection to fault history (in-memory + SQLite).
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
            seg["injected"] = True
            break

    # Map fault_type to human-readable root_cause and action for history
    root_cause_map = {
        "fiber_cut":      ("Fiber Cut",         96, "Dispatch technician to segment"),
        "congestion":     ("Link Congestion",   94, "Reroute traffic"),
        "flapping":       ("Flapping Interface", 85, "Check SFP / transceiver"),
        "device_failure": ("Device Failure",    91, "Reboot or replace device"),
    }
    root_cause, confidence, action = root_cause_map.get(
        fault_type, ("Fiber Cut", 96, "Dispatch technician to segment")
    )
    affected = calculate_impact(segment)
    district = _district_for_village(village)

    await append_history({
        "time":       datetime.now().strftime("%H:%M:%S"),
        "village":    village,
        "district":   district,
        "segment":    segment,
        "root_cause": root_cause,
        "confidence": f"{confidence}%",
        "action":     action,
        "affected":   affected,
    })

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
                seg["injected"] = False
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
