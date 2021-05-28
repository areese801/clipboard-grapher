"""
A simple utility to graph the contents of data (hopefully) on the clipboard

Originally written Adam Reese on May 28, 2021
areese801@gmail.com
"""

import os
import sys
import json
import pyperclip
import matplotlib.pyplot as plt


def main():
	"""
	# This program does it's
	"""

	"""
	Begin Kludge block.  This can be un-commented during dev to force something to 'be' on the clipboard
	"""
	# # data_file_name_short = 'test_data_1_col.tsv'
	# data_file_name_short = 'test_data.tsv'
	# # data_file_name_short = 'bad_data.tsv'
	# this_dir = os.path.dirname(os.path.realpath(__file__))
	# test_file = os.path.join(this_dir, 'test_data', data_file_name_short)
	# with open(test_file, 'r') as f:
	# 	test_data_str = f.read()
	# 	pyperclip.copy(str(test_data_str))
	# 	print(f"Kludge block put the contents of {test_file} on the the clipboard for dev purposes")

	"""
	End Kludge block
	"""


	# Read the contents of the clipboard into list
	cb_data_str = str(pyperclip.paste())
	print(cb_data_str)
	cb_data = cb_data_str.split('\n')
	prune_empty_rows(some_list=cb_data)

	# Infer the delimiter
	delim = infer_delimiter(some_row=cb_data[0])

	# Do some preliminary validations on the data to determine if it looks like we
	if preliminary_validation(data_rows=cb_data) is False:
		print(f"Preliminary validation failed.  Program will exit.", file=sys.stderr)
		exit(1)

	data_lists = make_data_lists(some_list=cb_data)

	plot_data(data_lists=data_lists)



	pass  # You can put a breakpoint here when you're just getting started


def preliminary_validation(data_rows: list):
	"""
	The main program will pass the str() contents of the clipboard into this function for some preliminary
	validations to try to lazily decide if it's dat or not.  We never really know what might be on the clipboard
	:param data_rows: a list of strings representing a row of data
	:return:
	"""

	if type(data_rows) is not list:
		raise ValueError(f"Expected ")

	data_looks_valid = True

	delim = infer_delimiter(some_row=data_rows[0])

	# Test #1:  Does it have new lines?  If not, it's not data.  Or not data that we would care to chart at least?
	if len(data_rows) <= 1:
		print(f"The data on the clipboard is not interesting enough to graph.  Len = {len(data_rows)}", file=sys.stderr)
		data_looks_valid = False
		return data_looks_valid

	# Test #2:  Are all of the columns (other than maybe the first) numeric?
	data_lists = make_data_lists(some_list=data_rows)
	num_cols = 0
	for dl in data_lists:
		num_cols = max(num_cols, len(dl))

	# If column 1 is the only column, it must be all numeric
	if num_cols == 1:
		row_counter = 0 #Helps be flexible about header being there or not
		for dl in data_lists:
			v = dl[0]
			if looks_like_a_number(some_value=v) is False:
				if row_counter == 0 and len(data_lists) >1 :
					# We were dealing with the header row
					print(f"{v} is not numeric.  Assuming it is the header record")
				else:
					data_looks_valid = False
					print(f"The data only has one column but it is not numeric.", file=sys.stderr)
					break

			row_counter += 1
		return data_looks_valid
	else:
		# If there is more than one column, we'll allow the first one to be a string, but the others must be numeric
		for dl in data_lists:
			for c in dl:
				idx = 0 # So we might be flexible about col 1 not being a number
				v = c[idx]
				if looks_like_a_number(some_value=v) is False and idx > 0:
					data_looks_valid = False
					print(f"The data has more than one column, but a column after the first one is not numeric.", file=sys.stderr)
					break

				idx += 1

			if data_looks_valid is False:
				break
		return data_looks_valid







def prune_empty_rows(some_list: list):
	"""
	Operates on some_list to drop any row that is an empty string
	:param some_list: Some list of things to look at.
	:return:
	"""

	# Fail if some_list is not a list
	if not type(some_list) is list:
		raise ValueError(f"Expected a {type(list)}, but got a {type(some_list)}")

	# Loop over the list backwards and delete any elements that are an empty string
	idx = len(some_list) - 1
	while idx >= 0:
		if str(some_list[idx]).strip() == '':
			del some_list[idx]
		idx -= 1

	# Is there anything left?
	if len(some_list) == 0:
		raise ValueError(f"After all empty strings there is no data left!  "
						 f"It must have all been empty strings all the way down!")


def infer_delimiter(some_row: str):
	"""
	Tests some string value of delim-separated stuff to infer the delimiter
	:param some_row:
	:return:
	"""

	# Try to be flexible if a list was passed in instead of a str
	if type(some_row) is list:
		some_row = some_row[0]

	# Fail if some_row is not a string
	if type(some_row) is not str:
		raise ValueError(f"The type should be {type(str)}.  Got {type(some_row)}")

	# Iterate over the list of candidate delimiters and try to find one
	delimiters = ['\t', ',', ';', ':', '|', ' ']
	found_delim = None

	for d in delimiters:
		l = some_row.split(d)  # Note, we don't hand for escaped chars anywhere in this program.  It's for simple stuff only
		if len(l) > 1:
			found_delim = d
			break

	# if found_delim is None:
	# 	print(f"Could not infer the delimiter for the string '{some_row}'.  Perhaps there is only one column of data.")

	return found_delim


def make_data_lists(some_list: list):
	"""
	Accepts a list of strings, each of which represents a row of data, perhaps delimited by a delimiter
	and coerces that list into a list of lists.  Each 'outer' list is a record, and each 'inner' list contains the
	atomic values after splitting on the delim
	:param some_list:
	:return:
	"""

	data_lists = []
	delim = infer_delimiter(some_list[0])

	for s in some_list:
		new_row = s.split(delim)
		data_lists.append(new_row)

	return data_lists


def looks_like_a_number(some_value):
	"""
	Returns True if some_value might be cast to a float, else False
	:param some_value:
	:return:
	"""

	ret_val = True

	try:
		f = float(some_value)
	except ValueError:
		ret_val = False

	return ret_val

def plot_data(data_lists):
	"""
	Accepts a list of lists (as prepared my make_data_lists function) and plots them on a graph
	:param data_lists:
	:return:
	"""

	# Determine the number of columns in the data
	num_cols = 0
	for row in data_lists:
		num_cols = max(num_cols, len(row))

	# Create the chart
	plt.style.use("seaborn")
	# plt.ion()  #This should be on when invoked to debug in pycharm, off when calling from the cli
	fig = plt.figure()
	plt.legend()

	# Handle for rows that are made up of only one column
	if num_cols == 1:
		values = []
		for row in data_lists:
			val = row[0]
			if looks_like_a_number(some_value=val) is True:  # For skipping headers
				values.append(float(val))

		plt.plot(values, linewidth=1)
	else:
		# We're dealing with more than one column.  We'll assume that the first most column is labels (like dates)

		# TODO:  Need to be more sophisticated about how we treat column 1.  Perhaps apply some hueristics to try
		#  to infer if it represents data or labels.  Consider:  a YYYYMMDD label that looks like a big huge integer
		#  will really throw off the scale of the chart when it paints for other 'smaller' data points

		for i in range(num_cols):
			values = []
			for row in data_lists:
				val = row[i]

				if looks_like_a_number(some_value=val) is True:  # For skipping headers
					values.append(float(val))

			plt.plot(values, linewidth=1)


	# Paint the chart
	plt.show()
	print("Done drawing.")



if __name__ == '__main__':
	main()
