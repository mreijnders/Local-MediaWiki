# 2 line fix to allow imports from the parrent folder
import sys
sys.path.append('..')

# Import dictionary of forbidden sequences (see file for more info)
from ForbiddenSequences import dForbiddenSequences as dForbiddenSequences

# Import commonly used functions and generators that can be used to build the specification
from FunctionsAndGenerators import genRandomDNAFunction, getReverseComplement

# Import the specification processor for the DNAConstructor
from DNAConstructor import processCompleteSpecification as verifyAndOptimizeSpecification

# Define complete specification
dCompleteSpec =\
{	'Specification Name'	: 'NdeI-125-PTF-25-ScaI-25-PTFCRC-125-NdeI',
	'Forbidden Sequences'	: dForbiddenSequences,
	'Feature Specification'	:
	[
		{	'name'		: 'PrecedingSeg-20',
			'seq'		: 'TTTATTATTTCGCCCGGCGC',
			'mutable'	: False,
			'maycontain': []
		},
		{	'name'		: 'NdeI',
			'seq'		: 'CATATG',
			'mutable'	: False,
			'maycontain': 
			[
				'General-NdeI'
			]
		},
		{	'name'		: 'DNARand-125',
			'seq'		: genRandomDNAFunction(125),
			'mutable'	: True,
			'maycontain': []
		},
		{	'name'		: 'ZifBindingMotif-PTF',
			'seq'		: 'ATCGGCGCCGGCGACATC',
			'mutable'	: False,
			'maycontain': 
			[
				'Zif-PTF'
			]
		},
		{	'name'		: 'DNARand-25',
			'seq'		: genRandomDNAFunction(25),
			'mutable'	: True,
			'maycontain': []
		},
		{	'name'		: 'Memory-ScaI',
			'seq'		: 'AGTACT',
			'mutable'	: False,
			'maycontain': 
			[
				'Memory-ScaI'
			]
		},
		{	'name'		: 'DNARand-25',
			'seq'		: genRandomDNAFunction(25),
			'mutable'	: True,
			'maycontain': []
		},
		{	'name'		: 'ZifBindingMotif-PTF-RC',
			'seq'		: getReverseComplement('ATCGGCGCCGGCGACATC'),
			'mutable'	: False,
			'maycontain': 
			[
				'Zif-PTF'
			]
		},
		{	'name'		: 'DNARand-125',
			'seq'		: genRandomDNAFunction(125),
			'mutable'	: True,
			'maycontain': []
		},
		{	'name'		: 'NdeI',
			'seq'		: 'CATATG',
			'mutable'	: False,
			'maycontain': 
			[
				'General-NdeI'
			]
		},
		{	'name'		: 'TrailingSeg-20',
			'seq'		: 'TACTAGTAGCGGCCGCTGCA',
			'mutable'	: False,
			'maycontain': 
			[
				'Forbidden-SpeI', 
				'Forbidden-NotI'
			]
		}
	],
	'GC Target Fraction'	: 0.55,
	'GC Optimization Map'	: 
	[
		(20, 40), 
		(40, -40), 
		(-40, -20)
	],
	'Optimization Attempts'	: 10000
}

verifyAndOptimizeSpecification(dCompleteSpec)
