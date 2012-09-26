# A dictionary of sequences that are not allowed
dForbiddenSequences = \
	{
	'Forbidden-EcoRI'	: 'GAATTC',
	'Forbidden-XbaI'	: 'TCTAGA',
	'Forbidden-SpeI'	: 'ACTAGT',
	'Forbidden-PstI'	: 'CTGCAG',
	'Forbidden-NotI'	: 'GCGGCCGC',
	'Avoidable-PvuII'	: 'CAGCTG',
	'Avoidable-XhoI'	: 'CTCGAG',
	'Avoidable-AvrII'	: 'CCTAGG',
	'Avoidable-NheI'	: 'GCTAGC',
	'Avoidable-SapI(1)'	: 'GCTCTTC',
	'Avoidable-SapI(2)'	: 'GAAGAGC',
	'Memory-ScaI'		: 'AGTACT',
	'Zif-E2C'			: 'GGGGCCGGAGCCGCAGTG',
	'Zif-PTF'			: 'ATCGGCGCCGGCGACATC',
	#'General-AluI'		: 'AGCT', # Blocked by EcoBI overlaps
	'General-BamHI'		: 'GGATCC', # Cuts Dam, Dcm & CpG overlaps
	#'General-FseI'		: 'GGCCGGCC', # Some impaired by Dcm and variable by CpG overlaps
	#'General-HindIII'	: 'AAGCTT', # Variable by EcoBI overlaps
	#'General-MluI'		: 'ACGCGT', # Blocked by CpG and variable by EcoBI & EcoKI overlaps
	'General-NdeI'		: 'CATATG', # Cuts EcoBI overlaps
	'ENatRes-EcoKI(1)'	: 'AACGTCG', # Restricts metyhlated dna at this sequence
	'ENatRes-EcoKI(2)'	: 'GCACGTT',
	'ENatMet-Dcm(1)'	: 'CCAGG', # Restricted by MrcA, MrBC & Mrr if unmodified by Dcm
	'ENatMet-Dcm(2)'	: 'CCTGG',
	#'ENatMet-Dam'		: 'GATC', # Restricted by Mrr if unmodified by Dam
	#'ENatMet-EcoKI'	: 'AACNNNNNNGTGC', # Resticted by Mrr if unmodified
	}