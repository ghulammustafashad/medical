import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from gtts import gTTS
import requests
from bs4 import BeautifulSoup
import re
import time

from transformers import BartTokenizer, BartForConditionalGeneration
# Load BART model and tokenizer
tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")

def complete_sentence(summary, max_word_count=50):
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', summary)
    word_count = 0
    selected_sentences = []
    for sentence in sentences:
        words = sentence.split()
        if word_count + len(words) <= max_word_count:
            selected_sentences.append(sentence)
            word_count += len(words)
        else:
            break
    return " ".join(selected_sentences)

def get_sections_content(pmc_id):
    url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    abstract_section = soup.select_one(".abstract-content")
    if abstract_section:
        abstract = abstract_section.get_text().strip()
    else:
        abstract = ""

    sections = soup.select(".tsec")
    section_data = {}

    unwanted_sections = [
        "Abstract",
        "Supplementary information",
        "Associated Data"
        "Acknowledgments",
        "Abbreviations",
        "Authors’ contributions",
        "Funding",
        "Availability of data and materials",
        "Ethics approval and consent to participate",
        "Consent for publication",
        "Competing interests",
        "Footnotes",
        "Publisher’s Note",
        "References",
        "Appendix. SUPPLEMENTARY INFORMATION",
        "REFERENCES",
        "Disclosure",
        "Appendix. Authors",  # Remove "Appendix. Authors" section
        "Study Funding",  # Remove "Study Funding" section
    ]

    for section in sections:
        section_title_element = section.find("h1") or section.find("h2") or section.find("h3") or section.find(
            "h4") 
        if section_title_element:
            section_title = section_title_element.get_text().strip()
            section_content = "\n".join([p.get_text() for p in section.select("p")])

            if section_title not in unwanted_sections:
                section_data[section_title] = section_content

    return abstract, section_data

def generate_pdf(category, title, authors, doi, abstract, section_data):
    output_dir = f"output/{category}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filename = os.path.join(output_dir, f"{title}_summary.pdf")

    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()

    content = []

    # Add category and article information to the PDF
    content.append(Paragraph(f"Category: {category.capitalize()}", styles["Title"]))
    content.append(Paragraph(f"Title: {title}", styles["Heading1"]))
    content.append(Paragraph(f"Authors: {authors}", styles["Normal"]))
    content.append(Paragraph(f"DOI: {doi}", styles["Normal"]))

    # Add abstract content to the PDF
    if abstract:
        content.append(Paragraph(f"Summary:\n{abstract}\n", styles["Normal"]))

    # Add section summaries to the PDF
    for section_title, section_summary in section_data.items():
        content.append(Paragraph(f"{section_title}", styles["Heading3"]))
        content.append(Paragraph(f"{section_summary}\n", styles["Normal"]))

    doc.build(content)

def generate_audio(category, title, abstract, section_data):
    output_dir = f"output/{category}/audio"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filename = os.path.join(output_dir, f"{title}.mp3")

    full_text = f"Summary: {title}\n\n"
    if abstract:
        full_text += f"{abstract}\n\n"

    for section_title, section_summary in section_data.items():
        full_text += f"{section_title}\n{section_summary}\n\n"

    tts = gTTS(text=full_text, lang="en", slow=False, tld="com")
    tts.save(filename)
    time.sleep(2)  # Add a delay of 2 seconds between generating audio files

