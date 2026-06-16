

TRAVEL_DOCUMENTS_MAPPING = {
    "id card": "ID Card",
    "passport": "Passport",
    "seaman's book": "Seaman's Book",
    "seaman book": "Seaman's Book",
    "visa": "Visa",
    "work permit": "Work permit",
    "driving license": "Driving License",
    "residence permit": "Residence permit",
    "vaccination against covid 19": "Vaccination against: Covid 19",
}

MIGR_MAPPING = {
    "food handling": "FOOD HANDLING",
    "steward": "STEWARD",
    "deck & engine rating": "DECK & ENGINE RATING",
    "deck and engine rating": "DECK & ENGINE RATING",
    "welder": "WELDER",
    "wiper": "WIPER",
    "messman": "MESSMAN",
    "galley boy": "GALLEY BOY",
    "electrician": "ELECTRICIAN",
    "ordinary seaman": "ORDINARY SEAMAN",
    "rating": "RATING",
    "pumpman": "PUMPMAN",
    "shipfitter": "SHIPFITTER",
}

COC_MAPPING = {
    "master": "Master on ships of 3000GT or more (unlimited)",
    "chief mate": "Chief mate on ships of 3000GT or more (unlimited)",
    "chief officer": "Chief mate on ships of 3000GT or more (unlimited)",
    "second engineer": "2nd Eng. on ships with power 3000 KWT or more (unlimited)",
    "2nd engineer": "2nd Eng. on ships with power 3000 KWT or more (unlimited)",
    "chief engineer": "Ch. Eng. on ships with power 3000 KWT or more (unlimited)",
    "eto": "Electro-Technical Officers (ETO)",
    "electro technical officer": "Electro-Technical Officers (ETO)",
    "officer in charge of engineering watch":
        "Officer in charge of an Engineering Watch",
    "officer in charge of navigation watch":
        "Officer in charge of a navigation watch",
    "cook": "Ship`s Cook",
    "welder": "Welder",
    "wiper": "Wiper",
}

MEDICAL_MAPPING = {
    "yellow fever": "Vaccination against: Yellow Fever",
    "yellow fever vaccination": "Vaccination against: Yellow Fever",

    "covid vaccine": "Vaccination against: Covid 19",
    "covid vaccination": "Vaccination against: Covid 19",

    "covid test": "COVID-19 test",
    "pcr covid test": "PCR -COVD TEST",

    "eng1": "Seafarer Medical Certificate (ENG1)",
    "medical certificate": "Seafarer Medical Certificate (ENG1)",

    "hiv": "HIV test",
    "hiv test": "HIV test",

    "hepatitis test": "Hepatitis test",
}

TRAINING_MAPPING = {

    "basic safety training":
        "Basic Safety Training (SOLAS)",

    "bst":
        "Basic Safety Training (SOLAS)",

    "aff":
        "Advanced Fire Fighting",

    "advanced fire fighting":
        "Advanced Fire Fighting",

    "crowd management":
        "Crowd management",

    "crisis management and human behavior":
        "Crisis Management and Human Behavior",

    "leadership and teamwork":
        "Leadership and Teamwork (Management Level) IMO 1.39",

    "security familiarization":
        "Security Familiarization (ISPS Code)",

    "isps":
        "Security Familiarization (ISPS Code)",

    "pst":
        "Personal Survival Techniques (PST)",

    "pSSR":
        "Personal Safety & Social Responsibilities (PSSR)",

    "elementary first aid":
        "Elementary First Aid (EFA)",

    "proficiency survival craft and rescue boat":
        "Proficiency Survival Craft and Rescue Boat (other than Fast Rescue boats)",

    "fast rescue boat":
        "Proficiency in Fast Rescue Boat",

    "tanker familiarization":
        "Tanker Familiarization",

    "ship security awareness":
        "Ship Security Awareness",

    "ship security officer":
        "Ship Security Officer",

    "gmdss":
        "GMDSS (Restricted Operator)",

    "ecdis":
        "The Operational Use of Electronic Chart Display and Information Systems (ECDIS)",
}

ENDORSEMENT_MAPPING = {
    "coc endorsement": "COC Endorsement",

    "gmdss endorsement": "GMDSS Endorsement",
    "gmdss": "GMDSS Endorsement",

    "ship cook": "Ship´s Cook MLC 2006",
    "ship's cook": "Ship´s Cook MLC 2006",
    "ships cook": "Ship´s Cook MLC 2006",

    "tanker endorsement chemical":
        "Tanker Endorsement (Chemical) Operational",

    "tanker endorsement gas":
        "Tanker Endorsement (Gas) Operational",

    "tanker endorsement oil":
        "Tanker Endorsement (Oil) Operational",

    "chemical tanker endorsement":
        "Tanker Endorsement (Chemical) Operational",

    "gas tanker endorsement":
        "Tanker Endorsement (Gas) Operational",

    "oil tanker endorsement":
        "Tanker Endorsement (Oil) Operational",
}

