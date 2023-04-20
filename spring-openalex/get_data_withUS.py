"""
Retrieves publication data from 
"""

import requests

def get_UW_filtered_works_url(email):
	"""
	Takes a string parameter 'yourEmail' to use the polite pool
	Builts the URL to request a list of UW Works from openAlex API
	"""
	uw_id = "https://ror.org/00cvxb145"

	# specify endpoint
	endpoint = 'works'

	# limit it to the last 20 years
	filters = ",".join((
		f'institutions.ror:{uw_id}',
		'from_publication_date:2003-01-01',
	))

	# put the URL together
	filtered_works_url = f'https://api.openalex.org/{endpoint}?filter={filters}'

	if email:
		filtered_works_url += f"&mailto={email}"

	print(filtered_works_url)

	return filtered_works_url

def get_full_publication_data(yourEmail):
	
	cursor = '*'

	select = ",".join((
	'id',
	'ids',
	'title',
	'display_name',
	'publication_year',
	'publication_date',
	'primary_location',
	'open_access',
	'authorships',
	'cited_by_count',
	'is_retracted',
	'is_paratext',
	'updated_date',
	'created_date',
	))
	# loop through pages
	works = []
	loop_index = 0

	# get the UW filtered works url, make sure to 
	filtered_works_url = get_UW_filtered_works_url(yourEmail)

	while cursor:
		# set cursor value and request page from OpenAlex
		url = f'{filtered_works_url}&select={select}&cursor={cursor}'
		page_with_results = requests.get(url).json()

		results = page_with_results['results']
		works.extend(results)

		# update cursor to meta.next_cursor
		cursor = page_with_results['meta']['next_cursor']
		loop_index += 1

		if loop_index in [5, 10, 20, 50, 100] or loop_index % 500 == 0:
			print(f'{loop_index} api requests made so far')

	print(f'done. made {loop_index} api requests. collected {len(works)} works')

	return works

def outside_uw_collab(institution_ids):
	"""
	Takes institution IDs (grouped by works)
	Returns True if the work has at least one non-UW affiliation
	"""
	if all(institution_ids == 'https://openalex.org/I201448701'):
		return False
	else:
		return True

def international_collab(institution_country_codes):
    """
    Takes institution country codes (grouped by works)
    Returns True if the work has at least one non-US affiliated institution
    """
    if all(institution_country_codes == 'US'):
        return False
    else:
        return True


def organize_works_data(works):
	"""
	Takes a array 'works' as parameter.
	Filters down to works that have at least one authorship outside of UW.
	Converts the works data into a Pandas dataframe.
	"""
	data = []

	for work in works:
		for authorship in work['authorships']:
			if authorship:
				author = authorship['author']
				author_id = author['id'] if author else None
				author_name = author['display_name'] if author else None
				author_position = authorship['author_position']

				for institution in authorship['institutions']:
					if institution:
						institution_id = institution['id']
						institution_name = institution['display_name']
						institution_country_code = institution['country_code']
						data.append({
							'work_id': work['id'],
							'work_title': work['title'],
							'work_display_name': work['display_name'],
							'work_publication_year': work['publication_year'],
							'work_publication_date': work['publication_date'],
							'author_id': author_id,
							'author_name': author_name,
							'author_position': author_position,
							'institution_id': institution_id,
							'institution_name': institution_name,
							'institution_country_code': institution_country_code,
						})
	df = pd.DataFrame(data)


	# filter for outside collaborations

	# label each row to indicate whether the work have at least one authorship outside of UW
	df['is_outside_uw_collab'] = df.groupby('work_id')['institution_id'].transform(outside_uw_collab)

	df_collab = df[df['is_outside_uw_collab']].drop(columns='is_outside_uw_collab')



	# filter for institutions outside of US

	#df_collab['is_international_collab'] = df_collab.groupby('work_id')['institution_country_code'].transform(international_collab)

	return df_collab




def main():
	works = get_full_publication_data("zwang28@uw.edu")

	organize_works_data(works)
	

if __name__ == '__main__':
    main()