def print_anesthesiology_summary():
    # Add spine surgery articles and their PMC IDs
    anesthesiology_articles = [

{
"pmc_id": "PMC10328513",
"title": "A consensus statement on the meaning, value and utility of training programme outcomes, with specific reference to anaesthesiology: A consensus statement on training programme outcomes",
"authors": "George Shorten, Lisa Bahrey, Amit Bardia, Stefan De Hert, Emilia Guasch, Eric Holmboe, Martin McCormack, Brian O’Brien, Camillus Power, Bernadette Rock, Olegs Sabelnikovs",
"doi": "10.1097/EJA.0000000000001868",
"year": "2023"
},

{
"pmc_id": "PMC8313821",
"title": "Thoracic Anesthesia during the COVID-19 Pandemic: 2021 Updated Recommendations by the European Association of Cardiothoracic Anaesthesiology and Intensive Care (EACTAIC) Thoracic Subspecialty Committee",
"authors": "Mert Şentürk, Mohamed R. El Tahan, Ben Shelley, Laszlo L. Szegedi, Federico Piccioni, Marc-Joseph Licker, Waheedullah Karzai, Manuel Granell Gil, Vojislava Neskovic, Caroline Vanpeteghem, Paolo Pelosi, Edmond Cohen, Massimiliano Sorbello, Johan Bence MBChB, Radu Stoica, Jo Mourisse, Alex Brunelli, Maria-José Jimenez, Mojca Drnovsek Globokar, Davud Yapici, Ahmed Salaheldin Morsy, Izumi Kawagoe, Tamás Végh, Ricard Navarro-Ripoll, Nandor Marczin, Balazs Paloczi, Carmen Unzueta, Guido Di Gregorio, Patrick Wouters, Steffen Rex, Chirojit Mukherjee, Gianluca Paternoster, Fabio Guarracino",
"doi": "10.1053/j.jvca.2021.07.027",
"year": "2021"
},

{
"pmc_id": "PMC9660141",
"title": "Practice of oxygen use in anesthesiology – a survey of the European Society of Anaesthesiology and Intensive Care",
"authors": "Martin Scharffenberg, Thomas Weiss, Jakob Wittenstein, Katharina Krenn, Magdalena Fleming, Peter Biro, Stefan De Hert, Jan F. A. Hendrickx, Daniela Ionescu, Marcelo Gama de Abreu, for the European Society of Anaesthesiology and Intensive Care",
"doi": "10.1186/s12871-022-01884-2",
"year": "2022"
},

{
"pmc_id": "PMC8356099",
"title": "Anaesthesiology in China: A cross-sectional survey of the current status of anaesthesiology departments",
"authors": "Changsheng Zhang, Shengshu Wang, Hange Li, Fan Su, Yuguang Huang, Weidong Mi, The Chinese Anaesthesiology Department Tracking Collaboration Group",
"doi": "10.1016/j.lanwpc.2021.100166",
"year": "2021"
},

{
"pmc_id": "PMC5727625",
"title": "Incidence and Factors Associated with Burnout in Anesthesiology: A Systematic Review",
"authors": "Filippo Sanfilippo, Alberto Noto, Grazia Foresta, Cristina Santonocito, Gaetano J. Palumbo, Antonio Arcadipane, Dirk M. Maybauer, Marc O. Maybauer",
"doi": "10.1155/2017/8648925",
"year": "2017"
},

{
"pmc_id": "PMC8582177",
"title": "First steps towards international competency goals for residency training: a qualitative comparison of 3 regional standards in anesthesiology",
"authors": "Clément Buléon, Reuben Eng, Jenny W. Rudolph, Rebecca D. Minehart",
"doi": "10.1186/s12909-021-03007-w",
"year": "2021"
},

{
"pmc_id": "PMC8558093",
"title": "Current practice of thoracic anesthesia in Europe – a survey by the European Society of Anaesthesiology Part I – airway management and regional anaesthesia techniques",
"authors": "Jerome Defosse, Mark Schieren, Torsten Loop, Vera von Dossow, Frank Wappler, Marcelo Gama de Abreu, Mark Ulrich Gerbershagen",
"doi": "10.1186/s12871-021-01480-w",
"year": "2021"
},

{
"pmc_id": "PMC7273774",
"title": "Clinical practice in the management of postoperative delirium by Chinese anesthesiologists: a cross-sectional survey designed by the European Society of Anaesthesiology",
"authors": "Simon Delp, Wei Mei, Claudia D. Spies, Bruno Neuner, César Aldecoa, Gabriella Bettelli, Federico Bilotta, Robert D. Sanders, Sylvia Kramer, Bjoern Weiss",
"doi": "10.1177/0300060520927207",
"year": "2020"
},

{
"pmc_id": "PMC5091797",
"title": "Reporting of preclinical research in ANESTHESIOLOGY: Transparency and Enforcement",
"authors": "James C. Eisenach, David S. Warner, Timothy T. Houle",
"doi": "10.1097/ALN.0000000000001044",
"year": "2016"
},

{
"pmc_id": "PMC7151284",
"title": "Thoracic Anesthesia of Patients With Suspected or Confirmed 2019 Novel Coronavirus Infection: Preliminary Recommendations for Airway Management by the European Association of Cardiothoracic Anaesthesiology Thoracic Subspecialty Committee",
"authors": "Mert Şentürk, Mohamed R. El Tahan, Laszlo L. Szegedi, Nandor Marczin, Waheedullah Karzai, Ben Shelley, Federico Piccioni, Manuel Granell Gil, Steffen Rex, Massimiliano Sorbello, Johan Bence, Edmond Cohen, Guido Di Gregorio, Izumi Kawagoe, Mojca Drnovšek Globokar, Maria-José Jimenez, Marc-Joseph Licker, Jo Mourisse, Chirojit Mukherjee, Ricard Navarro, Vojislava Neskovic, Balazs Paloczi, Gianluca Paternoster, Paolo Pelosi, Ahmed Salaheldeen, Radu Stoica, Carmen Unzueta, Caroline Vanpeteghem, Tamas Vegh, Patrick Wouters, Davud Yapici, Fabio Guarracino",
"doi": "10.1053/j.jvca.2020.03.059",
"year": "2020"
},

{
"pmc_id": "PMC6567593",
"title": "Anaesthesiology students’ Non-Technical skills: development and evaluation of a behavioural marker system for students (AS-NTS)",
"authors": "Parisa Moll-Khosrawi, Anne Kamphausen, Wolfgang Hampe, Leonie Schulte-Uentrop, Stefan Zimmermann, Jens Christian Kubitz",
"doi": "10.1186/s12909-019-1609-8",
"year": "2019"
},

{
"pmc_id": "PMC10335696",
"title": "National consensus on entrustable professional activities for competency-based training in anaesthesiology",
"authors": "Alexander Ganzhorn, Leonie Schulte-Uentrop, Josephine Küllmei, Christian Zöllner, Parisa Moll-Khosrawi",
"doi": "10.1371/journal.pone.0288197",
"year": "2023"
},

{
"pmc_id": "PMC9052481",
"title": "Development and consensus of entrustable professional activities for final-year medical students in anaesthesiology",
"authors": "Andreas Weissenbacher, Robert Bolz, Sebastian N. Stehr, Gunther Hempel",
"doi": "10.1186/s12871-022-01668-8",
"year": "2022"
},

{
"pmc_id": "PMC9799042",
"title": "Welfare practices for anaesthesiology trainees in Europe: A descriptive cross-sectional survey study",
"authors": "Joana Berger-Estilita, Jacqueline Leitl, Susana Vacas, Vojislava Neskovic, Frank Stüber, Marko Zdravkovic",
"doi": "10.1097/EJA.0000000000001787",
"year": "2023"
},

{
"pmc_id": "PMC8584380",
"title": "An Evaluation of the Performance of Five Burnout Screening Tools: A Multicentre Study in Anaesthesiology, Intensive Care, and Ancillary Staff",
"authors": "John Ong, Wan Yen Lim, Kinjal Doshi, Man Zhou, Ban Leong Sng, Li Hoon Tan, Sharon Ong",
"doi": "10.3390/jcm10214836",
"year": "2021"
},

{
"pmc_id": "PMC7889009",
"title": "EACTA/SCA Recommendations for the Cardiac Anesthesia Management of Patients With Suspected or Confirmed COVID-19 Infection: An Expert Consensus From the European Association of Cardiothoracic Anesthesiology and Society of Cardiovascular Anesthesiologists With Endorsement From the Chinese Society of Cardiothoracic and Vascular Anesthesiology",
"authors": "Fabio Guarracino, Stanton K. Shernan, Mohamed El Tahan, Pietro Bertini, Marc E. Stone, Bessie Kachulis, Gianluca Paternoster, Chirojit Mukherjee, Patrick Wouters, Steffen Rex",
"doi": "10.1053/j.jvca.2021.02.039",
"year": "2021"
},

{
"pmc_id": "PMC8295977",
"title": "The efficacy of virtual distance training of intensive therapy and anaesthesiology among fifth-year medical students during the COVID-19 pandemic: a cross-sectional study",
"authors": "Enikő Kovács, András Kállai, Gábor Fritúz, Zsolt Iványi, Vivien Mikó, Luca Valkó, Balázs Hauser, János Gál",
"doi": "10.1186/s12909-021-02826-1",
"year": "2021"
},

{
"pmc_id": "PMC4626294",
"title": "Apnea after awake-regional and general anesthesia in infants: The General Anesthesia compared to Spinal anesthesia (GAS) study: comparing apnea and neurodevelopmental outcomes, a randomized controlled trial",
"authors": "Andrew J. Davidson, Neil S. Morton, Sarah J. Arnup, Jurgen C. de Graaff, Nicola Disma, Davinia E. Withington, Geoff Frawley, Rodney W. Hunt, Pollyanna Hardy, Magda Khotcholava, Britta S. von Ungern Sternberg, Niall Wilton, Pietro Tuo, Ida Salvo, Gillian Ormond, Robyn Stargatt, Bruno Guido Locatelli, Mary Ellen McCann, The GAS Consortium (see Appendix 1)",
"doi": "10.1097/ALN.0000000000000709",
"year": "2015"
},

{
"pmc_id": "PMC4573227",
"title": "Risk and outcomes of substance use disorder among anesthesiology residents: A matched cohort analysis",
"authors": "David O. Warner, Keith Berge, Huaping Sun, Ann Harman, Andrew Hanson, Darrell R. Schroeder",
"doi": "10.1097/ALN.0000000000000810",
"year": "2015"
},

{
"pmc_id": "PMC6778496",
"title": "Artificial Intelligence and Machine Learning in Anesthesiology",
"authors": "Christopher W Connor",
"doi": "10.1097/ALN.0000000000002694",
"year": "2019"
},

{
"pmc_id": "PMC9594131",
"title": "Intensive care medicine in Europe: perspectives from the European Society of Anaesthesiology and Intensive Care",
"authors": "Kai Zacharowski, Daniela Filipescu, Paolo Pelosi, Jonas Åkeson, Serban Bubenek, Cesare Gregoretti, Michael Sander, Edoardo de Robertis",
"doi": "10.1097/EJA.0000000000001706",
"year": "2022"
},

{
"pmc_id": "PMC3470444",
"title": "Do technical skills correlate with non-technical skills in crisis resource management: a simulation study",
"authors": "N. Riem, S. Boet, M. D. Bould, W. Tavares, V. N. Naik",
"doi": "10.1093/bja/aes256",
"year": "2012"
},

{
"pmc_id": "PMC5367721",
"title": "Turkish Publications in Science Citation Index and Citation Index-Expanded Indexed Journals in the Field of Anaesthesiology: A Bibliographic Analysis",
"authors": "Şule Özbilgin, Volkan Hancı",
"doi": "10.5152/TJAR.2017.66587",
"year": "2017"
},

{
"pmc_id": "PMC9373559",
"title": "Competency-based anesthesiology teaching: comparison of programs in Brazil, Canada and the United States",
"authors": "Rafael Vinagre, Pedro Tanaka, Maria Angela Tardelli",
"doi": "10.1016/j.bjane.2020.12.026",
"year": "2021"
},


{
"pmc_id": "PMC6460737",
"title": "Microcirculatory perfusion disturbances following cardiac surgery with cardiopulmonary bypass are associated with in vitro endothelial hyperpermeability and increased angiopoietin-2 levels",
"authors": "Nicole A. M. Dekker, Anoek L. I. van Leeuwen, Willem W. J. van Strien, Jisca Majolée, Robert Szulcek, Alexander B. A. Vonk, Peter L. Hordijk, Christa Boer, Charissa E. van den Brom",
"doi": "10.1186/s13054-019-2418-5",
"year": "2019 Apr 11"
},

{
"pmc_id": "PMC8126531",
"title": "The effect of targeting Tie2 on hemorrhagic shock-induced renal perfusion disturbances in rats",
"authors": "Anoek L. I. van Leeuwen, Nicole A. M. Dekker, Paul Van Slyke, Esther de Groot, Marc G. Vervloet, Joris J. T. H. Roelofs, Matijs van Meurs, Charissa E. van den Brom",
"doi": "10.1186/s40635-021-00389-5",
"year": "2021 May 17"
},

{
"pmc_id": "PMC7222340",
"title": "Microcirculatory perfusion disturbances following cardiopulmonary bypass: a systematic review",
"authors": "Matthijs M. den Os, Charissa E. van den Brom, Anoek L. I. van Leeuwen, Nicole A. M. Dekker",
"doi": "10.1186/s13054-020-02948-w",
"year": "2020 May 13"
},

{
"pmc_id": "PMC7643051",
"title": "Artificial Intelligence in Anesthesiology: Current Techniques, Clinical Applications, and Limitations",
"authors": "Daniel A Hashimoto, Elan Witkowski, Lei Gao, Ozanan Meireles, Guy Rosman",
"doi": "10.1097/ALN.0000000000002960",
"year": "2020 Feb"
},

{
"pmc_id": "PMC6510665",
"title": "Progressive Increase in Scholarly Productivity of New American Board of Anesthesiology Diplomates From 2006 to 2016: A Bibliometric Analysis",
"authors": "Daniel K Ford, Aaron Richman, Lena M Mayes, Paul S Pagel, Karsten Bartels",
"doi": "10.1213/ANE.0000000000003926",
"year": "2019 Apr"
},

{
"pmc_id": "PMC6714503",
"title": "Implementation and Evaluation of a Web-Based Distribution System For Anesthesia Department Guidelines and Standard Operating Procedures: Qualitative Study and Content Analysis",
"authors": "Kaspar F Bachmann, Christian Vetter, Lars Wenzel, Christoph Konrad, Andreas P Vogt",
"doi": "10.2196/14482",
"year": "2019 Aug"
},

{
"pmc_id": "PMC9426260",
"title": "Critical Appraisal of Anesthesiology Educational Research for 2019",
"authors": "Lara Zisblatt, Fei Chen, Dawn Dillman, Amy N. DiLorenzo, Mark P. MacEachern, Amy Miller Juve, Emily E. Peoples, Connor Snarskis, Ashley E. Grantham",
"doi": "10.46374/volxxiv_issue2_zisblatt",
"year": "2022 Apr-Jun"
},

{
"pmc_id": "PMC9543689",
"title": "Transfusion strategies in bleeding critically ill adults: A clinical practice guideline from the European Society of Intensive Care Medicine: Endorsement by the Scandinavian Society of Anaesthesiology and Intensive Care Medicine",
"authors": "Morten Hylander Møller, Martin Ingi Sigurðsson, Klaus T. Olkkola, Marius Rehn, Arvi Yli‐Hankala, Michelle S. Chew",
"doi": "10.1111/aas.14047",
"year": "2022 May"
},

{
"pmc_id": "PMC2322866",
"title": "Anesthesiology Physician Scientists in Academic Medicine: A Wake-up Call",
"authors": "Debra A. Schwinn, Jeffrey R. Balser",
"doi": "10.1097/00000542-200601000-00023",
"year": "2006 Jan"
},

{
"pmc_id": "PMC6993108",
"title": "Humanistic medicine in anaesthesiology: development and assessment of a curriculum in humanism for postgraduate anaesthesiology trainees",
"authors": "Cecilia Canales, Suzanne Strom, Cynthia T. Anderson, Michelle A. Fortier, Maxime Cannesson, Joseph B. Rinehart, Zeev N. Kain, Danielle Perret",
"doi": "10.1016/j.bja.2019.08.021",
"year": "2019 Dec"
},

{
"pmc_id": "PMC7020051",
"title": "The Abbreviated Maslach Burnout Inventory Can Overestimate Burnout: A Study of Anesthesiology Residents",
"authors": "Wan Yen Lim, John Ong, Sharon Ong, Ying Hao, Hairil Rizal Abdullah, Darren LK Koh, Un Sam May Mok",
"doi": "10.3390/jcm9010061",
"year": "2020 Jan"
},

{
"pmc_id": "PMC6025802",
"title": "The effects of graduate competency-based education and mastery learning on patient care and return on investment: a narrative review of basic anesthetic procedures",
"authors": "Claus Hedebo Bisgaard, Sune Leisgaard Mørck Rubak, Svein Aage Rodt, Jens Aage Kølsen Petersen, Peter Musaeus",
"doi": "10.1186/s12909-018-1262-7",
"year": "2018 Jun 28"
},

{
"pmc_id": "PMC3905449",
"title": "Facilitation of Resident Scholarly Activity: Strategy and Outcome Analyses Using Historical Resident Cohorts and a Rank-to-Match Population",
"authors": "Tetsuro Sakai, Trent D. Emerick, David G. Metro, Rita M. Patel, Sandra C. Hirsch, Daniel G. Winger, Yan Xu",
"doi": "10.1097/ALN.0000000000000066",
"year": "2014 Jan"
},

{
"pmc_id": "PMC6204052",
"title": "TRACE (Routine posTsuRgical Anesthesia visit to improve patient outComE): a prospective, multicenter, stepped-wedge, cluster-randomized interventional study",
"authors": "Valérie M. Smit-Fun, Dianne de Korte-de Boer, Linda M. Posthuma, Annick Stolze, Carmen D. Dirksen, Markus W. Hollmann, Wolfgang F. Buhre, Christa Boer",
"doi": "10.1186/s13063-018-2952-5",
"year": "2018 Oct 26"
},

{
"pmc_id": "PMC6446467",
"title": "Patient safety in undergraduate medical education: Implementation of the topic in the anaesthesiology core curriculum at the University Medical Center Hamburg-Eppendorf",
"authors": "Nicolas Hoffmann, Jens C. Kubitz, Alwin E. Goetz, Stefan K. Beckers",
"doi": "10.3205/zma001220",
"year": "2019 Mar 15"
},

{
"pmc_id": "PMC8074021",
"title": "Critical Care Medicine Practice - A pilot survey of United States Anesthesia Critical Care Medicine Trained Physicians",
"authors": "Shahla Siddiqui, Karsten Bartels, Maximilian S. Schaefer, Lena Novack, Roshni Sreedharan, Talia K. Ben-Jacob, Ashish K. Khanna, Mark E. Nunnally, Michael Souter, Shawn T. Simmons, George Williams",
"doi": "10.1213/ANE.0000000000005030",
"year": "2021 Mar 1"
},

{
"pmc_id": "PMC9214381",
"title": "Anaesthesia provision, infrastructure and resources in the Heilongjiang Province, China: a cross-sectional observational study",
"authors": "Xiaoyu Zheng, Jingshun Zhao, Jian Zhang, Dandan Yao, Ge Jiang, Wanchao Yang, Xuesong Ma, Hui Wang, Xiaodi Lu, Xidong Zhu, Meijun Chen, Mingyue Zhang, Xi Zhang, Guonian Wang, Fei Han",
"doi": "10.1136/bmjopen-2021-051934",
"year": "2022 Jun 20"
},

{
"pmc_id": "PMC3893706",
"title": "Automated Near Real-Time Clinical Performance Feedback for Anesthesiology Residents: One Piece of the Milestones Puzzle",
"authors": "Jesse M. Ehrenfeld, Matthew D. McEvoy, William R. Furman, Dylan Snyder, Warren S. Sandberg",
"doi": "10.1097/ALN.0000000000000071",
"year": "2014 Jan"
},

{
"pmc_id": "PMC8511392",
"title": "Academic Publication of Anesthesiology From a Bibliographic Perspective From 1999 to 2018: Comparative Analysis Using Subject-Field Dataset and Department Dataset",
"authors": "Sy-Yuan Chen, Ling-Fang Wei, Mu-Hsuan Huang, Chiu-Ming Ho",
"doi": "10.3389/fmed.2021.658833",
"year": "2021 Sep 29"
},

{
"pmc_id": "PMC4955686",
"title": "Effect of Performance Deficiencies on Graduation and Board Certification Rates: A 10-Year Multicenter Study of Anesthesiology Residents",
"authors": "Judi A. Turner, Michael G. Fitzsimons, Manuel C. Pardo, Jr, Joy L. Hawkins, Yue Ming Huang, Maria D. D. Rudolph, Mary A. Keyes, Kimberly J. Howard-Quijano, Natale Z. Naim, Jack C. Buckley, Tristan R. Grogan, Randolph H. Steadman",
"doi": "10.1097/ALN.0000000000001142",
"year": "2016 Jul"
},


{
"pmc_id": "PMC9214381",
"title": "Anaesthesia provision, infrastructure and resources in the Heilongjiang Province, China: a cross-sectional observational study",
"authors": "Xiaoyu Zheng, Jingshun Zhao, Jian Zhang, Dandan Yao, Ge Jiang, Wanchao Yang, Xuesong Ma, Hui Wang, Xiaodi Lu, Xidong Zhu, Meijun Chen, Mingyue Zhang, Xi Zhang, Guonian Wang, Fei Han",
"doi": "10.1136/bmjopen-2021-051934",
"year": "2022 Jun 20"
},
        
        # Add more articles here
    ]

    for article in anesthesiology_articles:
        abstract, section_data = get_sections_content(article["pmc_id"])

        if section_data:
            print(f"\033[1m{article['title']}\033[0m\n")
            print(f"\033[1mAuthors:\033[0m {article['authors']}")
            print(f"\033[1mPMCID:\033[0m {article['pmc_id']}\n")

            summary = complete_sentence(abstract, max_word_count=50)
            print(f"\033[1mSummary\033[0m\n{'-' * 7}")
            print(f"{summary}\n")

            for section_title, section_content in section_data.items():
                summary = complete_sentence(section_content, max_word_count=50)
                print(f"\033[1m{section_title}\033[0m\n{'-' * len(section_title)}")
                print(f"{summary}\n")

            print("\n")

            # Save to PDF and audio files
            generate_pdf("anesthesiology", article["title"], article["authors"], "", abstract, section_data)
            generate_audio("anesthesiology", article["title"], abstract, section_data)
            time.sleep(2)  # Add a delay of 2 seconds before processing the next article

def main():
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Call the print_spine_surgery_summary directly
    print_anesthesiology_summary()

if __name__ == "__main__":
    main()