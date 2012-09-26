# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# ====================================================================================================
# ===================================  Personal Stuff (Optional)  ====================================
# ====================================================================================================

# Disable buffering of stdout to make console work propperly in notepad++
class Unbuffered:
	def __init__(self, stream):
		self.stream = stream
	def write(self, data):
		self.stream.write(data)
		self.stream.flush()
	def __getattr__(self, attr):
		return getattr(self.stream, attr)

import sys
sys.stdout=Unbuffered(sys.stdout)

# ====================================================================================================
# =========================================  Module Imports  =========================================
# ====================================================================================================

# Import required standard modules
import random
import re
import math

# Import required custom modules
from FunctionsAndGenerators import getReverseComplement, getGCcontent

# ====================================================================================================
# ============================================  Classes  =============================================
# ====================================================================================================

# Setup a class that can catch stuff thats send to the sdtout (usaly print)
class PrintCatcher:
	def __init__(self):
		self.sContent = str()
	def write(self, sString):
		self.sContent = str().join([self.sContent, sString])

# ====================================================================================================
# ===========================================  Functions  ============================================
# ====================================================================================================

# ========================================  Print Functions  =========================================
# Function that generates a function that either prints or doesnt print (voodoo magic)
def genPrintFunc(bVerbose):
	def printVerbos(*args, **kwargs):
		global print
		if bVerbose:
			print(*args, **kwargs)
	return printVerbos

# Function to prety print a DNA sequence
def prettyPrintDNA(sDNASeq, bVerbose=True, iChunkLenght=100, iAnonSteps=10):
	# Redefine print function to adheal to verbose printing (voodoo magic)
	print = genPrintFunc(bVerbose)
	iAnonStart = 0
	iAnonStop = iChunkLenght
	for iStart in range(0, len(sDNASeq), iChunkLenght):
		print(sDNASeq[iStart:iStart+iChunkLenght])
		for iWhere in range(iAnonStart, iAnonStop if iAnonStop < len(sDNASeq) else len(sDNASeq), iAnonSteps):
			print(str(iWhere)+' '*(iAnonSteps-len(str(iWhere))), end='')
		print()
		iAnonStart += iChunkLenght
		iAnonStop += iChunkLenght	
	
# ========================================  Regex Functions  =========================================		
# Function to compile dictionary of forbidden sequences to dict of regex objects (for speed)
def compileForbiddenSeqs(dForbiddenSeqs):
	# Setup a substiturion list for compound bases
	dCompoundBases = 	{
						'R' : '[GA]',
						'Y' : '[CT]',
						'M' : '[AC]',
						'K' : '[GT]',
						'S' : '[GC]',
						'W' : '[AT]',
						'B' : '[CGT]',
						'D' : '[AGT]',
						'H' : '[ACT]',
						'V' : '[ACG]',
						'N' : '[ACGT]'
						}
	
	dCompiledForbiddenSeqs = dict()
	# Look over all forbidden seq items
	for sKey, sSeq in dForbiddenSeqs.items():
		# Loop that replaces compound bases with regex compatible patterns
		for sCBase, sReSubs in dCompoundBases.items():
			sSeq = sSeq.replace(sCBase, sReSubs)
		
		# Compile the expressions into regular expression objects
		dCompiledForbiddenSeqs[sKey] = re.compile(sSeq)
	
	return dCompiledForbiddenSeqs
	
# Function that verifys DNA wheter it includes any forbidden sequences (supports regular expressions and compound bases)
def checkDNAforSeqs(sDNA, dCompiledPatterns):
	dSeqMatches = dict()
	# Loop over regex paterns and see if they are in the DNA
	for sKey, oRegexSearch in dCompiledPatterns.items():
		lMatches = list()
		# Loop that creates moving regex frame to check for the patter (incidently also includes overlaps)
		for iIndex in range(len(sDNA)):
			oMatch = oRegexSearch.match(sDNA, iIndex)
			if oMatch:
				lMatches.append((oMatch.start(), oMatch.end()))
		
		dSeqMatches[sKey] = lMatches
	
	return dSeqMatches

