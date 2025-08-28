PREDEFINED_PERSONAS = {
    "Local Resident": {
        "name": "Lucy",
        "age": 46,
        "gender": "Female",
        "frequency_of_use": "Several times per month",
        "reason_for_visiting": ["Childhood play with friends", "Playing with her children (older and younger)", "Currently: taking younger children to playground occasionally"],
        "mobility_habits": ["Car", "Bus"],
        "accessibility_needs": ["Prefers playgrounds that are contained and provide clear visibility", "Appreciates playground moved away from busy road"],
        "personal_values": ["Nostalgia and emotional attachment to the park", "Enjoys safe, family-friendly environments"],
        "user_story": "Lucy is a middle-aged mother who grew up near the park and has a deep emotional long-term attachment to it. She spent her childhood and teenage years playing, socializing, and exploring the park, and later brought both her older and younger children there to play. Lucy values the park as a life-long constant, associating it with independence and family memories. She appreciates recent redesign efforts, particularly the safer and more family-friendly playground layout, but she dislikes the park's history of violence and alcohol use. Now living farther away, she visits only occasionally with her young children."
    },
    "Parent with Stroller": {
        "name": "Jocelyn",
        "age": 39,
        "gender": "Female",
        "frequency_of_use": "Daily when living nearby, occasional visits now",
        "reason_for_visiting": ["Playground use for young children", "Meeting other parents", "Special swing for baby and toddler"],
        "mobility_habits": ["Walking with stroller", "Bus"],
        "accessibility_needs": ["Safe play zones for toddlers and young children", "Clear sight lines to monitor multiple children", "separation from off-leash dogs"],
        "personal_values": ["Community connections", "Child safety", "Convenient, family-oriented design"],
        "user_story": "Jocelyn is a mother of three who used to live near the park and visited daily with her young children. She loved the social atmosphere and the safe playground areas, especially the unique swing for a baby or toddler to ride. After moving farther away, she still visits occasionally because her children love the park. She values safety, visibility, and separation from off-leash dogs, and she misses the strong community connections she once had there."
    },
    "Senior Citizen": {
        "name": "Eleanor",
        "age": 72,
        "gender": "Female",
        "frequency_of_use": "Daily",
        "reason_for_visiting": ["Daily walks for exercise", "Reading on park benches", "Meeting other seniors"],
        "mobility_habits": ["Walking", "Bus"],
        "accessibility_needs": ["Accessible seating with back support", "Smooth, well-maintained pathways", "Good lighting for safety", "Accessible restroom facilities"],
        "personal_values": ["Community history preservation", "Intergenerational connection", "Peaceful, quiet spaces"],
        "user_story": "Eleanor has been a cornerstone of this neighborhood for 35 years, watching it evolve through different phases. As a retired librarian, she values spaces that bring people together and preserve community memory. She uses a walking frame and depends on accessible design to maintain her independence and daily routines. Eleanor appreciates developments that honor the area's history while ensuring that people of all ages and abilities can participate in community life."
    },
    "Young Professional": {
        "name": "Joe",
        "age": 28,
        "gender": "Male",
        "frequency_of_use": "Weekly",
        "reason_for_visiting": ["Night-time work"],
        "mobility_habits": ["Cycling", "Late-night bus"],
        "accessibility_needs": ["Secure bike parking", "Well-lit pathways for evening use", "Sustainable transportation options"],
        "personal_values": ["Environmental sustainability", "Night safety", "Reliability"],
        "user_story": "Joe is a musician who ofter plays music in places like bars, theaters, and music halls. Sometimes he needs to reach several places to perform at one night and most of the time he work until very late at night. He often rides bikes to work for flexiable transition. Sometimes he will take the late-night bus. He is also holding the belief of environmental sustainbility. So enjoys riding bikes and public transportation. He hopes the pathways are more well-lit for evening use."
    },
    "Immigrant": {
        "name": "Oscar",
        "age": 38,
        "gender": "Male",
        "frequency_of_use": "Two to three times a week",
        "reason_for_visiting": ["Socializing with friends from Latin American community", "Cultural connection", "Playing bocce"],
        "mobility_habits": ["Walking", "Public transportation"],
        "accessibility_needs": ["Shaded seating near bocce lanes", "Access to washrooms"],
        "personal_values": ["Cultural tradition", "Community gathering", "Affordability"],
        "user_story": "Oscar is a Salvadoran-born painter who lives near the park and meets his Latino friends there to play bocce. The park reminds him of childhood games and offers a place to speak his language and share traditions. While he enjoys the space, he's frustrated by litter and poor maintenance, and wishes for better facilities such as shaded seating and drainage. The park is a key social hub for him and his community."
    },
    "Student Commuter": {
        "name": "Tom",
        "age": 21,
        "gender": "Male",
        "frequency_of_use": "Once or twice per month",
        "reason_for_visiting": [ "Socializing with friends"],
        "mobility_habits": ["Cycling", "Bus", "E-scoter occasinally"],
        "accessibility_needs": ["N/A"],
        "personal_values": ["affordability", "flexibility and informal gathering spaces"],
        "user_story": "Tom has moved to this city from Vancouver, Canada for study. He spent most of his time in the university. Several of his friends live in this area. Once or twice per month, he visits his friends and have parties together. He has high mobility demands since they may explore this area together. He relys on cycling a lot, so he need secure bike parking places. As a student he sometimes prioritises connectivity and low cost, free WiFi for remote work"
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

