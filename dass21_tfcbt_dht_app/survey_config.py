"""Konfigurasi instrumen untuk prototaip DASS-21 + saringan trauma DHT."""

from __future__ import annotations


APP_VERSION = "1.0.0 AzuraAriffin@Copyright"

KKM_DASS_URL = "https://mits.moh.gov.my/Modules/Patient/public-dass/"
DASS_SCORING_REFERENCE = "https://pmc.ncbi.nlm.nih.gov/articles/PMC6805560/"
DHT_REFERENCE = "https://doi.org/10.37134/bitara.vol10.7.2017"
TF_CBT_REFERENCE = "https://pmc.ncbi.nlm.nih.gov/articles/PMC4476061/"


DASS_OPTIONS = {
    0: "Tidak langsung menggambarkan keadaan saya",
    1: "Sedikit atau jarang-jarang menggambarkan keadaan saya",
    2: "Banyak atau kerap kali menggambarkan keadaan saya",
    3: "Sangat banyak atau sangat kerap menggambarkan keadaan saya",
}

TRAUMA_OPTIONS = {
    0: "Tidak pernah / tidak langsung",
    1: "Sekali-sekala / sedikit",
    2: "Kerap / ketara",
    3: "Hampir selalu / sangat ketara",
}


# Teks Bahasa Melayu disalin daripada senarai soalan yang dimuatkan oleh
# halaman DASS awam MITS KKM pada 18 Ogos 2026.
DASS_ITEMS = [
    {"id": 1, "scale": "Stress", "text": "Saya dapati diri saya sukar ditenteramkan."},
    {"id": 2, "scale": "Anxiety", "text": "Saya sedar mulut saya terasa kering."},
    {"id": 3, "scale": "Depression", "text": "Saya tidak dapat mengalami perasaan positif sama sekali."},
    {
        "id": 4,
        "scale": "Anxiety",
        "text": "Saya mengalami kesukaran bernafas (contohnya pernafasan yang laju, tercungap-cungap walaupun tidak melakukan senaman fizikal).",
    },
    {"id": 5, "scale": "Depression", "text": "Saya sukar untuk mendapatkan semangat bagi melakukan sesuatu perkara."},
    {"id": 6, "scale": "Stress", "text": "Saya cenderung untuk bertindak keterlaluan dalam sesuatu keadaan."},
    {"id": 7, "scale": "Anxiety", "text": "Saya rasa menggeletar (contohnya pada tangan)."},
    {"id": 8, "scale": "Stress", "text": "Saya rasa saya menggunakan banyak tenaga dalam keadaan cemas."},
    {
        "id": 9,
        "scale": "Anxiety",
        "text": "Saya bimbang keadaan di mana saya mungkin menjadi panik dan melakukan perkara yang membodohkan diri sendiri.",
    },
    {"id": 10, "scale": "Depression", "text": "Saya rasa saya tidak mempunyai apa-apa untuk diharapkan."},
    {"id": 11, "scale": "Stress", "text": "Saya dapati diri saya semakin gelisah."},
    {"id": 12, "scale": "Stress", "text": "Saya rasa sukar untuk relaks."},
    {"id": 13, "scale": "Depression", "text": "Saya rasa sedih dan murung."},
    {
        "id": 14,
        "scale": "Stress",
        "text": "Saya tidak dapat menahan sabar dengan perkara yang menghalang saya meneruskan apa yang saya lakukan.",
    },
    {"id": 15, "scale": "Anxiety", "text": "Saya rasa hampir-hampir menjadi panik/cemas."},
    {"id": 16, "scale": "Depression", "text": "Saya tidak bersemangat dengan apa jua yang saya lakukan."},
    {"id": 17, "scale": "Depression", "text": "Saya rasa tidak begitu berharga sebagai seorang individu."},
    {"id": 18, "scale": "Stress", "text": "Saya rasa saya mudah tersentuh."},
    {
        "id": 19,
        "scale": "Anxiety",
        "text": "Saya sedar tindak balas jantung saya walaupun tidak melakukan aktiviti fizikal (contohnya kadar denyutan jantung bertambah atau berkurangan).",
    },
    {"id": 20, "scale": "Anxiety", "text": "Saya berasa takut tanpa sebab yang munasabah."},
    {"id": 21, "scale": "Depression", "text": "Saya rasa hidup ini tidak bermakna."},
]