# ================================  Partial Specification Functions  =================================	
# Function to generate DNA that is compliant with the DNA specification
def genSpecDNA(lDNASpec):
	sDNASeq = str()
	lFeatureMap = list()
	iFeatureStart = 0
	# Generate initial DNA string from spec build a feature map
	for dFeature in lDNASpec:
		if hasattr(dFeature['seq'], '__call__'):
			sDNAfeature = dFeature['seq']()
		else:
			sDNAfeature = dFeature['seq']
		
		sDNASeq += sDNAfeature
		iFeatureEnd = iFeatureStart + len(sDNAfeature)
		lFeatureMap.append((iFeatureStart, iFeatureEnd))
		iFeatureStart = iFeatureEnd
	
	return sDNASeq, lFeatureMap

# Function to reverse the feature map (can be used in conjunction with the reverse complement)
def reverseFeatureMap(lFeatureMap):
	iLenSeq = int()
	# Find lenght of the featuremap
	for iFeatureStart, iFeatureEnd in lFeatureMap:
		if iFeatureEnd > iLenSeq: iLenSeq = iFeatureEnd
	
	
	lRevFeatureMap = list()
	# Loop that recalculates the beginning and ending of the features
	for iFeatureStart, iFeatureEnd in lFeatureMap:
		iRevFeatureStart = iLenSeq - iFeatureEnd
		iRevFeatureEnd = iLenSeq - iFeatureStart
		lRevFeatureMap.append((iRevFeatureStart, iRevFeatureEnd))
	
	#lRevFeatureMap.reverse()
	return lRevFeatureMap

# ======================  Specification Verification and Validation Functions  =======================
# Function to verify DNA to see if its compliant with the DNA specification and forbidden sequences 
def verifyDNASpecCompliance(sDNASeq, lFeatureMap, lDNASpec, dCFSeqs, bVerbose=True):
	# Redefine print function to adheal to verbose printing (voodoo magic)
	print = genPrintFunc(bVerbose)
	
	# Pretty print dna sequence information
	prettyPrintDNA(sDNASeq, bVerbose)
	
	# Check dna for collisions with forbidden sequences
	dCollisions = checkDNAforSeqs(sDNASeq, dCFSeqs)
	
	bValid = True
	bCanPossiblyBeMadeValid = True
	# Check for each collision type if which features are part of that collision
	for sFSeqName, lCollisionMap in dCollisions.items():
		if lCollisionMap:
			bMayCollideWithAllFeatures = True
			bContainsMutableFeature = False
			for iColStart, iColEndBy in lCollisionMap:
				print('Forbidden site %s @[%i:%i] collides with Feature(s): ' % (sFSeqName, iColStart, iColEndBy), end='')
				
				# Loop that loops over the feature map and checks which features are in or shared with the collsion
				for iFeatIndex, (iFeatStart, iFeatEndBy) in enumerate(lFeatureMap):
					# Much simpler condition, check if the collision is outside of the feature and invert that awnser
					if not (iColStart >= iFeatEndBy or iColEndBy <= iFeatStart):
						# Get the feature
						dFeature = lDNASpec[iFeatIndex]

						# Check if feature is allowed
						bAllowed = False
						if sFSeqName in dFeature['maycontain']:
							bAllowed = True
						else:
							bMayCollideWithAllFeatures = False
							bValid = False
						
						# Check if feature is mutable
						bIsMutable = dFeature['mutable']
						if bIsMutable:
							bContainsMutableFeature = True
						
						print('%s%s%s @[%i:%i] ' % (dFeature['name'],
													'*' if bAllowed else '',
													'**' if bIsMutable else '',
													iFeatStart, 
													iFeatEndBy), end='')
						
				print()
			
			if not (bMayCollideWithAllFeatures or bContainsMutableFeature):
				bCanPossiblyBeMadeValid = False
	
	print('* Denotes that detected Fobridden site is allowed to be in this Feature!')
	print('** Denotes that this Feature can possibly be mutated to prevent the collision!')
	return bValid, bCanPossiblyBeMadeValid

