

# This lists the fields from mentors that should be used to constitute the mapping affinity with mentees, value is weight
FIELDS_USED_MENTORS = {
            "in_order_to_match_you_with_someone_in_a_related_subfield_what_are_your_main_research_areas_selection_1":"Main_Research_Area_1",
            "in_order_to_match_you_with_someone_in_a_related_subfield_what_are_your_main_research_areas_selection_2":"Main_Research_Area_2",
            "what_main_topic_can_you_provide_advice_on_this_will_help_us_with_the_matching_process_please_note_for_some_topics_you_will_be_prompted_for_further_details":"Main_Topic",
            'if_you_can_provide_mentoring_in_a_language_different_from_english_please_specify': 'language',
            'please_specify_what_aspects_of_health_you_can_discuss_check_all_that_apply_11': 'MT-health',
            "please_specify_the_country_location_you_can_discuss_check_all_that_apply_12": "MT-location-career",
            'please_specify_the_career_advancement_topics_you_can_discuss_check_all_that_apply': 'MT-career',
            'are_there_any_other_topics_you_can_advise_on_as_part_of_the_mentor_program': 'Second_Topic',
            'please_specify_the_country_location_you_can_discuss_check_all_that_apply_16': 'ST-location-career',
            'please_specify_the_career_advancement_topics_youre_in_a_position_to_discuss_check_all_that_apply': 'ST-career',
            'please_indicate_the_region_country_for_which_you_can_provide_careers_advice_click_all_that_apply': 'ST-career-location-empty',
            'please_specify_what_aspects_of_health_you_can_discuss_check_all_that_apply_19': 'ST-health',
            'will_you_be_participating_in_the_mentoring_program_virtually_or_onsite_in_rotterdam': 'onsite',
            'if_attending_virtually_what_time_zone_are_you_located_in': 'timezone',
            'any_other_relevant_information_or_questions_youd_like_to_pass_along_to_the_organizers': 'comments',
            }

# This lists the fields from mentees that should be used to constitute the mapping affinity with mentees, value is weight
FIELDS_USED_MENTEES = {
            "in_order_to_match_you_with_someone_in_a_related_subfield_what_are_your_main_research_areas_selection_1":"Main_Research_Area_1",
            "in_order_to_match_you_with_someone_in_a_related_subfield_what_are_your_main_research_areas_selection_2":"Main_Research_Area_2",
            'what_is_the_main_topic_you_would_you_like_to_discuss_with_your_mentor_this_will_help_us_with_the_matching_process_please_note_for_some_topics_you_will_be_prompted_for_further_details': 'Main_Topic',
            'please_specify_what_aspects_of_health_you_wish_to_discuss_check_all_that_apply_9': 'MT-health',
            'please_specify_the_country_location_you_wish_to_discuss_check_all_that_apply_10': 'MT-location-career',
            'please_specify_the_career_advancement_topics_youd_like_to_discuss_check_all_that_apply_11' : 'MT-career',
            'please_indicate_the_region_country_for_which_you_are_currently_seeking_careers_advice' : 'MT-career-location-empty',
            'are_there_any_other_topics_youd_like_to_discuss_as_part_of_the_mentor_program' : 'Second_Topic',
            'please_specify_the_country_location_you_wish_to_discuss_check_all_that_apply_14' : 'ST-location-career',
            'please_specify_the_career_advancement_topics_youd_like_to_discuss_check_all_that_apply_15': 'ST-career',
            'please_indicate_the_region_country_for_which_you_are_currently_seeking_careers_advice_click_all_that_apply': 'ST-career-location-empty',
            'please_specify_what_aspects_of_health_you_wish_to_discuss_check_all_that_apply_17': 'ST-health',
            'will_you_be_participating_in_the_mentoring_program_virtually_or_onsite_in_rotterdam': 'onsite' ,
            'if_attending_virtually_what_time_zone_are_you_located_in': 'timezone',
            'any_other_relevant_information_or_questions_youd_like_to_pass_along_to_the_organizers': 'comments',
            }

# column that is used to give the academia position of mentors / mentees
POSITION_COLUMN = 'status'
# This mapping is used to attribute a 'level' to each position, mentees will necessarily be given a mentor that has
# a higher 'level' than themselves. Change this mapping according to the available/given answers for position
ACADEMIA_LEVELS = {
    "MA student": 2,

    "PhD student": 3,
    "Predoctoral": 3,

    "Postdoc": 4,
    "Research Scientist": 4,
    "Researcher outside of academia": 4,

    "Adjunct/Visiting Professor/Lecturer": 5,
    "Rehab physician" : 5, # strange person !!

    "Assistant Professor": 6,

    "Associate Professor": 7,

    "Full Professor": 8,
}