CERTIFICATE_MAPPINGS = {
    "Travel Documents": TRAVEL_DOCUMENTS_MAPPING,
    "Migr": MIGR_MAPPING,
    "Certificate of Competency": COC_MAPPING,
    "Endorsements": ENDORSEMENT_MAPPING,
    "Medical": MEDICAL_MAPPING,
    "Training": TRAINING_MAPPING,
}

CERT_FIELD_MAPPING = {
    "Migr": {
        "country": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[4]/td/form/table/tbody/tr[3]/td/input",
        "issuer": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[4]/td/form/table/tbody/tr[4]/td/input",
        "issued": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[4]/td/form/table/tbody/tr[5]/td/input[1]",
        "expires": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[4]/td/form/table/tbody/tr[6]/td/input[1]",
        "number": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[4]/td/form/table/tbody/tr[7]/td/input",
        "notes": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[4]/td/form/table/tbody/tr[8]/td/textarea",
    },
    "Certificate of Competency": {
        "country": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[6]/td/form/table/tbody/tr[3]/td/input",
        "issuer": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[6]/td/form/table/tbody/tr[4]/td/input",
        "issued": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[6]/td/form/table/tbody/tr[5]/td/input[1]",
        "expires": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[6]/td/form/table/tbody/tr[6]/td/input[1]",
        "number": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[6]/td/form/table/tbody/tr[7]/td/input",
        "notes": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[6]/td/form/table/tbody/tr[8]/td/textarea",
    },
    "Endorsements": {
        "country": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[8]/td/form/table/tbody/tr[3]/td/input",
        "issuer": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[8]/td/form/table/tbody/tr[4]/td/input",
        "issued": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[8]/td/form/table/tbody/tr[5]/td/input[1]",
        "expires": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[8]/td/form/table/tbody/tr[6]/td/input[1]",
        "number": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[8]/td/form/table/tbody/tr[7]/td/input",
        "notes": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[8]/td/form/table/tbody/tr[8]/td/textarea",
    },
    "Medical": {
        "country": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[10]/td/form/table/tbody/tr[3]/td/input",
        "issuer": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[10]/td/form/table/tbody/tr[4]/td/input",
        "issued": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[10]/td/form/table/tbody/tr[5]/td/input[1]",
        "expires": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[10]/td/form/table/tbody/tr[6]/td/input[1]",
        "number": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[10]/td/form/table/tbody/tr[7]/td/input",
        "notes": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[10]/td/form/table/tbody/tr[8]/td/textarea",
    },
    "Training": {
        "country": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[12]/td/form/table/tbody/tr[3]/td/input",
        "issuer": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[12]/td/form/table/tbody/tr[4]/td/input",
        "issued": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[12]/td/form/table/tbody/tr[5]/td/input[1]",
        "expires": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[12]/td/form/table/tbody/tr[6]/td/input[1]",
        "number": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[12]/td/form/table/tbody/tr[7]/td/input",
        "notes": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[12]/td/form/table/tbody/tr[8]/td/textarea",
    },
    "Travel documents": {
        "country": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[14]/td/form/table/tbody/tr[3]/td/input",
        "issuer": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[14]/td/form/table/tbody/tr[4]/td/input",
        "issued": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[14]/td/form/table/tbody/tr[5]/td/input[1]",
        "expires": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[14]/td/form/table/tbody/tr[6]/td/input[1]",
        "number": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[14]/td/form/table/tbody/tr[7]/td/input",
        "notes": "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[14]/td/form/table/tbody/tr[8]/td/textarea",
    }       
}

SAVE_MAPPING = {
        "Migr":
            "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[4]/td/form/table/tbody/tr[12]/td/input",

        "Certificate of Competency":
            "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[6]/td/form/table/tbody/tr[12]/td/input",
        "Endorsements":
            "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[8]/td/form/table/tbody/tr[12]/td/input",
        "Medical":
            "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[10]/td/form/table/tbody/tr[12]/td/input",
        "Training":
            "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[12]/td/form/table/tbody/tr[12]/td/input",
        "Travel documents":
            "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[14]/td/form/table/tbody/tr[12]/td/input"
    }

CERT_ID_LOCATORS = {
    "Migr":
        "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[4]/td/form/table/tbody/tr[2]/td/select",

    "Certificate of Competency":
        "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[6]/td/form/table/tbody/tr[2]/td/select",
    "Endorsements":
        "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[8]/td/form/table/tbody/tr[2]/td/select",
    "Medical":
        "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[10]/td/form/table/tbody/tr[2]/td/select",
    "Training":
        "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[12]/td/form/table/tbody/tr[2]/td/select",
    "Travel documents":
        "xpath=/html/body/table/tbody/tr[4]/td/div[1]/form/table[1]/tbody/tr[14]/td/form/table/tbody/tr[2]/td/select"
}