# Function to make DNA spec compliant if able
def makeDNASpecCompliant(sDNASeq, lFeatureMap, lDNASpec, dCFSeqs, bVerbose=True, bCheckOnly=False, dInsertIntoAndVerityOtherMaps=None):
	# Redefine print function to adheal to verbose printing (voodoo magic)
	print = genPrintFunc(bVerbose)
	
	# First check DNA
	print('Verifying DNA Sequence:')
	tVerResult = verifyDNASpecCompliance(sDNASeq, lFeatureMap, lDNASpec, dCFSeqs, bVerbose)
	
	# What to do
	if not tVerResult[1]: # If it cannot be mutated to create valid match its invalid and return None
		print('DNA sequence cannot be mutated to create valid sequence! - Returning None')
		return None, None
	elif tVerResult[0]: # DNA seq is valid
		
#		# PLACEHOLDER/ NOT CURRENTLY USED Function to insert this into aditional feature specifications and verify those too
#		def verifyAgainsAditionalMaps(sDNASeq, lFeatureMap, lDNASpec, dInsertIntoAndVerityOtherMaps, dCFSeqs, bVerbose=True):
#			lStaticFeatureMap = list(lDNASpec)
#			# First make a static DNA specification of using the iserted sequence
#			for iIndex, tRegion in enumerate(lFeatureMap):
#				lStaticFeatureMap[iIndex]['seq'] = sDNASeq[tRegion[0]:tRegion[1]]
		
		sDNASeqRevComp = getReverseComplement(sDNASeq)
		lRevFeatureMap = reverseFeatureMap(lFeatureMap)
		print('Verifying DNA Sequence Reverse Complement:')
		tRevCompVerResult = verifyDNASpecCompliance(sDNASeqRevComp, lRevFeatureMap, lDNASpec, dCFSeqs, bVerbose)
		if not tRevCompVerResult[1]: # If the reverse complement cannot be mutated to create valid match its invalid and return None
			print('DNA sequence reverse complement cannot be mutated to create valid sequence! - Returning None')
			return None, None
		elif tRevCompVerResult[0]: # DNA reverse complement is valid
			print('DNA sequence and its reverse complement are bought valid! - Returning Sequence')
			return sDNASeq, lFeatureMap # DNA sequence and its reverse compliment are valid thus return the sequence
	
	# So if it doesnt return anything either the DNA sequence or its reverse complement where invalid but can be mutated to get a valid result
	print('DNA sequence and/or its reverse complement are/is invalid but are bought mutable!', end='')
	if bCheckOnly:
		print(' - Returning None')
		return None, None
	print(' - Mutating Sequence')
	sDNASeq, lFeatureMap = genSpecDNA(lDNASpec) # Thus generate another version of the dna
	sDNASeq, lFeatureMap = makeDNASpecCompliant(sDNASeq, lFeatureMap, lDNASpec, dCFSeqs, bVerbose) # And try to make it compliant agan (gottal love recusion)
	return sDNASeq, lFeatureMap

# ==============================  Specification Optimization Functions  ==============================
# Function that checks CG content in regions
def checkGCInRegions(sSeq, lCGMap):
	dGCResults = dict()
	# Loop that loops over each specified segment
	for iBegin, iEndBy in lCGMap:
		sSegPiece = sSeq[iBegin:iEndBy]
		dGCResults[(iBegin, iEndBy)] = getGCcontent(sSegPiece)
	
	return dGCResults

