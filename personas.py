PREDEFINED_PERSONAS = {
    "Local Resident": {
        "name": "Lucy",
        "age": 36,
        "gender": "Female",
        "frequency_of_use": "Several times per week",
        "reason_for_visiting": ["Childhood play with friends", "Teenager socializing, hanging out", "Walking dogs", "Playing with her children (older and younger)", "Currently: taking younger children to playground occasionally"],
        "mobility_habits": ["Walking", "playing", "Traffic", "climbing structures", "walking dogs"],
        "accessibility_needs": ["Prefers playgrounds that are contained and provide clear visibility", "Appreciates playground moved away from busy road"],
        "personal_values": ["Nostalgia and emotional attachment to the park ('life-long constant')", "Independence and empowerment (as a child climbing structures)", "Enjoys safe, family-friendly environments"],
        "user_story": "Lucy is a middle-aged mother who grew up near the park and has a deep emotional attachment to it. She spent her childhood and teenage years playing, socializing, and exploring the park, and later brought both her older and younger children there to play. Lucy values the park as a life-long constant, associating it with independence and family memories. She appreciates recent redesign efforts, particularly the safer and more family-friendly playground layout, but she dislikes the park's history of violence and alcohol use. Now living farther away, she visits only occasionally with her young children."
    },
    "Parent with Stroller": {
        "name": "Jocelyn",
        "age": 39,
        "gender": "Female",
        "frequency_of_use": "Daily when living nearby, occasional visits now",
        "reason_for_visiting": ["Playground use for young children", "Meeting other parents", "Community picnics", "Special swing (Blue Swing) for baby and toddler"],
        "mobility_habits": ["Walking with stroller", "Pushing swings", "Sitting on grass", "Using picnic areas"],
        "accessibility_needs": ["Safe play zones for toddlers and young children", "Separation from off-leash dogs", "Clear sight lines to monitor multiple children"],
        "personal_values": ["Community connections", "Child safety", "Convenient, family-oriented design"],
        "user_story": "Jocelyn is a mother of three who used to live near the park and visited daily with her young children. She loved the social atmosphere and the safe playground areas, especially the unique Blue Swing for a baby and toddler to ride together. After moving farther away, she still visits occasionally because her children love the park. She values safety, visibility, and separation from off-leash dogs, and she misses the strong community connections she once had there."
    },
    "Senior Citizen": {
        "name": "Eleanor",
        "age": 72,
        "gender": "Female",
        "frequency_of_use": "Daily",
        "reason_for_visiting": ["Daily walks for exercise", "Reading on park benches", "Meeting other seniors", "Volunteering for community events", "Attending outdoor activities"],
        "mobility_habits": ["Walking with mobility frame", "Using public transit", "Relying on accessible pathways"],
        "accessibility_needs": ["Accessible seating with back support", "Smooth, well-maintained pathways", "Good lighting for safety", "Accessible restroom facilities", "Clear wayfinding signage"],
        "personal_values": ["Community history preservation", "Intergenerational connection", "Accessibility for all ages", "Peaceful, quiet spaces"],
        "user_story": "Eleanor has been a cornerstone of this neighborhood for 35 years, watching it evolve through different phases. As a retired librarian, she values spaces that bring people together and preserve community memory. She uses a walking frame and depends on accessible design to maintain her independence and daily routines. Eleanor appreciates developments that honor the area's history while ensuring that people of all ages and abilities can participate in community life. She's particularly passionate about creating spaces where different generations can interact and learn from each other."
    },
    "Young Professional": {
        "name": "Joe",
        "age": 28,
        "gender": "Male",
        "frequency_of_use": "Weekly",
        "reason_for_visiting": ["Cycling to work", "Meeting friends for outdoor activities", "Using green spaces for relaxation"],
        "mobility_habits": ["Cycling", "Walking", "Public transit", "E-scooter occasionally"],
        "accessibility_needs": ["Secure bike parking", "Well-lit pathways for evening use", "Free WiFi for remote work", "Sustainable transportation options"],
        "personal_values": ["Environmental sustainability", "Smart city innovation", "Affordable housing", "Flexible, informal gathering spaces", "Tolerance for diverse activities"],
        "user_story": "Joe is a musician who grew up visiting the park and sees it as an inclusive space where people can socialize, play music, and enjoy leisure without judgment. He values the acceptance of different groups, including marginalized people, and dislikes selective policing. The park is a creative and social hub in his life."
    },
    "Immigrant": {
        "name": "Oscar",
        "age": 62,
        "gender": "Male",
        "frequency_of_use": "Two to three times a week",
        "reason_for_visiting": ["Playing bocce", "Socializing with friends from Latin American community", "Relaxing outdoors", "Cultural connection"],
        "mobility_habits": ["Walking to park", "Standing while playing bocce", "Occasional cycling"],
        "accessibility_needs": ["Shaded seating near bocce lanes", "Proper drainage on bocce courts", "Access to washrooms"],
        "personal_values": ["Cultural tradition", "Community gathering", "Maintaining connections with people who share his language"],
        "user_story": "Oscar is a Salvadoran-born painter who lives near the park and meets his Latino friends there to play bocce. The park reminds him of childhood games and offers a place to speak his language and share traditions. While he enjoys the space, he's frustrated by litter and poor maintenance, and wishes for better facilities such as shaded seating and drainage. The park is a key social hub for him and his community."
    },
    "Marginal Housing User": {
        "name": "Tom",
        "age": 47,
        "gender": "Male",
        "frequency_of_use": "Multiple times daily",
        "reason_for_visiting": ["Relaxing", "Socializing with friends", "Taking breaks from work"],
        "mobility_habits": ["Walking", "Carrying belongings", "Sitting on benches"],
        "accessibility_needs": ["Safe, non-judgmental gathering spaces", "Areas for coexisting with families and other groups", "Access to public washrooms"],
        "personal_values": ["Laid-back community vibe", "Acceptance of diverse park users", "Coexistence between different groups"],
        "user_story": "Tom has lived in East Vancouver for years, often staying in temporary housing. He spends much of his day at the park relaxing, socializing, and taking breaks from casual work. He values the park's laid-back atmosphere compared to other, more chaotic public spaces, and appreciates being able to coexist with families and dog walkers without major conflict."
    }
}

# Custom persona categories for user story generation
PERSONA_CATEGORIES = {
    "Place": "The specific urban location/area",
    "Age": "Age of the persona",
    "Gender": "Gender identity",
    "Frequency of use": "How often they use/visit the space",
    "Reason for visiting": "Why they come to this place",
    "Mobility habits": "How they move around/travel",
    "Accessibility needs": "Any accessibility requirements",
    "Personal values": "What matters most to them"
}
