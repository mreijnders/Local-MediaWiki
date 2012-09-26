# A Dictionary of commonly used features
dCommonFeatures =\
{
	'Seperator' :
	{
		'name'		: 'Seperator',
		'seq'		: '',
		'mutable'	: False,
		'maycontain': []
	},
	'BioBrick-Prefix' : 
	{
		'name'		: 'BioBrick-Prefix',
		'seq'		: 'GAATTCGCGGCCGCTTCTAGAG',
		'mutable'	: False,
		'maycontain':
		[
			'Forbidden-EcoRI',
			'Forbidden-XbaI',
			'Forbidden-NotI'
		]
	},
	'BioBrick-Suffix' :
	{
		'name'		: 'BioBrick-Suffix',
		'seq'		: 'TACTAGTAGCGGCCGCTGCAG',
		'mutable'	: False,
		'maycontain':
		[
			'Forbidden-SpeI',
			'Forbidden-PstI',
			'Forbidden-NotI'
		]
	},
	'BioBrick-Scar'	:
	{
		'name'		: 'BioBrick-Scar',
		'seq'		: 'TACTAGAG',
		'mutable'	: False,
		'maycontain': []
	}
}