def makeAndGCOptimiseSpecDNA(lDNASpec, dForbiddenSeqs, lGCMap, fTargetGC, iIterations, bVerbose=True):
	# Redefine print function to adheal to verbose printing (voodoo magic)
	print = genPrintFunc(bVerbose)
	
	# Complile forbidden sequences into regular expression match objects
	dCFSeqs = compileForbiddenSeqs(dForbiddenSeqs)
	
	dBestGCDiffs = dict()
	# Set best GCDiffs to 1
	for tRegion in lGCMap:
		dBestGCDiffs[tRegion] = 1
	
	sBestSequence = str()
	dBestGCRegionResult = dict()
	lBestFeatureMap = list()
	iBestResultAtIteration = int()
	for i in range(iIterations):
		# Build and validate DNA
		sDNASeq, lFeatureMap = genSpecDNA(lDNASpec)
		sValidDNASeq, lValidFeatureMap  = makeDNASpecCompliant(sDNASeq, lFeatureMap, lDNASpec, dCFSeqs, bVerbose=False)

		# Return None if its not possible to make valid DNA
		if not sValidDNASeq:
			makeDNASpecCompliant(sDNASeq, lFeatureMap, lDNASpec, dCFSeqs, bVerbose=True, bCheckOnly=True)
			return None
		
		# Get the GC contents for each specified region
		dGCResults = checkGCInRegions(sValidDNASeq, lGCMap)
		
		dGCDiffs = dict()
		bGCDiffsAreBetterThanBestGCDiffs = True
		# Check wheter all gcdiffs are beter
		for tRegion, fResult in dGCResults.items():
			fDiff = math.fabs(fTargetGC - fResult)
			dGCDiffs[tRegion] = fDiff
			if fDiff > dBestGCDiffs[tRegion]:
				bGCDiffsAreBetterThanBestGCDiffs = False
		
		if bGCDiffsAreBetterThanBestGCDiffs:
			dBestGCDiffs = dGCDiffs
			sBestSequence = sValidDNASeq
			dBestGCRegionResult = dGCResults
			lBestFeatureMap = lValidFeatureMap
			iBestResultAtIteration = i
	
	# Calculate weighted and non-weighted average
	fNonWeightedAvg = float()
	fWeightedAvg = float() 
	for (iRegStart, iRegEndBy), fResult in dBestGCRegionResult.items():
		fNonWeightedAvg += fResult
		fWeightedAvg += fResult*len(sBestSequence[iRegStart:iRegEndBy])
	
	fNonWeightedAvg  /= len(dBestGCRegionResult)
	fWeightedAvg /= len(sBestSequence)
	
	return sBestSequence, (fNonWeightedAvg, fWeightedAvg), dBestGCRegionResult, lBestFeatureMap, iBestResultAtIteration

# ====================================================================================================
# =============================  Complete DNA Specification Processors  ==============================
# ====================================================================================================

