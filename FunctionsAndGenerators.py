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

# Import required libraries
import random

# ====================================================================================================
# ===================================== Commonly Used Functions ======================================
# ====================================================================================================

# Function that generates random DNA sequence of specified size
def genRandomDNA(iSize):
	return str().join(random.choice('ATGC') for i in range(iSize))

# Function that generates the reverse complement of a DNA sequence
def getReverseComplement(sDNA):
	# Setup a base complements list
	dBaseComplements = 	{
						'A' : 'T',
						'T'	: 'A',
						'G'	: 'C',
						'C'	: 'G',
						'R'	: 'Y',
						'Y'	: 'R',
						'M' : 'K',
						'K' : 'M',
						'B' : 'V',
						'V' : 'B',
						'D' : 'H',
						'H' : 'D'
						}
	
	sComplementDNA = str()
	# Walk backwards over the string and add complements to new string
	for cCodon in reversed(sDNA):
		sComplementDNA += dBaseComplements[cCodon]
	
	return sComplementDNA
	
# Function that calculates the GC content fraction
def getGCcontent(sDNA):
	iGC = sDNA.count('G')+sDNA.count('C')
	#iAT = sDNA.count('A')+sDNA.count('T')
	return iGC / len(sDNA)
	
# ====================================================================================================
# =========================================== Generators =============================================
# ====================================================================================================	

# Generator that returns a function that generates random DNA sequence of specified size
def genRandomDNAFunction(iSize):
	return lambda: genRandomDNA(iSize)
	
	

	
		