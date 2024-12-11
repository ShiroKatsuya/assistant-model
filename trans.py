from deep_translator import GoogleTranslator

# Use any translator you like, in this example GoogleTranslator
text = (
    "Akhir dari segala sesuatu di alam semesta adalah konsep yang telah memukau para ilmuwan dan filsuf selama berabad-abad. Berdasarkan teori-teori ilmiah saat ini, ada beberapa skenario yang mungkin untuk nasib akhir alam semesta:\n\n"
    "Kematian Panas (The Big Freeze)\n"
    "Dalam skenario ini, alam semesta akan terus mengembang selamanya. Seiring waktu, bintang-bintang akan padam, lubang hitam akan menguap, dan materi akan semakin tersebar. Akhirnya, alam semesta akan mencapai keadaan entropi maksimum, di mana tidak ada energi yang tersedia untuk menopang proses apapun, dan menjadi dingin, gelap, serta tak bernyawa.\n\n"
    "The Big Crunch\n"
    "Ini adalah kebalikan dari Big Bang. Jika tarikan gravitasi dari semua materi di alam semesta mengalahkan gaya yang mendorong ekspansinya, alam semesta bisa mulai berkontraksi. Selama miliaran tahun, semuanya akan runtuh menjadi singularitas, yang pada dasarnya membalikkan Big Bang.\n\n"
    "The Big Rip\n"
    "Jika ekspansi alam semesta terus dipercepat karena energi gelap, bisa saja mencapai titik di mana struktur ruang-waktu meregang sedemikian rupa sehingga galaksi, bintang, planet, bahkan atom akan terkoyak.\n\n"
    "Keruntuhan Vakum (Vacuum Decay)\n"
    "Ini adalah teori yang lebih spekulatif yang menyatakan bahwa alam semesta mungkin berada dalam keadaan \"vakum palsu\". Fluktuasi kuantum dapat menyebabkan peralihannya ke \"vakum sejati,\" menciptakan gelembung kehancuran yang menyebar dengan kecepatan cahaya dan menghancurkan segala sesuatu di jalurnya.\n\n"
    "Setiap skenario ini bergantung pada faktor-faktor seperti sifat energi gelap, total massa alam semesta, dan hukum-hukum fisika. Meskipun semuanya menggambarkan akhir yang tak terhindarkan, skala waktu yang terlibat sangatlah besar—triliunan hingga triliunan tahun—sehingga sulit dipahami dalam istilah manusia."
)

translated = GoogleTranslator(source='auto', target='en').translate(text)  # output -> Weiter so, du bist großartig



print(translated)
