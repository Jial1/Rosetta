"""
Retrieves publication data from openAlex
"""
import pandas as pd
import requests
import json
import os

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

	return filtered_works_url

def get_full_publication_data(yourEmail):
	
	cursor = '*'

	select = ",".join((
	'id',
	'doi',
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

	# get the UW filtered works url
	filtered_works_url = get_UW_filtered_works_url(yourEmail)
	"""
	# for testing, just 1 page
	
	url = f'{filtered_works_url}&select={select}&cursor={cursor}'
	page_with_results = requests.get(url).json()

	results = page_with_results['results']
	works.extend(results)
	

	"""
	while cursor:
		# set cursor value and request page from OpenAlex
		url = f'{filtered_works_url}&select={select}&cursor={cursor}'
		

		for i in range(3):
			try:
				print("try times:", i)
				# make the API request
				page_with_results = requests.get(url).json()
				results = page_with_results['results']
				works.extend(results)
				break
			except json.decoder.JSONDecodeError:
				# print a JSONDecodeError message
				print("Failed to reuqest the API call", loop_index, url)
				continue
			except Exception as e:
				# any other errors
				print("An error occurred: {}".format(str(e)))
				break

		else:
			print("Failed after trying 3 times")
		

		# update cursor to meta.next_cursor
		cursor = page_with_results['meta']['next_cursor']
		loop_index += 1
		print(loop_index)


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
	Takes a array 'works' as parameter
	Filters down to works that have at least one authorship outside of UW
	Converts the works data into a Pandas dataframe
	"""
	data = []

	for work in works:
		if work['primary_location'] is not None:
			for key, source in work['primary_location'].items():
				if key == 'source':
					if source:
						if source['display_name']:
							journal_name = source['display_name'] if source else None



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
							'doi_link': work['doi'],
							'journal_name': journal_name,
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


def get_institution_data(df_collab):
	institution_ids = df_collab['institution_id'].dropna().unique()

	endpoint = "institutions"
	size = 50
	loop_index = 0
	institutions = []

	for list_index in range(0, len(institution_ids), size):
		subset = institution_ids[list_index:list_index+size]
		pipe_separated_ids = "|".join(subset)
		r = requests.get(f"https://api.openalex.org/institutions?filter=openalex:{pipe_separated_ids}&per-page={size}")
		results = r.json()['results']
		institutions.extend(results)
		loop_index += 1

	print(f"collected {len(institutions)} institutions using {loop_index} api calls")

	data = []

	for institution in institutions:
		data.append({
			'id': institution['id'],
			'ror': institution['ror'],
			'display_name': institution['display_name'],
			'country_code': institution['country_code'],
			'type': institution['type'],
			'latitude': institution['geo']['latitude'],
			'longitude': institution['geo']['longitude'],
			'city': institution['geo']['city'],
			'region': institution['geo']['region'],
			'country': institution['geo']['country'],
			'image_url': institution['image_url'],
			'image_thumbnail_url': institution['image_thumbnail_url'],
		})

	df_institutions = pd.DataFrame(data)

	return df_institutions


def save_data(df_collab, df_institutions):
	"""
	Saves the data in CSV format
	"""
	if not os.path.isdir('data'):
		os.mkdir('data')

	# Save the publications data
	# Each row represents a publication-author-affiliation
	outpath = './data/uw_publication_collabs_withUS.csv.gz'
	df_collab.to_csv(outpath, index=False)

	outpath = './data/uw_collabs_institutions_withUS.csv.gz'
	df_institutions.to_csv(outpath, index=False)




def main():
	works = get_full_publication_data("xzhu22@uw.edu")

	df_collab = organize_works_data(works)

	df_institutions = get_institution_data(df_collab)

	save_data(df_collab, df_institutions)
	

if __name__ == '__main__':
    main()