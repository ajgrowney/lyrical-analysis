metadata_test = {
    "input": [
        "Kendrick-lamar/To-pimp-a-butterfly",
        "Kendrick-lamar/Good-kid-m-a-a-d-city", 
        "Logic/Under-pressure",
        "Logic/The-incredible-true-story",
    ],
    "output": [
        {"title": "To Pimp a Butterfly", "year": 2015, "id": 120991},
        {"title": "good kid, m.A.A.d city", "year": 2012, "id": 15946},
        {"title": "Under Pressure", "year": 2014, "id": 112067},
        {"title": "The Incredible True Story", "year": 2015, "id": 130526},
    ]
}
songurl_test = {
    "input": [
        "Kendrick-lamar/To-pimp-a-butterfly",
        "Kendrick-lamar/Good-kid-m-a-a-d-city", 
        "Logic/Under-pressure",
        "Logic/The-incredible-true-story",
    ],
    "output": [
        [
            "Kendrick-lamar-wesleys-theory-lyrics",
            "Kendrick-lamar-for-free-interlude-lyrics",
            "Kendrick-lamar-king-kunta-lyrics",
            "Kendrick-lamar-institutionalized-lyrics",
            "Kendrick-lamar-these-walls-lyrics",
            "Kendrick-lamar-u-lyrics",
            "Kendrick-lamar-alright-lyrics",
            "Kendrick-lamar-for-sale-interlude-lyrics",
            "Kendrick-lamar-momma-lyrics",
            "Kendrick-lamar-hood-politics-lyrics",
            "Kendrick-lamar-how-much-a-dollar-cost-lyrics",
            "Kendrick-lamar-complexion-a-zulu-love-lyrics",
            "Kendrick-lamar-the-blacker-the-berry-lyrics",
            "Kendrick-lamar-you-aint-gotta-lie-momma-said-lyrics",
            "Kendrick-lamar-i-album-version-lyrics",
            "Kendrick-lamar-mortal-man-lyrics",
            "Kendrick-lamar-to-pimp-a-butterfly-credits-lyrics",
            "Kendrick-lamar-alright-music-video-lyrics",
            "Screen-genius-god-is-gangsta-short-film-annotated",
            "Kendrick-lamar-to-pimp-a-butterfly-booklet-annotated",
            "Genius-an-exegetical-study-of-to-pimp-a-butterfly-annotated",
            "Kendrick-lamar-to-pimp-a-butterfly-tracklist-album-art-annotated",
            "Kendrick-lamar-i-single-version-lyrics"
        ],
        [
            "Kendrick-lamar-sherane-aka-master-splinters-daughter-lyrics",
            "Kendrick-lamar-bitch-dont-kill-my-vibe-lyrics",
            "Kendrick-lamar-backseat-freestyle-lyrics",
            "Kendrick-lamar-the-art-of-peer-pressure-lyrics",
            "Kendrick-lamar-money-trees-lyrics",
            "Kendrick-lamar-poetic-justice-lyrics",
            "Kendrick-lamar-good-kid-lyrics",
            "Kendrick-lamar-maad-city-lyrics",
            "Kendrick-lamar-swimming-pools-drank-lyrics",
            "Kendrick-lamar-sing-about-me-im-dying-of-thirst-lyrics",
            "Kendrick-lamar-real-lyrics",
            "Kendrick-lamar-compton-lyrics",
            "Kendrick-lamar-good-kid-maad-city-credits-annotated",
            "Kendrick-lamar-good-kid-maad-city-booklet-annotated"
        ],
        [
            "Logic-intro-lyrics",
            "Logic-soul-food-lyrics",
            "Logic-im-gone-lyrics",
            "Logic-gang-related-lyrics",
            "Logic-buried-alive-lyrics", 
            "Logic-bounce-lyrics",
            "Logic-growing-pains-iii-lyrics",
            "Logic-never-enough-lyrics",
            "Logic-metropolis-lyrics",
            "Logic-nikki-lyrics",
            "Logic-under-pressure-lyrics",
            "Logic-till-the-end-lyrics",
            "Logic-driving-ms-daisy-lyrics",
            "Logic-now-lyrics",
            "Logic-alright-lyrics",
            "Logic-under-pressure-credits-lyrics",
            "Logic-under-pressure-album-cover-and-tracklist-annotated"
        ],
        [
            "Logic-contact-lyrics",
            "Logic-fade-away-lyrics",
            "Logic-upgrade-lyrics",
            "Logic-white-people-scene-lyrics",
            "Logic-like-woah-lyrics",
            "Logic-young-jesus-lyrics",
            "Logic-innermission-lyrics",
            "Logic-i-am-the-greatest-lyrics",
            "Logic-the-cube-scene-lyrics",
            "Logic-lord-willin-lyrics",
            "Logic-city-of-stars-lyrics",
            "Logic-stainless-lyrics",
            "Logic-babel-scene-lyrics",
            "Logic-paradise-lyrics",
            "Logic-never-been-lyrics",
            "Logic-run-it-lyrics",
            "Logic-lucidity-scene-lyrics",
            "Logic-the-incredible-true-story-lyrics",
            "Logic-the-incredible-true-story-trailer-lyrics",
            "Logic-the-incredible-true-story-tracklist-album-cover-annotated",
            "Logic-the-incredible-true-story-credits-lyrics"
        ],
    ]
}

albumfeatures_test = {
    "input": [
        "Kendrick-lamar/To-pimp-a-butterfly",
        "Kendrick-lamar/Good-kid-m-a-a-d-city", 
        "Logic/Under-pressure",
        "Logic/The-incredible-true-story",
    ],
    "output": [
        {'verified': {14148: 'Rapsody', 17649: 'James Fauntleroy', 2668: 'Ronald Isley', 1421: 'Kendrick Lamar', 46: 'Snoop Dogg', 177: 'Bilal', 351: 'George Clinton'}, 'unverified': {14481: 'Thundercat', 2434: 'Anna Wise'}},
        {'verified': {1403: 'Jay Rock'}, 'unverified': {130: 'Drake', 123: u'Dr.\xa0Dre', 4637: 'MC Eiht', 2434: 'Anna Wise'}},
        {'verified': {1745: 'Childish Gambino', 492: 'Big Sean'}, 'unverified': {}},
        {'verified': {569307: 'Big Lenbo', 12636: 'Jesse Boykins III'}, 'unverified': {213416: 'Dria', 27710: 'Kevin Randolph', 561494: 'Anna Elyse Palchikoff', 71478: 'Lucy Rose', 561493: 'Steve Blum'}}
    ]
}
songids_test = {
    "input": [
        "Logic/The-incredible-true-story"
    ],
    "output": [
        {
            2312800: "Young Jesus",
            2338721: "I Am the Greatest",
            2313673: "The Incredible True Story [Tracklist + Album Cover]",
            2338720: "Lord Willin'",
            2343638: "Lucidity (Scene)",
            2300278: "The Incredible True Story (Trailer)",
            2327079: "Like Woah",
            2343640: "The Incredible True Story",
            2343628: "Innermission",
            2343629: "The Cube (Scene)",
            2343630: "City of Stars",
            2343632: "Stainless",
            2343633: "Babel (Scene)",
            2343635: "Paradise",
            2343636: "Never Been",
            2343637: "Run It",
            2343414: "Contact",
            2343415: "Fade Away",
            2343416: "Upgrade",
            2343417: "White People (Scene)",
            2374047: "The Incredible True Story [Credits]",
        }
    ]
}