# Indikator trauma berikut ialah item eksploratori yang dibina untuk prototaip,
# bukan instrumen PTSD/trauma yang telah divalidasi. Pemetaan perlu disemak oleh
# penyelidik utama, pakar klinikal, pakar syariah dan jawatankuasa etika.
TRAUMA_ITEMS = [
    {
        "id": "TR01",
        "domain": "Nyawa",
        "need_level": "Dharuriyyat",
        "tfcbt_impact": "Keselamatan",
        "safety_critical": True,
        "text": "Saya berasa keselamatan fizikal saya atau orang tanggungan saya terancam pada masa ini.",
    },
    {
        "id": "TR02",
        "domain": "Nyawa",
        "need_level": "Hajiyyat",
        "tfcbt_impact": "Biologi",
        "safety_critical": False,
        "text": "Selepas peristiwa sukar, gangguan tidur, mimpi buruk atau reaksi tubuh mengganggu rutin harian saya.",
    },
    {
        "id": "TR03",
        "domain": "Nyawa",
        "need_level": "Tahsiniyyat",
        "tfcbt_impact": "Penjagaan diri",
        "safety_critical": False,
        "text": "Saya sukar mengekalkan rutin penjagaan diri dan aktiviti pemulihan yang membantu saya berasa selamat.",
    },
    {
        "id": "TR04",
        "domain": "Akal",
        "need_level": "Dharuriyyat",
        "tfcbt_impact": "Kognitif/persepsi",
        "safety_critical": False,
        "text": "Ingatan, bayangan atau perasaan seolah-olah peristiwa sukar berulang datang tanpa saya mahu dan sukar dikawal.",
    },
    {
        "id": "TR05",
        "domain": "Akal",
        "need_level": "Hajiyyat",
        "tfcbt_impact": "Kognitif/pembelajaran",
        "safety_critical": False,
        "text": "Saya sukar menumpukan perhatian, belajar atau membuat keputusan selepas peristiwa sukar.",
    },
    {
        "id": "TR06",
        "domain": "Akal",
        "need_level": "Tahsiniyyat",
        "tfcbt_impact": "Afektif",
        "safety_critical": False,
        "text": "Saya sukar menikmati aktiviti bermakna atau aktiviti yang biasanya menenangkan fikiran saya.",
    },
    {
        "id": "TR07",
        "domain": "Keturunan",
        "need_level": "Dharuriyyat",
        "tfcbt_impact": "Keselamatan sosial/keluarga",
        "safety_critical": True,
        "text": "Hubungan dengan keluarga, penjaga atau individu rapat menjadi sumber ancaman atau ketakutan pada masa ini.",
    },
    {
        "id": "TR08",
        "domain": "Keturunan",
        "need_level": "Hajiyyat",
        "tfcbt_impact": "Sosial/sokongan",
        "safety_critical": False,
        "text": "Saya berasa terasing atau kehilangan sokongan daripada keluarga atau rakan yang saya percayai.",
    },
    {
        "id": "TR09",
        "domain": "Keturunan",
        "need_level": "Tahsiniyyat",
        "tfcbt_impact": "Sosial/komuniti",
        "safety_critical": False,
        "text": "Saya sukar mengambil bahagian dalam hubungan atau aktiviti komuniti yang biasanya menguatkan rasa dimiliki.",
    },
    {
        "id": "TR10",
        "domain": "Harta",
        "need_level": "Dharuriyyat",
        "tfcbt_impact": "Keperluan asas",
        "safety_critical": False,
        "text": "Peristiwa sukar menyebabkan saya kehilangan atau berisiko kehilangan tempat tinggal, makanan atau keperluan asas.",
    },
    {
        "id": "TR11",
        "domain": "Harta",
        "need_level": "Hajiyyat",
        "tfcbt_impact": "Fungsi/pembelajaran",
        "safety_critical": False,
        "text": "Masalah kewangan, pengangkutan atau akses peranti/bahan belajar mengganggu pembelajaran atau pemulihan saya.",
    },
    {
        "id": "TR12",
        "domain": "Harta",
        "need_level": "Tahsiniyyat",
        "tfcbt_impact": "Kualiti hidup",
        "safety_critical": False,
        "text": "Kehilangan atau kerosakan barang/sumber peribadi menjejaskan keselesaan dan kualiti hidup saya.",
    },
    {
        "id": "TR13",
        "domain": "Agama",
        "need_level": "Dharuriyyat",
        "tfcbt_impact": "Kerohanian/pegangan",
        "safety_critical": False,
        "text": "Peristiwa sukar menjejaskan kemampuan saya melaksanakan kewajipan agama atau spiritual yang penting bagi saya.",
    },
    {
        "id": "TR14",
        "domain": "Agama",
        "need_level": "Hajiyyat",
        "tfcbt_impact": "Sokongan kerohanian",
        "safety_critical": False,
        "text": "Saya kehilangan akses kepada sokongan agama/spiritual yang selamat dan tidak menghakimi apabila saya memerlukannya.",
    },
    {
        "id": "TR15",
        "domain": "Agama",
        "need_level": "Tahsiniyyat",
        "tfcbt_impact": "Komuniti/kerohanian",
        "safety_critical": False,
        "text": "Saya sukar menyertai rutin atau komuniti agama/spiritual yang biasanya memberi ketenangan dan makna.",
    },
]


DASS_THRESHOLDS = {
    "Depression": [
        (0, 9, "Normal"),
        (10, 13, "Ringan"),
        (14, 20, "Sederhana"),
        (21, 27, "Teruk"),
        (28, 42, "Sangat Teruk"),
    ],
    "Anxiety": [
        (0, 7, "Normal"),
        (8, 9, "Ringan"),
        (10, 14, "Sederhana"),
        (15, 19, "Teruk"),
        (20, 42, "Sangat Teruk"),
    ],
    "Stress": [
        (0, 14, "Normal"),
        (15, 18, "Ringan"),
        (19, 25, "Sederhana"),
        (26, 33, "Teruk"),
        (34, 42, "Sangat Teruk"),
    ],
}

SEVERITY_ORDER = ["Normal", "Ringan", "Sederhana", "Teruk", "Sangat Teruk"]
ASSESSMENT_PHASES = ["Pra-intervensi", "Pasca-intervensi", "Susulan", "Lain-lain"]