# Function that processes a complete DNA specification and generates results accordingly
def processCompleteSpecification(dCompleteSpec):
	# Setup initial variables
	lDNASpecification 	= dCompleteSpec['Feature Specification']
	dForbiddenSeqs 		= dCompleteSpec['Forbidden Sequences']
	lGCMap 				= dCompleteSpec['GC Optimization Map']
	fTargetGC 			= dCompleteSpec['GC Target Fraction']
	iIterations			= dCompleteSpec['Optimization Attempts']
	
	# Print info about the job
	print('='*100)
	print('%s Job Info %s' % ('='*45, '='*45))
	print('='*100)
	
	print('Note: DNA specification name: %s' % dCompleteSpec['Specification Name'])
	print('Note: Type of job: %s' % 'GVVGCO (Gneration, Verification, Validation and GC Optimization)')	
	
	print('Note: Feature map contains %i features:' % len(lDNASpecification))
	for iFeature, dFeature in enumerate(lDNASpecification):
		print('      %i: %s: ' % (iFeature, dFeature['name']) )
		print('            SeqType: %s' % ('Generator' if hasattr(dFeature['seq'], '__call__') else 'Specified'), end='')
		if not hasattr(dFeature['seq'], '__call__'): print(', SeqLenght: %i' % len(dFeature['seq']), end='')
		print(', Mutable: %s' % dFeature['mutable'])
		print('            MayContain:%s' % (' None' if not dFeature['maycontain'] else ''), end='')
		sInfront = ''
		for sMayContain in dFeature['maycontain']:
			print ('%s %s' % (sInfront, sMayContain), end='')
			sInfront = ','
		print()
		
	print('Note: Forbidden sequences:')
	lForbiddenSeqNames = list(dForbiddenSeqs.keys())
	lForbiddenSeqNames.sort()
	for sFSeqName in lForbiddenSeqNames:
		print('      %s: %s' % (sFSeqName, dForbiddenSeqs[sFSeqName]))
	
	print('Note: Target GC contents: %f%%' % (fTargetGC*100))	
	print('Note: Optimize GC contents of the folowing regions(%i):' % (len(lGCMap)))
	for iRegion, (iRegBegin, iRegEndBy) in enumerate(lGCMap):
		if not iRegEndBy: iRegEndBy = 0
		print('      Region %i @[%i:%i]' % (iRegion, iRegBegin, iRegEndBy))
		
	print('Note: Number of optimization attempts: %i' % iIterations)
		
	# Setup some stuff to catch prints that would normaly happen to early (i know its not nice to do it this way :P)
	oStdoutOld = sys.stdout # Store default sdtout pipe
	oPrintCatcher = PrintCatcher() 
	sys.stdout = oPrintCatcher # Start catching print output
	
	# Run the DNA creation, verification and optimization function
	tTemp = makeAndGCOptimiseSpecDNA(lDNASpecification, dForbiddenSeqs, lGCMap, fTargetGC, iIterations, bVerbose=False)
	
	# Restore original stdout (and thus stop catching output from the print function)
	sys.stdout = oStdoutOld 

	# If this was a success than display the results
	if tTemp:
		sBestSequence, fBestAvgGCResult, dBestGCRegionResult, lBestFeatureMap, iBestResultAtIteration = tTemp
		print('='*100)
		print('%s Result - Success! :D %s' % ('='*39, '='*39))
		print('='*100)
		
		print('Note: Best result found at iteration: %i' % iBestResultAtIteration)
		print('Note: Optimised GC contents of the folowing regions(%i):' % (len(dBestGCRegionResult)))
		for (iRegBegin, iRegEndBy), fResult in dBestGCRegionResult.items():
			if not iRegEndBy: iRegEndBy = 0
			print('      GC content @[%i:%i]: %f%%' % (iRegBegin, iRegEndBy, fResult*100))
		print('Note: Non-weighted regional average CG contents:  %f%%' % (fBestAvgGCResult[0]*100))
		print('Note: Weighted regional average CG contents: %f%%' % (fBestAvgGCResult[1]*100))
		
		print('Note: Feature map contains features(%i):' % len(lBestFeatureMap))
		for iFeature, (iRegBegin, iRegEndBy) in enumerate(lBestFeatureMap):
			print('      %i @[%i:%i]: %s (GC: %f%%)' % (iFeature, iRegBegin, iRegEndBy, lDNASpecification[iFeature]['name'], getGCcontent(sBestSequence[iRegBegin:iRegEndBy])))
		
		print('Note: Overall GC contents: %f%%' % getGCcontent(sBestSequence))
		
		print('Note: DNA sequence:')
		prettyPrintDNA(sBestSequence, True)

		print('Note: See final verification procedure for more information (displayed below)')	
		print('%s Reverifying Result %s' % ('='*40, '='*40))
		
		makeDNASpecCompliant(sBestSequence, lBestFeatureMap, lDNASpecification, compileForbiddenSeqs(dForbiddenSeqs), bCheckOnly=True)
		
		print('='*100)

	# Else it was no success so than display why it resulted in a failure	
	else:
		print('='*100)
		print('%s Result - Failure! :( %s' % ('='*39, '='*39))
		print('='*100)
		print('Note: Procces ended in a warning because the DNA could not possibly be made valid!')
		print('Note: See final verification procedure for more information (displayed below)')
		print('%s Reverifying Result %s' % ('='*40, '='*40))
		print(oPrintCatcher.sContent, end='')
		print('='*100)
